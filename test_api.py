#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json

def test_publish():
    """测试发布API"""
    
    # 测试数据
    data = {
        "title": "测试文章标题",
        "content": "这是一篇测试文章的内容，用于验证系统功能。",
        "author_token": "test123"
    }
    
    # 转换为JSON
    json_data = json.dumps(data).encode('utf-8')
    
    # 创建请求
    req = urllib.request.Request(
        'http://localhost:8001/publish',
        data=json_data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        # 发送请求
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            print("✅ 请求成功！")
            print("状态码:", response.status)
            print("响应结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            if result.get("success"):
                print("\n🎉 文章发布成功！")
                print(f"📄 文章ID: {result.get('post_id')}")
            else:
                print(f"\n❌ 发布失败: {result.get('message')}")
                
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    print("🧪 测试WordPress软文发布API")
    print("=" * 50)
    test_publish()