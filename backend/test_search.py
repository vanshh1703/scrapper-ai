import urllib.request
import json
import urllib.parse

from core.database import SessionLocal
from models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == 'test_debug@test.com').first()
if not user:
    print("Creating user...")
    from core.security import get_password_hash
    user = User(email='test_debug@test.com', hashed_password=get_password_hash('password123'))
    db.add(user)
    db.commit()

url = 'http://127.0.0.1:8000/api/v1/auth/login'
data = {'username': 'test_debug@test.com', 'password': 'password123'}

try:
    req = urllib.request.Request(
        url, 
        data=urllib.parse.urlencode(data).encode('utf-8'), 
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    res = urllib.request.urlopen(req)
    token = json.loads(res.read().decode('utf-8'))['access_token']
    print("TOKEN_OBTAINED")
    
    # Now test search
    search_url = 'http://127.0.0.1:8000/api/v1/products/search?query=iphone+15'
    search_req = urllib.request.Request(
        search_url,
        headers={'Authorization': f'Bearer {token}'}
    )
    search_res = urllib.request.urlopen(search_req)
    print("SEARCH_STATUS:", search_res.getcode())
    print("SEARCH_RESULTS:", search_res.read().decode('utf-8')[:500])
except urllib.error.HTTPError as e:
    print("HTTP_ERROR:", e.code)
    try:
        body = json.loads(e.read().decode('utf-8'))
        print("BODY_DETAIL:\n", body.get("detail", body))
    except:
        pass
except Exception as e:
    print("ERROR:", e)
