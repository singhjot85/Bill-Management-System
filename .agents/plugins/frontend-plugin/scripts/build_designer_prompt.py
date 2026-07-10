import json
from pathlib import Path

def main():
    root = Path(".")
    fe_plugin_dir = root / ".agents/plugins/frontend-plugin"
    
    # Load designer template
    template_path = fe_plugin_dir / "agents/designer.txt"
    template = template_path.read_text(encoding="utf-8")
    
    # Load injections
    conventions_ref = (fe_plugin_dir / "context/conventions_ref.md").read_text(encoding="utf-8")
    token_registry = (fe_plugin_dir / "context/token_registry.json").read_text(encoding="utf-8")
    taste_rules = (root / ".agents/rules/taste_and_animation_rules.md").read_text(encoding="utf-8")
    
    # Load context file: api.ts
    api_ts = (root / "frontend/src/services/api.ts").read_text(encoding="utf-8")
    context_text = f"File: frontend/src/services/api.ts\n```typescript\n{api_ts}\n```"
    
    # Perform injections
    prompt = template
    prompt = prompt.replace("[INJECT: constraints]", "")
    prompt = prompt.replace("[INJECT: conventions]", "")
    prompt = prompt.replace("[INJECT: context/conventions_ref.md]", conventions_ref)
    prompt = prompt.replace("[INJECT: context/token_registry.json]", token_registry)
    prompt = prompt.replace("[INJECT: rules/taste_and_animation_rules.md]", taste_rules)
    
    # Perform variable replacements
    prompt = prompt.replace("{{feature}}", "Login and Authentication Flow Review")
    prompt = prompt.replace("{{feature_type}}", "refactor")
    prompt = prompt.replace("{{completed_stages}}", "[]")
    prompt = prompt.replace("{{pending_stages}}", '["DESIGN_DRAFT", "DESIGN_LINT", "DESIGN_REVIEW", "DESIGN_APPROVED", "CODE_GEN", "CODE_LINT", "CODE_SELF_CHECK", "MANUAL_QA_PENDING"]')
    prompt = prompt.replace("{{current_stage}}", "DESIGN_DRAFT")
    prompt = prompt.replace("{{architect_notes}}", "Enabled TokenAuthentication in REST_FRAMEWORK settings to allow the frontend's token header to be validated. Cleaned up dead AuthViewSet in apps.tenants. Corrected Axios 401 interceptor behavior for public routes.")
    prompt = prompt.replace("{{context}}", context_text)
    prompt = prompt.replace("[INJECT: retry_errors]", "")
    
    # Write to ignored outputs directory
    out_dir = root / ".agents/logs/outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "designer_prompt.txt").write_text(prompt, encoding="utf-8")
    print("Designer prompt built successfully at .agents/logs/outputs/designer_prompt.txt")

if __name__ == "__main__":
    main()
