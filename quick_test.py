#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本
"""

import asyncio
import aiohttp
import json

async def test_publish():
    """测试发布功能"""
    
    # 测试数据
    test_data = {
        "title": "测试文章标题",
        "content": "这是一篇测试文章的内容，用于验证系统功能是否正常。",
        "author_token": "test123"  # 使用测试令牌
    }
    
    url = "http://localhost:8001/publish"
    
    async with aiohttp.ClientSession() as session:
        try:
            print("🚀 正在测试发布功能...")
            print(f"📝 测试数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
            
            async with session.post(url, json=test_data) as response:
                result = await response.json()
                
                print(f"\n📊 响应状态码: {response.status}")
                print(f"📋 响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get("success"):
                    print("\n✅ 测试成功！文章发布功能正常")
                    if result.get("post_id"):
                        print(f"📄 文章ID: {result['post_id']}")
                else:
                    print("\n❌ 测试失败")
                    print(f"❗ 失败原因: {result.get('message')}")
                    
        except Exception as e:
            print(f"❌ 请求失败: {e}")

async def test_sensitive_content():
    """测试敏感内容检测"""
    
    test_data = {
        "title": "包含测试敏感词的标题",
        "content": "这篇文章包含测试敏感词，应该被审核系统拦截。",
        "author_token": "test123"
    }
    
    url = "http://localhost:8001/publish"
    
    async with aiohttp.ClientSession() as session:
        try:
            print("\n🔍 正在测试敏感内容检测...")
            
            async with session.post(url, json=test_data) as response:
                result = await response.json()
                
                print(f"📊 响应状态码: {response.status}")
                print(f"📋 审核结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if not result.get("success"):
                    print("\n✅ 敏感内容检测正常！内容被成功拦截")
                else:
                    print("\n⚠️ 敏感内容检测可能有问题")
                    
        except Exception as e:
            print(f"❌ 请求失败: {e}")

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 WordPress软文发布代理 - 快速测试")
    print("=" * 60)
    
    # 1. 测试正常发布
    await test_publish()
    
    # 2. 测试敏感内容检测
    await test_sensitive_content()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("💡 现在您可以访问 http://localhost:8001 使用Web界面")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())