#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复HTTP 200空响应问题的专用脚本
使用多种方法测试WordPress连接
"""

import os
import asyncio
import aiohttp
import base64
import ssl
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_different_methods():
    """测试不同的HTTP请求方法"""
    print("🔧 修复HTTP 200空响应问题")
    print("=" * 50)
    
    wp_domain = os.getenv("WP_DOMAIN")
    wp_username = os.getenv("WP_USERNAME")
    wp_app_password = os.getenv("WP_APP_PASSWORD")
    
    print(f"域名: {wp_domain}")
    print(f"用户名: {wp_username}")
    
    # 构建API URL
    domain = wp_domain.replace('https://', '').replace('http://', '')
    api_base = f"https://{domain}/wp-json/wp/v2"
    
    # 准备认证
    credentials = f"{wp_username}:{wp_app_password}"
    encoded_creds = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
    
    # 测试文章数据
    test_post = {
        "title": "HTTP 200修复测试",
        "content": "这是一篇用于修复HTTP 200问题的测试文章",
        "status": "draft"
    }
    
    # 方法1: 标准aiohttp配置
    print("\n🧪 方法1: 标准aiohttp配置")
    await test_method_1(api_base, encoded_creds, test_post)
    
    # 方法2: 禁用SSL验证
    print("\n🧪 方法2: 完全禁用SSL验证")
    await test_method_2(api_base, encoded_creds, test_post)
    
    # 方法3: 自定义SSL上下文
    print("\n🧪 方法3: 自定义SSL上下文")
    await test_method_3(api_base, encoded_creds, test_post)
    
    # 方法4: 强制HTTP/1.1
    print("\n🧪 方法4: 强制HTTP/1.1")
    await test_method_4(api_base, encoded_creds, test_post)

async def test_method_1(api_base, encoded_creds, test_post):
    """方法1: 标准配置"""
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=15)
        
        headers = {
            "Authorization": f"Basic {encoded_creds}",
            "Content-Type": "application/json",
            "User-Agent": "WordPress-Test-Method1"
        }
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            async with session.post(
                f"{api_base}/posts",
                json=test_post,
                headers=headers
            ) as response:
                print(f"   状态码: {response.status}")
                text = await response.text()
                print(f"   响应长度: {len(text)}")
                if text:
                    print(f"   响应预览: {text[:100]}...")
                else:
                    print("   ❌ 响应为空")
                    
    except Exception as e:
        print(f"   ❌ 方法1失败: {e}")

async def test_method_2(api_base, encoded_creds, test_post):
    """方法2: 完全禁用SSL"""
    try:
        connector = aiohttp.TCPConnector(
            ssl=False,
            verify_ssl=False,
            limit=10,
            limit_per_host=5
        )
        
        headers = {
            "Authorization": f"Basic {encoded_creds}",
            "Content-Type": "application/json",
            "User-Agent": "WordPress-Test-Method2",
            "Connection": "close"
        }
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                f"{api_base}/posts",
                json=test_post,
                headers=headers,
                timeout=10
            ) as response:
                print(f"   状态码: {response.status}")
                
                # 尝试不同的读取方法
                try:
                    text = await response.text(encoding='utf-8')
                    print(f"   text()响应长度: {len(text)}")
                    if text:
                        print(f"   响应预览: {text[:100]}...")
                    
                    # 尝试读取原始字节
                    await response.read()
                    
                except Exception as read_error:
                    print(f"   读取错误: {read_error}")
                    
    except Exception as e:
        print(f"   ❌ 方法2失败: {e}")

async def test_method_3(api_base, encoded_creds, test_post):
    """方法3: 自定义SSL上下文"""
    try:
        # 创建不验证SSL的上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        headers = {
            "Authorization": f"Basic {encoded_creds}",
            "Content-Type": "application/json",
            "User-Agent": "WordPress-Test-Method3",
            "Accept": "application/json, text/plain, */*"
        }
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                f"{api_base}/posts",
                json=test_post,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                print(f"   状态码: {response.status}")
                print(f"   响应头: {dict(response.headers)}")
                
                text = await response.text()
                print(f"   响应长度: {len(text)}")
                if text:
                    print(f"   响应预览: {text[:100]}...")
                else:
                    print("   ❌ 响应为空")
                    
    except Exception as e:
        print(f"   ❌ 方法3失败: {e}")

async def test_method_4(api_base, encoded_creds, test_post):
    """方法4: 强制HTTP/1.1"""
    try:
        connector = aiohttp.TCPConnector(
            ssl=False,
            force_close=True,
            enable_cleanup_closed=True
        )
        
        headers = {
            "Authorization": f"Basic {encoded_creds}",
            "Content-Type": "application/json",
            "User-Agent": "WordPress-Test-Method4",
            "Connection": "close",
            "Accept": "application/json"
        }
        
        # 强制使用HTTP/1.1
        async with aiohttp.ClientSession(
            connector=connector,
            version=aiohttp.HttpVersion11
        ) as session:
            async with session.post(
                f"{api_base}/posts",
                json=test_post,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=20)
            ) as response:
                print(f"   状态码: {response.status}")
                print(f"   HTTP版本: {response.version}")
                
                # 分步读取响应
                content_length = response.headers.get('Content-Length', '未知')
                print(f"   Content-Length: {content_length}")
                
                text = await response.text()
                print(f"   实际响应长度: {len(text)}")
                
                if text:
                    print(f"   ✅ 成功获取响应: {text[:100]}...")
                    try:
                        json_data = await response.json()
                        print(f"   ✅ JSON解析成功: {json_data.get('id', 'N/A')}")
                    except:
                        print("   ⚠️ JSON解析失败，但有文本响应")
                else:
                    print("   ❌ 响应仍为空")
                    
    except Exception as e:
        print(f"   ❌ 方法4失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_different_methods())