#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress连接测试脚本
用于验证域名配置和API连接
"""

import os
import asyncio
import aiohttp
import base64
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_wordpress_connection():
    """测试WordPress连接"""
    print("🔍 WordPress连接测试")
    print("=" * 50)
    
    # 获取配置
    wp_domain = os.getenv("WP_DOMAIN")
    wp_username = os.getenv("WP_USERNAME")
    wp_app_password = os.getenv("WP_APP_PASSWORD")
    
    print(f"域名: {wp_domain}")
    print(f"用户名: {wp_username}")
    print(f"应用密码: {'已配置' if wp_app_password else '未配置'}")
    
    if not all([wp_domain, wp_username, wp_app_password]):
        print("❌ 配置信息不完整")
        return False
    
    # 处理域名格式
    domain = wp_domain
    if domain.startswith('http://'):
        domain = domain[7:]
    elif domain.startswith('https://'):
        domain = domain[8:]
    
    # 构建API URL
    if '192.168.' in domain or 'localhost' in domain or domain.startswith('127.'):
        api_base = f"http://{domain}/wp-json/wp/v2"
        print(f"🔗 使用HTTP协议: {api_base}")
    else:
        api_base = f"https://{domain}/wp-json/wp/v2"
        print(f"🔗 使用HTTPS协议: {api_base}")
    
    # 准备认证
    credentials = f"{wp_username}:{wp_app_password}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
        "User-Agent": "WordPress-Connection-Test"
    }
    
    # 测试连接
    test_urls = [
        f"{api_base}/users/me",  # 测试认证
        f"{api_base}/adv_posts", # 测试自定义端点
        f"{api_base}/posts"      # 测试标准端点
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(test_urls):
            endpoint_name = ["用户认证", "自定义端点", "标准端点"][i]
            print(f"\n🧪 测试{endpoint_name}: {url}")
            
            try:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                    ssl=False  # 忽略SSL证书验证（测试用）
                ) as response:
                    print(f"   状态码: {response.status}")
                    
                    if response.status == 200:
                        print(f"   ✅ {endpoint_name}连接成功")
                        if i == 0:  # 用户认证测试
                            data = await response.json()
                            print(f"   用户ID: {data.get('id', 'N/A')}")
                            print(f"   用户名: {data.get('name', 'N/A')}")
                    elif response.status == 401:
                        print(f"   ❌ {endpoint_name}认证失败 - 请检查用户名和应用密码")
                    elif response.status == 404:
                        print(f"   ⚠️ {endpoint_name}不存在 - 可能是插件未激活")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ {endpoint_name}错误: {response.status}")
                        print(f"   错误信息: {error_text[:200]}...")
                        
            except asyncio.TimeoutError:
                print(f"   ❌ {endpoint_name}连接超时")
            except Exception as e:
                print(f"   ❌ {endpoint_name}连接失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    asyncio.run(test_wordpress_connection())