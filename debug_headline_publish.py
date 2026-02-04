#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
头条发布功能调试脚本
用于测试头条发布功能是否正常工作
"""

import asyncio
import json
import aiohttp
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_headline_publish_direct():
    """直接测试WordPress API的头条发布功能"""
    print("🧪 开始直接测试WordPress API头条发布功能...")
    
    # WordPress API配置
    wp_domain = os.getenv("WP_DOMAIN")
    wp_username = os.getenv("WP_USERNAME") 
    wp_password = os.getenv("WP_APP_PASSWORD")
    
    if not all([wp_domain, wp_username, wp_password]):
        print("❌ WordPress配置不完整，请检查环境变量")
        return
    
    # 构建API URL
    api_url = f"{wp_domain}/wp-json/wp/v2/adv_posts"
    
    # 认证信息
    import base64
    credentials = f"{wp_username}:{wp_password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    # 测试数据
    test_title = f"🧪 头条测试文章 - {int(asyncio.get_event_loop().time())}"
    test_content = "<p>这是一个头条测试文章的内容。</p><p>应该保存为草稿状态，分类ID为16035。</p>"
    
    # 头条文章数据
    headline_data = {
        "title": test_title,
        "content": test_content,
        "status": "draft",
        "categories": [16035],
        "headline_article": True
    }
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
        "User-Agent": "WordPress-Publisher-Debug"
    }
    
    print(f"📡 API URL: {api_url}")
    print(f"📋 发送数据: {json.dumps(headline_data, indent=2, ensure_ascii=False)}")
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            
            async with session.post(
                api_url,
                json=headline_data,
                headers=headers
            ) as response:
                
                response_text = await response.text()
                print(f"📊 响应状态: {response.status}")
                print(f"📄 响应内容: {response_text}")
                
                if response.status == 201:
                    result = await response.json()
                    print(f"✅ 头条文章创建成功!")
                    print(f"   文章ID: {result.get('id')}")
                    print(f"   文章状态: {result.get('status')}")
                    print(f"   分类: {result.get('categories', [])}")
                    print(f"   链接: {result.get('link', 'N/A')}")
                    return result
                else:
                    print(f"❌ 头条文章创建失败: HTTP {response.status}")
                    try:
                        error_data = await response.json()
                        print(f"   错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                    except:
                        print(f"   错误内容: {response_text}")
                    return None
                    
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_python_api():
    """测试Python发布系统的API"""
    print("\n🐍 测试Python发布系统API...")
    
    # 测试数据
    test_data = {
        "title": f"🧪 Python API头条测试 - {int(asyncio.get_event_loop().time())}",
        "content": "<p>通过Python API发布的头条测试文章。</p>",
        "publish_type": "headline"
    }
    
    print(f"📋 发送到Python API的数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        # 这里需要根据您的Python服务地址调整
        python_api_url = "http://localhost:8001/publish"  # 请根据实际情况修改
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                python_api_url,
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                response_text = await response.text()
                print(f"📊 Python API响应状态: {response.status}")
                print(f"📄 Python API响应内容: {response_text}")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Python API调用成功: {result.get('message')}")
                    return result
                else:
                    print(f"❌ Python API调用失败: HTTP {response.status}")
                    return None
                    
    except Exception as e:
        print(f"❌ Python API测试异常: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 开始头条发布功能完整测试...")
    
    # 运行测试
    loop = asyncio.get_event_loop()
    
    # 测试1: 直接WordPress API
    wp_result = loop.run_until_complete(test_headline_publish_direct())
    
    # 测试2: Python发布系统API
    python_result = loop.run_until_complete(test_python_api())
    
    print("\n📋 测试总结:")
    print(f"WordPress API测试: {'✅ 成功' if wp_result else '❌ 失败'}")
    print(f"Python API测试: {'✅ 成功' if python_result else '❌ 失败'}")
    
    if not wp_result and not python_result:
        print("\n🔧 建议检查:")
        print("1. WordPress插件是否正确安装和激活")
        print("2. 环境变量配置是否正确")
        print("3. WordPress API权限是否正常")
        print("4. Python服务是否正在运行")
        print("5. 查看WordPress错误日志")