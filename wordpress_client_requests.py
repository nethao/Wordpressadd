#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress客户端 - 使用requests库的备用实现
解决认证问题的专用版本
"""

import os
import base64
import requests
from requests.auth import HTTPBasicAuth
import urllib3
from datetime import datetime
from typing import Dict, Any

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WordPressRequestsClient:
    """WordPress REST API客户端 - 使用requests库"""
    
    def __init__(self):
        # 重新加载环境变量
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        self.wp_domain = os.getenv("WP_DOMAIN")
        self.wp_username = os.getenv("WP_USERNAME")
        self.wp_app_password = os.getenv("WP_APP_PASSWORD")
        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        
        print(f"🔍 环境变量检查:")
        print(f"   WP_DOMAIN: {self.wp_domain}")
        print(f"   WP_USERNAME: {self.wp_username}")
        print(f"   WP_APP_PASSWORD: {self.wp_app_password[:10] if self.wp_app_password else 'None'}...")
        print(f"   TEST_MODE: {self.test_mode}")
        
        if not self.test_mode and not all([self.wp_domain, self.wp_username, self.wp_app_password]):
            raise ValueError(f"WordPress配置信息不完整: domain={bool(self.wp_domain)}, username={bool(self.wp_username)}, password={bool(self.wp_app_password)}")
        
        if not self.test_mode:
            # 处理域名格式
            domain = self.wp_domain
            if domain.startswith('http://'):
                domain = domain[7:]
            elif domain.startswith('https://'):
                domain = domain[8:]
            domain = domain.rstrip('/')
            
            # 构建API基础URL
            if '192.168.' in domain or 'localhost' in domain or domain.startswith('127.'):
                self.api_base = f"http://{domain}/wp-json/wp/v2"
            else:
                self.api_base = f"https://{domain}/wp-json/wp/v2"
    
    def create_post_sync(self, title: str, content: str) -> Dict[str, Any]:
        """同步创建WordPress文章"""
        if self.test_mode:
            return {
                "id": 12345,
                "title": {"rendered": title},
                "content": {"rendered": content},
                "status": "pending",
                "date": datetime.now().isoformat(),
                "link": f"https://test-domain.com/adv_posts/12345"
            }
        
        url = f"{self.api_base}/adv_posts"
        
        # 方法1：使用HTTPBasicAuth
        auth = HTTPBasicAuth(self.wp_username, self.wp_app_password)
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "WordPress-Publisher-V2.1"
        }
        
        post_data = {
            "title": title,
            "content": content,
            "status": "pending",
            "date": datetime.now().isoformat(),
            "author": 1
        }
        
        print(f"🔍 使用requests库测试:")
        print(f"   URL: {url}")
        print(f"   用户名: {self.wp_username}")
        print(f"   密码: {self.wp_app_password[:5]}...")
        
        try:
            # 方法1：HTTPBasicAuth
            response = requests.post(
                url,
                json=post_data,
                headers=headers,
                auth=auth,
                verify=False,  # 本地测试禁用SSL验证
                timeout=30
            )
            
            print(f"📊 方法1响应状态: {response.status_code}")
            print(f"📋 方法1响应内容: {response.text[:300]}...")
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 401:
                # 方法1失败，尝试方法2：手动编码Authorization头
                print("🔄 方法1失败，尝试方法2...")
                return self._try_manual_auth(url, post_data, headers)
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ 方法1失败: {e}")
            # 尝试方法2
            return self._try_manual_auth(url, post_data, headers)
    
    def _try_manual_auth(self, url: str, post_data: dict, headers: dict) -> Dict[str, Any]:
        """方法2：手动编码Authorization头"""
        credentials = f"{self.wp_username}:{self.wp_app_password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
        
        headers_with_auth = headers.copy()
        headers_with_auth["Authorization"] = f"Basic {encoded_credentials}"
        
        print(f"🔄 方法2 - 手动Authorization头:")
        print(f"   认证字符串: {credentials}")
        print(f"   编码后: Basic {encoded_credentials[:30]}...")
        
        try:
            response = requests.post(
                url,
                json=post_data,
                headers=headers_with_auth,
                verify=False,
                timeout=30
            )
            
            print(f"📊 方法2响应状态: {response.status_code}")
            print(f"📋 方法2响应内容: {response.text[:300]}...")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                # 尝试方法3：使用posts端点
                return self._try_posts_endpoint(post_data, headers_with_auth)
                
        except Exception as e:
            print(f"❌ 方法2失败: {e}")
            # 尝试方法3
            return self._try_posts_endpoint(post_data, headers_with_auth)
    
    def _try_posts_endpoint(self, post_data: dict, headers: dict) -> Dict[str, Any]:
        """方法3：尝试标准posts端点"""
        url = f"{self.api_base}/posts"
        
        print(f"🔄 方法3 - 尝试标准posts端点:")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(
                url,
                json=post_data,
                headers=headers,
                verify=False,
                timeout=30
            )
            
            print(f"📊 方法3响应状态: {response.status_code}")
            print(f"📋 方法3响应内容: {response.text[:300]}...")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                raise Exception(f"所有方法都失败了。最后错误: HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ 方法3失败: {e}")
            raise Exception(f"WordPress连接失败，所有认证方法都无效: {str(e)}")

def test_wordpress_connection():
    """测试WordPress连接"""
    print("🧪 测试WordPress连接...")
    
    try:
        client = WordPressRequestsClient()
        result = client.create_post_sync(
            "测试文章 - requests库",
            "<p>这是使用requests库发布的测试文章</p>"
        )
        
        print("✅ WordPress连接成功！")
        print(f"📄 文章ID: {result.get('id')}")
        return True
        
    except Exception as e:
        print(f"❌ WordPress连接失败: {e}")
        return False

if __name__ == "__main__":
    test_wordpress_connection()