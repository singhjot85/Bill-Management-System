import json
import re
from pathlib import Path

def main():
    root = Path(".")
    output_path = root / ".agents/logs/outputs/designer_output.txt"
    state_path = root / ".agents/plugins/frontend-plugin/plugin_state.json"
    
    text = output_path.read_text(encoding="utf-8")
    match = re.search(r"=== DESIGNER CONTRACT ===(.*?)=== END DESIGNER CONTRACT ===", text, re.DOTALL)
    if not match:
        raise ValueError("Designer contract block not found in output.")
        
    contract_json = json.loads(match.group(1).strip())
    
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["contract"] = contract_json
    
    state_path.write_text(json.dumps(state, indent=4), encoding="utf-8")
    print("Updated plugin_state.json with new contract.")

if __name__ == "__main__":
    main()
