import * as fs from 'fs';
import * as path from 'path';

interface DesignContract {
  wireframe: {
    svg_content: string;
    review_mode: string;
  };
}

interface PluginState {
  feature: string;
  contract: DesignContract | null;
}

function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: npx tsx render_svg.ts <path_to_plugin_state.json>');
    process.exit(1);
  }

  const statePath = path.resolve(args[0]);
  if (!fs.existsSync(statePath)) {
    console.error(`State file not found at: ${statePath}`);
    process.exit(1);
  }

  let state: PluginState;
  try {
    state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  } catch (err: any) {
    console.error(`Failed to parse state file: ${err.message}`);
    process.exit(1);
  }

  if (!state.contract || !state.contract.wireframe || !state.contract.wireframe.svg_content) {
    console.error('No SVG wireframe content found in design contract.');
    process.exit(1);
  }

  const svgContent = state.contract.wireframe.svg_content;
  const pluginDir = path.dirname(statePath);
  const contextDir = path.join(pluginDir, 'context');
  const svgOutputPath = path.join(contextDir, 'wireframe.svg');

  try {
    fs.mkdirSync(contextDir, { recursive: true });
    fs.writeFileSync(svgOutputPath, svgContent, 'utf8');
    
    // Log success
    const result = {
      passed: true,
      svg_file: svgOutputPath,
      message: `SVG successfully rendered and saved to: ${svgOutputPath}`
    };
    console.log(JSON.stringify(result));
    process.exit(0);
  } catch (err: any) {
    const result = {
      passed: false,
      errors: [{ file: 'wireframe.svg', issue: `Failed to write SVG: ${err.message}` }],
      retry_prompt: 'Check permissions and try again.'
    };
    console.log(JSON.stringify(result));
    process.exit(1);
  }
}

main();
