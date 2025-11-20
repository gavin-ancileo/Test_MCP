"""
Import workflow templates into n8n
Reads JSON files from n8n-workflow-templates/ and creates workflows via n8n API
"""

import os
import json
import requests
from pathlib import Path

N8N_URL = os.getenv("N8N_URL", "http://aap-n8n.aap.local:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")

def get_headers():
    headers = {"Content-Type": "application/json"}
    if N8N_API_KEY:
        headers["X-N8N-API-KEY"] = N8N_API_KEY
    return headers

def import_template(file_path: str):
    """Import a single workflow template"""
    print(f"\n📄 Reading template: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        template_data = json.load(f)

    workflow_name = template_data.get("name", "Unnamed Workflow")
    print(f"   Name: {workflow_name}")

    # Check if workflow already exists
    list_url = f"{N8N_URL}/api/v1/workflows"
    response = requests.get(list_url, headers=get_headers(), timeout=30)

    if response.status_code == 200:
        existing_workflows = response.json().get('data', [])
        existing = next((w for w in existing_workflows if w['name'] == workflow_name), None)

        if existing:
            print(f"   ⚠️  Workflow already exists with ID: {existing['id']}")
            print(f"   Skipping import. Delete manually in n8n UI if you want to recreate.")
            return existing['id']

    # Create new workflow
    create_url = f"{N8N_URL}/api/v1/workflows"
    response = requests.post(
        create_url,
        headers=get_headers(),
        json=template_data,
        timeout=30
    )

    if response.status_code in [200, 201]:
        workflow_id = response.json().get('id')
        print(f"   ✅ Successfully created workflow with ID: {workflow_id}")
        return workflow_id
    else:
        print(f"   ❌ Failed to create workflow: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def main():
    print("=" * 60)
    print("🔧 N8N Workflow Template Importer")
    print("=" * 60)
    print(f"N8N URL: {N8N_URL}")
    print(f"API Key configured: {'Yes' if N8N_API_KEY else 'No'}")

    # Find all template files
    templates_dir = Path("n8n-workflow-templates")
    if not templates_dir.exists():
        print(f"\n❌ Templates directory not found: {templates_dir}")
        return

    template_files = list(templates_dir.glob("*-template.json"))

    if not template_files:
        print(f"\n⚠️  No template files found in {templates_dir}")
        return

    print(f"\nFound {len(template_files)} template(s):")
    for f in template_files:
        print(f"  - {f.name}")

    # Import each template
    results = {}
    for template_file in template_files:
        workflow_id = import_template(str(template_file))
        results[template_file.name] = workflow_id

    # Summary
    print("\n" + "=" * 60)
    print("📊 Import Summary")
    print("=" * 60)
    for name, wf_id in results.items():
        status = "✅ Imported" if wf_id else "❌ Failed"
        print(f"{status}: {name} → {wf_id or 'N/A'}")

    print("\n💡 Next Steps:")
    print("1. Open n8n UI and verify workflows are created")
    print("2. Workflows are NOT active by default")
    print("3. When users enable workflows, they will be auto-cloned and activated")
    print()

if __name__ == "__main__":
    main()
