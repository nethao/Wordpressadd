#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试客户端脚本
用于测试WordPress软文发布代理程序
"""

import asyncio
import aiohttp
import json

async def test_publish():
    """测试发布接口"""
    
    # 测试数据
    test_data = {
        "title": "测试文章标题",
        "content": "这是一篇测试文章的内容。包含了一些正常的文字，用于测试百度AI审核和WordPress发布功能。",
        "author_token": "token1"  # 请确保这个token在.env中配置
    }
    
    url = "http://localhost:8000/publish"
    
    async with aiohttp.ClientSession() as session:
        try:
            print("正在发送测试请求...")
            print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
            
            async with session.post(url, json=test_data) as response:
                result = await response.json()
                
                print(f"\n响应状态码: {response.status}")
                print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get("success"):
                    print("\n✅ 测试成功！文章已发布到WordPress")
                    if result.get("post_id"):
                        print(f"文章ID: {result['post_id']}")
                else:
                    print("\n❌ 测试失败")
                    print(f"失败原因: {result.get('message')}")
                    
        except Exception as e:
            print(f"❌ 请求失败: {e}")

async def test_health():
    """测试健康检查接口"""
    url = "http://localhost:8000/health"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                result = await response.json()
                print("健康检查结果:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"健康检查失败: {e}")

async def test_sensitive_content():
    """测试敏感内容审核"""
    
    # 包含可能敏感词汇的测试数据
    test_data = {
        "title": "测试敏感内容",
        "content": "这是一个测试，包含一些可能的敏感词汇进行审核测试。",
        "author_token": "token1"
    }
    
    url = "http://localhost:8000/publish"
    
    async with aiohttp.ClientSession() as session:
        try:
            print("\n正在测试敏感内容审核...")
            
            async with session.post(url, json=test_data) as response:
                result = await response.json()
                
                print(f"响应状态码: {response.status}")
                print(f"审核结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
        except Exception as e:
            print(f"敏感内容测试失败: {e}")

async def main():
    """主测试函数"""
    print("=== WordPress软文发布代理测试 ===\n")
    
    # 1. 健康检查
    print("1. 健康检查测试")
    await test_health()
    
    print("\n" + "="*50 + "\n")
    
    # 2. 正常内容发布测试
    print("2. 正常内容发布测试")
    await test_publish()
    
    print("\n" + "="*50 + "\n")
    
    # 3. 敏感内容审核测试
    print("3. 敏感内容审核测试")
    await test_sensitive_content()

if __name__ == "__main__":
    asyncio.run(main())