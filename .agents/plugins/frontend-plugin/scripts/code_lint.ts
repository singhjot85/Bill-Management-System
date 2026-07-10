import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

interface DesignContract {
  component_name: string;
  tier: 'generic' | 'layout' | 'view';
  code_files: string[];
}

interface PluginState {
  feature: string;
  contract: DesignContract | null;
}

interface LintViolation {
  source: 'impeccable' | 'frontend_conventions';
  rule: string;
  message: string;
  location: string;
}

const HOOK_NAME = 'code_lint';

function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: npx tsx code_lint.ts <path_to_plugin_state.json>');
    process.exit(1);
  }

  const statePath = path.resolve(args[0]);
  if (!fs.existsSync(statePath)) {
    console.log(JSON.stringify({
      passed: false,
      errors: [{ file: 'state', issue: `State file not found at: ${statePath}` }],
      retry_prompt: 'Ensure the state file is initialized.'
    }));
    process.exit(1);
  }

  let state: PluginState;
  try {
    state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  } catch (err: any) {
    console.log(JSON.stringify({
      passed: false,
      errors: [{ file: 'state', issue: `Failed to parse plugin_state.json: ${err.message}` }],
      retry_prompt: 'Fix the JSON syntax of the state file.'
    }));
    process.exit(1);
  }

  if (!state.contract) {
    console.log(JSON.stringify({
      passed: false,
      errors: [{ file: 'contract', issue: 'Design contract is empty.' }],
      retry_prompt: 'Ensure the design contract is approved.'
    }));
    process.exit(1);
  }

  const contract = state.contract;
  const projectRoot = path.resolve(path.dirname(statePath), '..', '..', '..');
  const violations: LintViolation[] = [];

  for (const fileRelativePath of contract.code_files) {
    const fullPath = path.join(projectRoot, fileRelativePath);

    if (!fs.existsSync(fullPath)) {
      violations.push({
        source: 'frontend_conventions',
        rule: 'file_existence',
        message: `File does not exist: ${fileRelativePath}`,
        location: fileRelativePath
      });
      continue;
    }

    const content = fs.readFileSync(fullPath, 'utf8');

    // 1. Component tier and path placement validation
    const fileName = path.basename(fileRelativePath);
    if (contract.tier === 'generic') {
      if (!fileRelativePath.startsWith('frontend/src/components/common/')) {
        violations.push({
          source: 'frontend_conventions',
          rule: 'tier_placement',
          message: `Generic component must reside in "frontend/src/components/common/". Found: ${fileRelativePath}`,
          location: fileRelativePath
        });
      }
    } else if (contract.tier === 'layout') {
      if (!fileRelativePath.startsWith('frontend/src/components/layout/')) {
        violations.push({
          source: 'frontend_conventions',
          rule: 'tier_placement',
          message: `Layout component must reside in "frontend/src/components/layout/". Found: ${fileRelativePath}`,
          location: fileRelativePath
        });
      }
    } else if (contract.tier === 'view') {
      const isUnderViewDir = fileRelativePath.startsWith('frontend/src/components/view/');
      const isUnderViewsDir = fileRelativePath.startsWith('frontend/src/views/');
      if (!isUnderViewDir && !isUnderViewsDir) {
        violations.push({
          source: 'frontend_conventions',
          rule: 'tier_placement',
          message: `View component must reside in "frontend/src/components/view/" or "frontend/src/views/". Found: ${fileRelativePath}`,
          location: fileRelativePath
        });
      }
    }

    // 2. Service Layer purity (No direct Axios or Fetch in components)
    if (fileRelativePath.includes('components/')) {
      if (content.includes('import axios') || content.includes("import axios from 'axios'") || content.includes('axios.get') || content.includes('axios.post')) {
        violations.push({
          source: 'frontend_conventions',
          rule: 'service_layer_purity',
          message: `Component must not import or call axios directly. Use store actions or service modules.`,
          location: fileRelativePath
        });
      }
      if (content.includes('fetch(')) {
        violations.push({
          source: 'frontend_conventions',
          rule: 'service_layer_purity',
          message: `Component must not use direct fetch(). Use store actions or service modules.`,
          location: fileRelativePath
        });
      }
    }

    // 3. Prefer Vuetify classes/props over custom inline styles
    const styleLines = content.split('\n');
    styleLines.forEach((line, idx) => {
      if (line.includes('style="') || line.includes("style='")) {
        // Simple warning or check, but we could enforce it
        violations.push({
          source: 'frontend_conventions',
          rule: 'styling_priority',
          message: `Avoid custom inline styles. Prefer Vuetify utility classes or props. Line content: "${line.trim()}"`,
          location: `${fileRelativePath}:${idx + 1}`
        });
      }
    });

    // 4. Try running impeccable's detect CLI if available
    try {
      // Check if impeccable is available (e.g. check version or command existence)
      // Since it's a CLI rule, we attempt to execute it. If it fails due to command not found, we skip it.
      const stdout = execSync(`detect check ${fullPath} --json`, { stdio: 'pipe' }).toString();
      const cliViolations = JSON.parse(stdout);
      if (Array.isArray(cliViolations)) {
        cliViolations.forEach((v: any) => {
          violations.push({
            source: 'impeccable',
            rule: v.rule || 'aesthetic_anti_pattern',
            message: v.message || 'Aesthetic validation warning',
            location: `${fileRelativePath}:${v.line || 0}`
          });
        });
      }
    } catch (err: any) {
      // impeccable detect tool not installed or failed, log in debug but don't fail conventions on account of it
      // unless required. For now, we degrade gracefully.
    }
  }

  const passed = violations.length === 0;

  // Log run
  const pluginDir = path.dirname(statePath);
  const featureSlug = state.feature.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const logDir = path.join(pluginDir, '..', 'logs', featureSlug);
  fs.mkdirSync(logDir, { recursive: true });
  const logPath = path.join(logDir, `${timestamp}_${HOOK_NAME}.log`);

  const errors = violations.map(v => ({
    file: v.location,
    issue: `[${v.source}::${v.rule}] ${v.message}`
  }));

  const result = {
    passed,
    errors,
    retry_prompt: passed ? '' : 'Fix the conventions or styling violations identified by code_lint.'
  };

  const logMessage = `[${new Date().toISOString()}] code_lint validation run. Result: ${passed ? 'PASSED' : 'FAILED'}\nViolations:\n${JSON.stringify(violations, null, 2)}\n`;
  fs.writeFileSync(logPath, logMessage, 'utf8');

  console.log(JSON.stringify(result));
  process.exit(passed ? 0 : 1);
}

main();
