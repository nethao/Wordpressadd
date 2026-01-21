import requests
import json

# 测试数据
data = {
    "title": "测试文章标题",
    "content": "这是测试内容",
    "author_token": "test123"
}

try:
    # 发送请求
    response = requests.post("http://localhost:8001/publish", json=data)
    result = response.json()
    
    print("状态码:", response.status_code)
    print("响应结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get("success"):
        print("\n✅ 发布成功！")
    else:
        print("\n❌ 发布失败:", result.get("message"))
        
except Exception as e:
    print("错误:", e)