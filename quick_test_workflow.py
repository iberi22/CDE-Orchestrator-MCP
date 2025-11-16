import json

import cde_rust_core

result = cde_rust_core.validate_workflows_py(".github/workflows")
report = json.loads(result)

print(f"Valid: {report['valid']}")
print(f"Total files: {report['total_files']}")
print(f"Valid files: {report['valid_files']}")
print(f"Summary: {report['summary']}")

if report["issues"]:
    print(f"\nIssues ({len(report['issues'])}):")
    for issue in report["issues"][:5]:
        print(f"  {issue['severity']}: {issue['message']}")
