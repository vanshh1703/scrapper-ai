import urllib.request
import json

url = 'http://127.0.0.1:8000/api/v1/auth/register'
data = {'email': 'test3@test.com', 'password': 'password123'}

try:
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    print("STATUS:", res.getcode())
    print("BODY:", res.read().decode('utf-8'))
except Exception as e:
    print("ERROR:", e)
