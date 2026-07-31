from fastapi.testclient import TestClient
from app.main import app
from app.routers.auth import fake_code_store

client = TestClient(app)

# 1. 发送验证码
r = client.post('/api/auth/send-code', json={'phone': '13800138000'})
print('1. send-code:', r.status_code, r.json())
print('   stored code:', fake_code_store.get('13800138000'))

# 2. 用存储的验证码登录
code = fake_code_store.get('13800138000')
r2 = client.post('/api/auth/login', json={'phone': '13800138000', 'code': code})
print('2. login:', r2.status_code)
token = r2.json().get('access_token', '')
print('   token:', token[:20] + '...' if token else 'NONE')

# 3. 创建菜品
headers = {'Authorization': f'Bearer {token}'}
r3 = client.post('/api/dishes', json={'name': '红烧肉', 'description': '经典家常菜'}, headers=headers)
print('3. create dish:', r3.status_code, r3.json())

# 4. 获取菜品列表
r4 = client.get('/api/dishes', headers=headers)
print('4. list dishes:', r4.status_code, r4.json())
