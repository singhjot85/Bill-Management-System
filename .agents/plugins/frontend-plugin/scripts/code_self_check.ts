import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';

interface PluginState {
  feature: string;
}

const HOOK_NAME = 'code_self_check';

function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: npx tsx code_self_check.ts <path_to_plugin_state.json>');
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

  const pluginDir = path.dirname(statePath);
  const projectRoot = path.resolve(pluginDir, '..', '..', '..');
  const frontendDir = path.join(projectRoot, 'frontend');

  // We run typescript checking (vue-tsc --noEmit)
  exec('npx vue-tsc --noEmit', { cwd: frontendDir }, (error, stdout, stderr) => {
    const passed = !error;
    const errors: { file: string; issue: string }[] = [];

    if (!passed) {
      const output = stdout || stderr || '';
      // Parse compiler output for readability or report as a block
      errors.push({
        file: 'Compilation / Typecheck',
        issue: output.trim() || 'Typecheck failed with unknown compilation error.'
      });
    }

    // Log run
    const featureSlug = state.feature.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const logDir = path.join(pluginDir, '..', 'logs', featureSlug);
    fs.mkdirSync(logDir, { recursive: true });
    const logPath = path.join(logDir, `${timestamp}_${HOOK_NAME}.log`);

    const result = {
      passed,
      errors,
      retry_prompt: passed ? '' : 'Resolve the TypeScript compiler errors before proceeding.'
    };

    const logMessage = `[${new Date().toISOString()}] code_self_check run. Result: ${passed ? 'PASSED' : 'FAILED'}\nOutput:\n${stdout}\nError:\n${stderr}\n`;
    fs.writeFileSync(logPath, logMessage, 'utf8');

    console.log(JSON.stringify(result));
    process.exit(passed ? 0 : 1);
  });
}

main();
