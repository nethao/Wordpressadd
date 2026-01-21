#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress认证快速修复脚本
"""

import os
import asyncio
import aiohttp
import base64
from dotenv import load_dotenv

load_dotenv()

async def quick_auth_test():
    """快速认证测试"""
    print("🔧 WordPress认证快速修复")
    print("=" * 40)
    
    wp_domain = os.getenv("WP_DOMAIN")
    wp_username = os.getenv("WP_USERNAME") 
    wp_app_password = os.getenv("WP_APP_PASSWORD")
    
    print(f"域名: {wp_domain}")
    print(f"用户名: {wp_username}")
    print(f"应用密码: {wp_app_password}")
    print()
    
    # 构建API URL
    domain = wp_domain.replace('https://', '').replace('http://', '')
    
    # 测试不同的认证格式
    auth_formats = [
        f"{wp_username}:{wp_app_password}",
        f"{wp_username.strip()}:{wp_app_password.strip()}",
        f"{wp_username.lower()}:{wp_app_password}",
    ]
    
    connector = aiohttp.TCPConnector(ssl=False)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        for i, auth_string in enumerate(auth_formats):
            print(f"🧪 测试格式 {i+1}: {auth_string[:20]}...")
            
            encoded = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')
            headers = {
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/json"
            }
            
            try:
                async with session.get(
                    f"https://{domain}/wp-json/wp/v2/users/me",
                    headers=headers,
                    timeout=10
                ) as response:
                    print(f"   状态码: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ 认证成功!")
                        print(f"   用户ID: {data.get('id')}")
                        print(f"   用户名: {data.get('name')}")
                        print(f"   角色: {data.get('roles', [])}")
                        
                        # 测试发布权限
                        await test_publish_permission(session, domain, headers)
                        return
                    else:
                        error_data = await response.json()
                        print(f"   ❌ 失败: {error_data.get('message', '未知错误')}")
                        
            except Exception as e:
                print(f"   ❌ 请求失败: {e}")
    
    print("\n💡 所有认证格式都失败了！")
    print("请检查以下几点：")
    print("1. WordPress用户名是否正确")
    print("2. 应用密码是否正确生成")
    print("3. 用户是否有足够权限")
    print("4. WordPress是否启用了应用密码功能")

async def test_publish_permission(session, domain, headers):
    """测试发布权限"""
    print("\n🧪 测试发布权限...")
    
    test_post = {
        "title": "权限测试文章",
        "content": "这是一篇测试文章",
        "status": "draft"  # 草稿状态
    }
    
    try:
        async with session.post(
            f"https://{domain}/wp-json/wp/v2/posts",
            headers=headers,
            json=test_post,
            timeout=10
        ) as response:
            print(f"   发布测试状态码: {response.status}")
            
            if response.status == 201:
                result = await response.json()
                print(f"   ✅ 发布权限正常! 文章ID: {result.get('id')}")
            else:
                error_data = await response.json()
                print(f"   ❌ 发布失败: {error_data.get('message', '未知错误')}")
                
    except Exception as e:
        print(f"   ❌ 发布测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(quick_auth_test())