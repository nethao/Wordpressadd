#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress软文发布中间件 V2.2 测试脚本
测试多角色登录系统和所有功能
"""

import requests
import json
import time
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8001"
TEST_ADMIN_USER = "admin"
TEST_ADMIN_PASS = "admin123456"
TEST_OUTSOURCE_USER = "outsource"
TEST_OUTSOURCE_PASS = "outsource123456"

class TestSession:
    """测试会话管理器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # 本地测试环境
        
    def login(self, username, password):
        """用户登录"""
        print(f"🔐 测试登录: {username}")
        
        response = self.session.post(f"{BASE_URL}/login", data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print(f"✅ 登录成功: {result.get('message')}")
                print(f"   角色: {result.get('role')}")
                print(f"   重定向: {result.get('redirect_url')}")
                return True
            else:
                print(f"❌ 登录失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 登录请求失败: HTTP {response.status_code}")
            return False
    
    def logout(self):
        """用户登出"""
        print("🚪 测试登出")
        
        response = self.session.post(f"{BASE_URL}/logout")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 登出成功: {result.get('message')}")
            return True
        else:
            print(f"❌ 登出失败: HTTP {response.status_code}")
            return False
    
    def get_user_info(self):
        """获取用户信息"""
        print("👤 测试获取用户信息")
        
        response = self.session.get(f"{BASE_URL}/api/user")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                user = result.get("user", {})
                print(f"✅ 用户信息获取成功:")
                print(f"   用户名: {user.get('username')}")
                print(f"   角色: {user.get('role')}")
                print(f"   登录时间: {user.get('login_time')}")
                return user
            else:
                print(f"❌ 用户信息获取失败: {result.get('message')}")
                return None
        elif response.status_code == 401:
            print("❌ 未登录或会话已过期")
            return None
        else:
            print(f"❌ 用户信息请求失败: HTTP {response.status_code}")
            return None
    
    def test_publish(self, title="测试文章", content="这是一篇测试文章内容"):
        """测试文章发布"""
        print(f"📝 测试文章发布: {title}")
        
        response = self.session.post(f"{BASE_URL}/publish", json={
            "title": title,
            "content": content
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print(f"✅ 文章发布成功:")
                print(f"   文章ID: {result.get('post_id')}")
                print(f"   消息: {result.get('message')}")
                return True
            else:
                print(f"❌ 文章发布失败: {result.get('message')}")
                if result.get("violations"):
                    print("   违规详情:")
                    for violation in result.get("violations", []):
                        print(f"     - {violation}")
                return False
        elif response.status_code == 401:
            print("❌ 未登录或会话已过期")
            return False
        else:
            print(f"❌ 文章发布请求失败: HTTP {response.status_code}")
            return False
    
    def test_config_access(self):
        """测试配置访问"""
        print("⚙️ 测试配置访问")
        
        response = self.session.get(f"{BASE_URL}/config")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ 配置访问成功")
                config = result.get("config", {})
                print(f"   WordPress域名: {config.get('wp_domain')}")
                print(f"   测试模式: {config.get('test_mode')}")
                return True
            else:
                print(f"❌ 配置访问失败: {result.get('message')}")
                return False
        elif response.status_code == 401:
            print("❌ 未登录或会话已过期")
            return False
        elif response.status_code == 403:
            print("❌ 权限不足，无法访问配置")
            return False
        else:
            print(f"❌ 配置访问请求失败: HTTP {response.status_code}")
            return False
    
    def test_admin_page_access(self):
        """测试管理后台页面访问"""
        print("🏠 测试管理后台页面访问")
        
        response = self.session.get(f"{BASE_URL}/admin")
        
        if response.status_code == 200:
            print("✅ 管理后台页面访问成功")
            return True
        elif response.status_code == 302:
            print("❌ 被重定向，可能权限不足")
            return False
        elif response.status_code == 401:
            print("❌ 未登录")
            return False
        elif response.status_code == 403:
            print("❌ 权限不足")
            return False
        else:
            print(f"❌ 管理后台访问失败: HTTP {response.status_code}")
            return False

def test_health_check():
    """测试健康检查"""
    print("🏥 测试健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/health", verify=False)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 健康检查成功:")
            print(f"   服务状态: {result.get('status')}")
            print(f"   版本: {result.get('version')}")
            print(f"   活跃会话: {result.get('active_sessions', 0)}")
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_unauthorized_access():
    """测试未授权访问"""
    print("🚫 测试未授权访问")
    
    # 测试未登录访问受保护的页面
    try:
        response = requests.get(f"{BASE_URL}/", verify=False, allow_redirects=False)
        
        if response.status_code == 302:
            print("✅ 未登录用户被正确重定向到登录页")
            return True
        elif response.status_code == 401:
            print("✅ 未登录用户收到401错误")
            return True
        else:
            print(f"❌ 未登录用户访问异常: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 未授权访问测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("WordPress软文发布中间件 V2.2 功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试地址: {BASE_URL}")
    print()
    
    # 1. 健康检查测试
    print("1️⃣ 基础功能测试")
    print("-" * 30)
    health_ok = test_health_check()
    unauthorized_ok = test_unauthorized_access()
    print()
    
    # 2. 管理员登录测试
    print("2️⃣ 管理员功能测试")
    print("-" * 30)
    admin_session = TestSession()
    
    admin_login_ok = admin_session.login(TEST_ADMIN_USER, TEST_ADMIN_PASS)
    if admin_login_ok:
        admin_user_info = admin_session.get_user_info()
        admin_publish_ok = admin_session.test_publish("管理员测试文章", "这是管理员发布的测试文章")
        admin_config_ok = admin_session.test_config_access()
        admin_page_ok = admin_session.test_admin_page_access()
        admin_logout_ok = admin_session.logout()
    else:
        admin_user_info = None
        admin_publish_ok = False
        admin_config_ok = False
        admin_page_ok = False
        admin_logout_ok = False
    print()
    
    # 3. 外包人员登录测试
    print("3️⃣ 外包人员功能测试")
    print("-" * 30)
    outsource_session = TestSession()
    
    outsource_login_ok = outsource_session.login(TEST_OUTSOURCE_USER, TEST_OUTSOURCE_PASS)
    if outsource_login_ok:
        outsource_user_info = outsource_session.get_user_info()
        outsource_publish_ok = outsource_session.test_publish("外包测试文章", "这是外包人员发布的测试文章")
        outsource_config_ok = outsource_session.test_config_access()  # 应该失败
        outsource_page_ok = outsource_session.test_admin_page_access()  # 应该失败
        outsource_logout_ok = outsource_session.logout()
    else:
        outsource_user_info = None
        outsource_publish_ok = False
        outsource_config_ok = False
        outsource_page_ok = False
        outsource_logout_ok = False
    print()
    
    # 4. 敏感词测试
    print("4️⃣ 内容审核测试")
    print("-" * 30)
    audit_session = TestSession()
    audit_session.login(TEST_ADMIN_USER, TEST_ADMIN_PASS)
    
    # 测试敏感词拦截
    sensitive_ok = not audit_session.test_publish("敏感词测试", "这篇文章包含测试敏感词内容")
    audit_session.logout()
    print()
    
    # 5. 测试结果汇总
    print("📊 测试结果汇总")
    print("=" * 60)
    
    results = {
        "基础功能": {
            "健康检查": health_ok,
            "未授权访问控制": unauthorized_ok
        },
        "管理员功能": {
            "登录": admin_login_ok,
            "用户信息": admin_user_info is not None,
            "文章发布": admin_publish_ok,
            "配置访问": admin_config_ok,
            "管理后台访问": admin_page_ok,
            "登出": admin_logout_ok
        },
        "外包人员功能": {
            "登录": outsource_login_ok,
            "用户信息": outsource_user_info is not None,
            "文章发布": outsource_publish_ok,
            "配置访问限制": not outsource_config_ok,  # 应该被拒绝
            "管理后台访问限制": not outsource_page_ok,  # 应该被拒绝
            "登出": outsource_logout_ok
        },
        "内容审核": {
            "敏感词拦截": sensitive_ok
        }
    }
    
    total_tests = 0
    passed_tests = 0
    
    for category, tests in results.items():
        print(f"\n{category}:")
        for test_name, result in tests.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {test_name}: {status}")
            total_tests += 1
            if result:
                passed_tests += 1
    
    print(f"\n总体结果: {passed_tests}/{total_tests} 测试通过")
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"成功率: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 测试结果优秀！V2.2版本功能正常")
    elif success_rate >= 70:
        print("⚠️ 测试结果良好，部分功能需要检查")
    else:
        print("❌ 测试结果不理想，需要修复问题")
    
    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    main()