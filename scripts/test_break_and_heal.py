import json
import time
import urllib.request

code_to_break = 'def broken():\n    path = "C:\\\\test\\\\file"\n    return path\n    return redundant\n'

req = urllib.request.Request(
    "http://localhost:8740/api/aurum/break-and-heal",
    data=json.dumps({"code": code_to_break}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)
t0 = time.time()
r = urllib.request.urlopen(req)
elapsed = time.time() - t0
res = json.loads(r.read().decode("utf-8"))
print(json.dumps(res, indent=2))
print(f"MEASURED ROUNDTRIP: {elapsed*1000:.2f}ms")

