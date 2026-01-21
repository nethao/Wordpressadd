#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress认证修复脚本
测试不同的认证方式和用户权限
"""

import os
import asyncio
import aiohttp
import base64
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_auth_methods():
    """测试不同的认证方式"""
    print("🔧 WordPress认证修复测试")
    print("=" * 50)
    
    wp_domain = os.getenv("WP_DOMAIN")
    wp_username = os.getenv("WP_USERNAME")
    wp_app_password = os.getenv("WP_APP_PASSWORD")
    
    print(f"域名: {wp_domain}")
    print(f"用户名: {wp_username}")
    print(f"应用密码: {wp_app_password}")
    
    # 构建API URL
    domain = wp_domain
    if domain.startswith('http://'):
        domain = domain[7:]
    elif domain.startswith('https://'):
        domain = domain[8:]
    
    api_base = f"https://{domain}/wp-json/wp/v2"
    
    # 测试不同的认证格式
    auth_tests = [
        {
            "name": "标准格式",
            "credentials": f"{wp_username}:{wp_app_password}"
        },
        {
            "name": "去除空格",
            "credentials": f"{wp_username.strip()}:{wp_app_password.strip()}"
        },
        {
            "name": "小写用户名",
            "credentials": f"{wp_username.lower()}:{wp_app_password}"
        }
    ]
    
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False),
        timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        
        for auth_test in auth_tests:
            print(f"\n🧪 测试{auth_test['name']}")
            
            # 编码认证信息
            encoded_creds = base64.b64encode(
                auth_test['credentials'].encode('utf-8')
            ).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {encoded_creds}",
                "Content-Type": "application/json",
                "User-Agent": "WordPress-Auth-Test"
            }
            
            # 测试用户认证
            try:
                async with session.get(
                    f"{api_base}/users/me",
                    headers=headers,
                    ssl=False
                ) as response:
                    print(f"   状态码: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ 认证成功!")
                        print(f"   用户ID: {data.get('id')}")
                        print(f"   用户名: {data.get('name')}")
                        print(f"   角色: {data.get('roles', [])}")
                        return True
                    elif response.status == 401:
                        error_data = await response.json()
                        print(f"   ❌ 认证失败: {error_data.get('message', '未知错误')}")
                    else:
                        print(f"   ⚠️ 其他错误: {response.status}")
                        
            except Exception as e:
                print(f"   ❌ 请求失败: {e}")
        
        # 测试发布权限
        print(f"\n🧪 测试发布权限")
        
        # 使用原始认证信息测试发布
        credentials = f"{wp_username}:{wp_app_password}"
        encoded_creds = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {encoded_creds}",
            "Content-Type": "application/json",
            "User-Agent": "WordPress-Publish-Test"
        }
        
        # 测试发布到自定义端点
        test_post = {
            "title": "认证测试文章",
            "content": "这是一篇用于测试认证的文章",
            "status": "draft"  # 草稿状态，不会真正发布
        }
        
        try:
            async with session.post(
                f"{api_base}/adv_posts",
                headers=headers,
                json=test_post,
                ssl=False
            ) as response:
                print(f"   自定义端点状态码: {response.status}")
                
                if response.status == 201:
                    print(f"   ✅ 自定义端点发布权限正常")
                elif response.status == 401:
                    print(f"   ❌ 自定义端点认证失败")
                elif response.status == 403:
                    print(f"   ❌ 自定义端点权限不足")
                else:
                    error_text = await response.text()
                    print(f"   ⚠️ 自定义端点其他错误: {response.status}")
                    print(f"   错误信息: {error_text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ 自定义端点请求失败: {e}")
        
        # 测试标准端点
        try:
            async with session.post(
                f"{api_base}/posts",
                headers=headers,
                json=test_post,
                ssl=False
            ) as response:
                print(f"   标准端点状态码: {response.status}")
                
                if response.status == 201:
                    print(f"   ✅ 标准端点发布权限正常")
                elif response.status == 401:
                    print(f"   ❌ 标准端点认证失败")
                elif response.status == 403:
                    print(f"   ❌ 标准端点权限不足")
                else:
                    error_text = await response.text()
                    print(f"   ⚠️ 标准端点其他错误: {response.status}")
                    print(f"   错误信息: {error_text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ 标准端点请求失败: {e}")
    
    print("\n" + "=" * 50)
    print("认证测试完成")
    print("\n💡 解决建议:")
    print("1. 检查WordPress用户是否有发布文章的权限")
    print("2. 确认应用密码是否正确生成")
    print("3. 检查WordPress插件是否已激活")
    print("4. 确认用户角色是否为管理员或编辑者")

if __name__ == "__main__":
    asyncio.run(test_auth_methods())