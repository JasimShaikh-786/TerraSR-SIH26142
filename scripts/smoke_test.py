"""Offline endpoint smoke test. Start the backend first."""
import json, urllib.request
BASE = "http://127.0.0.1:8000/api"
def call(path, body=None):
    req=urllib.request.Request(BASE+path, data=json.dumps(body or {}).encode() if body is not None else None, headers={"Content-Type":"application/json"}, method="POST" if body is not None else "GET")
    return json.loads(urllib.request.urlopen(req, timeout=15).read())
assert call("/health")["status"] == "ok"
for endpoint in ["/scenes/search","/scenes/select","/scenes/preview","/preprocess","/sr/preview","/validation","/uncertainty","/agriculture","/urban","/disaster","/change-detection","/nemotron/analyze","/report"]:
    assert call(endpoint,{"scene_id":"urban","prompt":"Analyze this scene"})
    print("PASS", endpoint)
print("Offline judge-prototype smoke test passed.")
