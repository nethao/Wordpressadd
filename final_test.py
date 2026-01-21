import json
import urllib.request

print("测试开始...")

# 测试数据
data = {"title": "测试", "content": "内容", "author_token": "test123"}
json_str = json.dumps(data)
print(f"发送数据: {json_str}")

# 发送请求
req = urllib.request.Request(
    "http://localhost:8001/publish",
    data=json_str.encode(),
    headers={"Content-Type": "application/json"}
)

try:
    resp = urllib.request.urlopen(req)
    result = resp.read().decode()
    print(f"响应: {result}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()