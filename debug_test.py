#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试测试脚本
"""

import urllib.request
import urllib.error
import json
import sys

def test_health():
    """测试健康检查接口"""
    try:
        print("🔍 测试健康检查接口...")
        response = urllib.request.urlopen('http://localhost:8001/health')
        data = response.read().decode()
        print(f"✅ 健康检查成功: {data}")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_publish():
    """测试发布接口"""
    try:
        print("\n📝 测试发布接口...")
        
        # 准备数据
        data = {
            "title": "测试文章标题",
            "content": "这是测试内容",
            "author_token": "test123"
        }
        
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        print(f"📤 发送数据: {json.dumps(data, ensure_ascii=False)}")
        
        # 创建请求
        req = urllib.request.Request(
            'http://localhost:8001/publish',
            data=json_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            method='POST'
        )
        
        # 发送请求
        print("🚀 发送POST请求...")
        response = urllib.request.urlopen(req, timeout=10)
        
        # 读取响应
        result_data = response.read().decode('utf-8')
        result = json.loads(result_data)
        
        print(f"📊 响应状态: {response.status}")
        print(f"📋 响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get("success"):
            print("✅ 发布测试成功！")
        else:
            print(f"⚠️ 发布失败: {result.get('message')}")
            
        return True
        
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP错误: {e.code} - {e.reason}")
        try:
            error_data = e.read().decode('utf-8')
            print(f"错误详情: {error_data}")
        except:
            pass
        return False
        
    except urllib.error.URLError as e:
        print(f"❌ URL错误: {e.reason}")
        return False
        
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_invalid_token():
    """测试无效令牌"""
    try:
        print("\n🔒 测试无效令牌...")
        
        data = {
            "title": "测试文章",
            "content": "测试内容",
            "author_token": "invalid_token"
        }
        
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            'http://localhost:8001/publish',
            data=json_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        if not result.get("success"):
            print("✅ 令牌验证正常工作")
        else:
            print("⚠️ 令牌验证可能有问题")
            
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("✅ 令牌验证正常工作（返回401）")
        else:
            print(f"⚠️ 意外的HTTP错误: {e.code}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主测试函数"""
    print("🧪 WordPress软文发布代理 - 调试测试")
    print("=" * 60)
    
    # 1. 测试健康检查
    if not test_health():
        print("❌ 服务器未运行或无法访问")
        sys.exit(1)
    
    # 2. 测试发布功能
    test_publish()
    
    # 3. 测试令牌验证
    test_invalid_token()
    
    print("\n" + "=" * 60)
    print("🎯 测试完成！")
    print("💡 如果发布成功，您可以访问 http://localhost:8001 使用Web界面")

if __name__ == "__main__":
    main()