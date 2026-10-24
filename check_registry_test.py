from checks_registry import get_checks
checks = get_checks()
print("Total checks:", len(checks))
print("Total max points:", sum(c["max_points"] for c in checks))
for i, c in enumerate(checks, 1):
    print(f"  {i:2}. {c['id']:22} | {c['tier']:12} | {c['source']:7} | {c['max_points']}pts")
