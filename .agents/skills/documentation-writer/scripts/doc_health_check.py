import re
import sys
from pathlib import Path

# Configuration
DOCS_ROOT = Path("docs")
APPS_ROOT = Path("backend/apps")
CONFIG_ROOT = Path("backend/config")
UTILS_ROOT = Path("backend/utils")
TESTS_ROOT = Path("backend/tests")

REQUIRED_SECTIONS = [
    "## Purpose",
    "## Quick Start",
    "## Key Concepts",
    "## Configuration",
    "## Testing",
    "## Related Documentation"
]

FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---", re.DOTALL | re.MULTILINE)

def check_file_health(file_path):
    issues = []
    content = file_path.read_text()
    lines = content.splitlines()

    # 1. Line count check
    if len(lines) > 500:
        issues.append(f"File too long: {len(lines)} lines (max 500)")

    # 2. Frontmatter check
    if not FRONTMATTER_PATTERN.match(content):
        issues.append("Missing or malformed YAML frontmatter")

    # 3. Required sections (for app READMEs)
    if "backend/apps" in str(file_path) and "Readme.md" in str(file_path):
        for section in REQUIRED_SECTIONS:
            if section not in content:
                issues.append(f"Missing required section: {section}")

    # 4. Broken link check (simplified)
    links = re.findall(r"\[.*?\]\((.*?)\)", content)
    for link in links:
        if link.startswith("http") or link.startswith("#"):
            continue
        
        # Resolve relative link
        link_path = (file_path.parent / link).resolve()
        if not link_path.exists():
            issues.append(f"Broken link: {link}")

    return issues

def main():
    all_issues = {}
    
    # Files to check
    docs_to_check = list(DOCS_ROOT.rglob("*.md"))
    readme_to_check = [
        *APPS_ROOT.rglob("Readme.md"),
        *APPS_ROOT.rglob("README.md"),
        CONFIG_ROOT / "Readme.md",
        UTILS_ROOT / "Readme.md",
        TESTS_ROOT / "Readme.md"
    ]

    for file_path in docs_to_check + readme_to_check:
        if not file_path.exists():
            continue
        issues = check_file_health(file_path)
        if issues:
            all_issues[str(file_path)] = issues

    if all_issues:
        print("Documentation Health Check Failed!")
        for file, issues in all_issues.items():
            print(f"\n{file}:")
            for issue in issues:
                print(f"  - {issue}")
        sys.exit(1)
    else:
        print("Documentation Health Check Passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
