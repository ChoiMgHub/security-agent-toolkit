from rbac import check_permission

REQUESTS = [
    ("seoyeon", "SALES", "QUERY"),
    ("seoyeon", "SETTLE", "QUERY"),
    ("junho", "SETTLE", "QUERY"),
    ("junho", "SALES", "CHANGE"),
    ("dami", "SALES", "QUERY"),
    ("minsu", "SALES", "QUERY"),
    ("gaeun", "ACCOUNT", "CHANGE"),
    ("batch-night", "SETTLE", "QUERY"),
    ("tester", "SALES", "QUERY"),
]

for user, resource, action in REQUESTS:
    ok, reason = check_permission(user, resource, action)
    print(user, resource, action, "->", ok, reason)
