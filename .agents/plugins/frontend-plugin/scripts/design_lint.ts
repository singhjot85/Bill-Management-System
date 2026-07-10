import * as fs from 'fs';
import * as path from 'path';

interface TokenRegistry {
  [category: string]: string[];
}

interface DesignContract {
  component_name: string;
  tier: string;
  vuetify_components: string[];
  design_tokens: { [key: string]: string };
  states: string[];
  animation_spec: string;
  wireframe: {
    svg_content: string;
    review_mode: string;
  };
  review: {
    status: string;
    iteration: number;
    notes: string;
  };
  code_files: string[];
}

interface PluginState {
  feature: string;
  contract: DesignContract | null;
}

const HOOK_NAME = 'design_lint';

function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: npx tsx design_lint.ts <path_to_plugin_state.json>');
    process.exit(1);
  }

  const statePath = path.resolve(args[0]);
  if (!fs.existsSync(statePath)) {
    console.log(JSON.stringify({
      passed: false,
      errors: [{ file: 'state', issue: `State file not found at: ${statePath}` }],
      retry_prompt: 'Ensure the orchestrator initialized the state file.'
    }));
    process.exit(1);
  }

  // Load state
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

  const errors: { file: string; issue: string }[] = [];

  if (!state.contract) {
    errors.push({ file: 'contract', issue: 'Design contract is empty/null.' });
    console.log(JSON.stringify({
      passed: false,
      errors,
      retry_prompt: 'Please request the Designer to generate the design contract.'
    }));
    process.exit(1);
  }

  const contract = state.contract;

  // 1. Component name validation (PascalCase)
  const nameRegex = /^[A-Z][a-zA-Z0-9]*$/;
  if (!nameRegex.test(contract.component_name)) {
    errors.push({
      file: 'contract.component_name',
      issue: `Component name "${contract.component_name}" must be in PascalCase.`
    });
  }

  // 2. Tier validation
  const validTiers = ['generic', 'layout', 'view'];
  if (!validTiers.includes(contract.tier)) {
    errors.push({
      file: 'contract.tier',
      issue: `Component tier "${contract.tier}" is invalid. Must be one of: ${validTiers.join(', ')}.`
    });
  }

  // 3. Design token validation
  const pluginDir = path.dirname(statePath);
  const tokenRegistryPath = path.join(pluginDir, 'context', 'token_registry.json');
  let allowedTokens: string[] = [];

  if (fs.existsSync(tokenRegistryPath)) {
    try {
      const tokenRegistry: TokenRegistry = JSON.parse(fs.readFileSync(tokenRegistryPath, 'utf8'));
      allowedTokens = Object.values(tokenRegistry).flat();
    } catch (err: any) {
      errors.push({
        file: 'token_registry.json',
        issue: `Failed to parse token registry: ${err.message}`
      });
    }
  } else {
    errors.push({
      file: 'token_registry.json',
      issue: 'Token registry file is missing from context.'
    });
  }

  if (allowedTokens.length > 0 && contract.design_tokens) {
    for (const [key, val] of Object.entries(contract.design_tokens)) {
      if (!allowedTokens.includes(val)) {
        errors.push({
          file: 'contract.design_tokens',
          issue: `Token "${val}" used for "${key}" is not registered in token_registry.json.`
        });
      }
    }
  }

  // 4. SVG wireframe validation
  const svg = contract.wireframe?.svg_content || '';
  if (!svg.trim().startsWith('<svg') || !svg.trim().endsWith('</svg>')) {
    errors.push({
      file: 'contract.wireframe.svg_content',
      issue: 'SVG wireframe content must be valid SVG wrapping tags (start with <svg and end with </svg>).'
    });
  }

  // 5. Code file path validation
  if (!contract.code_files || contract.code_files.length === 0) {
    errors.push({
      file: 'contract.code_files',
      issue: 'Design contract must specify at least one target code file in code_files.'
    });
  } else {
    for (const file of contract.code_files) {
      if (!file.startsWith('frontend/src/')) {
        errors.push({
          file: 'contract.code_files',
          issue: `Target path "${file}" must reside inside "frontend/src/".`
        });
      }
    }
  }

  // Log hook execution
  const featureSlug = state.feature.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const logDir = path.join(pluginDir, '..', 'logs', featureSlug);
  fs.mkdirSync(logDir, { recursive: true });
  const logPath = path.join(logDir, `${timestamp}_${HOOK_NAME}.log`);

  const passed = errors.length === 0;
  const result = {
    passed,
    errors,
    retry_prompt: passed ? '' : 'Please revise the design contract based on the design_lint validation errors.'
  };

  const logMessage = `[${new Date().toISOString()}] design_lint validation run. Result: ${passed ? 'PASSED' : 'FAILED'}\nErrors:\n${JSON.stringify(errors, null, 2)}\n`;
  fs.writeFileSync(logPath, logMessage, 'utf8');

  console.log(JSON.stringify(result));
  process.exit(passed ? 0 : 1);
}

main();
