import urllib.request
import json

url = 'http://127.0.0.1:8000/api/v1/auth/register'
data = {'email': 'test_debug@test.com', 'password': 'password123'}

try:
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    print("SUCCESS:", res.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP_ERROR:", e.code)
    print("BODY:", e.read().decode('utf-8'))
except Exception as e:
    print("OTHER ERROR:", e)
