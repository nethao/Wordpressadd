#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布中间件 V2.4 测试脚本
功能优化与审核逻辑调整版本测试
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8002"
TEST_CREDENTIALS = {
    "admin": {"username": "admin", "password": "admin123456"},
    "outsource": {"username": "outsource", "password": "outsource123456"}
}

class V2_4_Tester:
    """V2.4版本功能测试器"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
        self.current_user = None
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 WordPress 软文发布中间件 V2.4 功能测试")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # 基础功能测试
            await self.test_health_check()
            await self.test_api_info()
            
            # 登录系统测试
            await self.test_login_system()
            
            # 管理员功能测试
            await self.test_admin_features()
            
            # 发布功能测试
            await self.test_publish_features()
            
            # V2.4新功能测试
            await self.test_v2_4_features()
            
            # 外包人员功能测试
            await self.test_outsource_features()
        
        # 输出测试结果
        self.print_test_summary()
    
    async def test_health_check(self):
        """测试健康检查接口"""
        print("\n🔍 测试健康检查接口...")
        
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    ai_enabled = data.get('ai_check_enabled', False)
                    print(f"✅ 健康检查通过 - 服务版本: {data.get('version', 'unknown')}")
                    print(f"🤖 AI审核状态: {'启用' if ai_enabled else '禁用'}")
                    self.add_result("健康检查", True, "服务正常运行")
                else:
                    print(f"❌ 健康检查失败 - HTTP {response.status}")
                    self.add_result("健康检查", False, f"HTTP {response.status}")
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            self.add_result("健康检查", False, str(e))
    
    async def test_api_info(self):
        """测试API信息接口"""
        print("\n📋 测试API信息接口...")
        
        try:
            async with self.session.get(f"{BASE_URL}/api/info") as response:
                if response.status == 200:
                    data = await response.json()
                    features = data.get('features', [])
                    v2_4_features = [
                        "编辑器HTML代码模式",
                        "发布历史面板", 
                        "AI审核开关优化"
                    ]
                    
                    has_v2_4_features = all(feature in features for feature in v2_4_features)
                    
                    if has_v2_4_features:
                        print("✅ API信息获取成功 - V2.4功能完整")
                        self.add_result("API信息", True, "V2.4功能完整")
                    else:
                        print("⚠️ API信息获取成功 - 部分V2.4功能缺失")
                        self.add_result("API信息", False, "部分V2.4功能缺失")
                else:
                    print(f"❌ API信息获取失败 - HTTP {response.status}")
                    self.add_result("API信息", False, f"HTTP {response.status}")
        except Exception as e:
            print(f"❌ API信息获取异常: {e}")
            self.add_result("API信息", False, str(e))
    
    async def test_login_system(self):
        """测试登录系统"""
        print("\n🔐 测试登录系统...")
        
        # 测试管理员登录
        admin_login = await self.login("admin")
        if admin_login:
            print("✅ 管理员登录成功")
            self.add_result("管理员登录", True, "登录成功")
            await self.logout()
        else:
            print("❌ 管理员登录失败")
            self.add_result("管理员登录", False, "登录失败")
        
        # 测试外包人员登录
        outsource_login = await self.login("outsource")
        if outsource_login:
            print("✅ 外包人员登录成功")
            self.add_result("外包人员登录", True, "登录成功")
            await self.logout()
        else:
            print("❌ 外包人员登录失败")
            self.add_result("外包人员登录", False, "登录失败")
    
    async def test_admin_features(self):
        """测试管理员功能"""
        print("\n👑 测试管理员功能...")
        
        if not await self.login("admin"):
            print("❌ 无法登录管理员账户，跳过管理员功能测试")
            return
        
        # 测试配置获取
        try:
            async with self.session.get(f"{BASE_URL}/config") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        config = data.get('config', {})
                        ai_check_enabled = config.get('enable_ai_check', True)
                        print(f"✅ 配置获取成功 - AI审核: {'启用' if ai_check_enabled else '禁用'}")
                        self.add_result("配置获取", True, "获取成功")
                    else:
                        print("❌ 配置获取失败")
                        self.add_result("配置获取", False, "获取失败")
                else:
                    print(f"❌ 配置获取失败 - HTTP {response.status}")
                    self.add_result("配置获取", False, f"HTTP {response.status}")
        except Exception as e:
            print(f"❌ 配置获取异常: {e}")
            self.add_result("配置获取", False, str(e))
        
        await self.logout()
    
    async def test_publish_features(self):
        """测试发布功能"""
        print("\n📝 测试发布功能...")
        
        if not await self.login("admin"):
            print("❌ 无法登录，跳过发布功能测试")
            return
        
        # 测试本月统计
        try:
            async with self.session.get(f"{BASE_URL}/api/stats/monthly") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        count = data.get('monthly_count', 0)
                        month = data.get('current_month', '未知')
                        print(f"✅ 本月统计获取成功 - {month}: {count}篇")
                        self.add_result("本月统计", True, f"{count}篇")
                    else:
                        print("❌ 本月统计获取失败")
                        self.add_result("本月统计", False, "获取失败")
                else:
                    print(f"❌ 本月统计获取失败 - HTTP {response.status}")
                    self.add_result("本月统计", False, f"HTTP {response.status}")
        except Exception as e:
            print(f"❌ 本月统计获取异常: {e}")
            self.add_result("本月统计", False, str(e))
        
        # 测试文章发布
        test_article = {
            "title": f"V2.4测试文章 - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "content": "<h2>V2.4功能测试</h2><p>这是一篇测试文章，用于验证V2.4版本的发布功能。</p><ul><li>编辑器HTML代码模式</li><li>发布历史面板</li><li>AI审核开关优化</li></ul><p>测试时间: " + datetime.now().isoformat() + "</p>"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/publish",
                json=test_article,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        post_id = data.get('post_id', '未知')
                        audit_result = data.get('audit_result', {})
                        ai_disabled = audit_result.get('ai_check_disabled', False)
                        
                        print(f"✅ 文章发布成功 - ID: {post_id}")
                        if ai_disabled:
                            print("🚫 AI审核已禁用，内容直接发布")
                        else:
                            print("🤖 AI审核通过")
                        
                        self.add_result("文章发布", True, f"ID: {post_id}")
                    else:
                        message = data.get('message', '未知错误')
                        print(f"❌ 文章发布失败: {message}")
                        self.add_result("文章发布", False, message)
                else:
                    print(f"❌ 文章发布失败 - HTTP {response.status}")
                    self.add_result("文章发布", False, f"HTTP {response.status}")
        except Exception as e:
            print(f"❌ 文章发布异常: {e}")
            self.add_result("文章发布", False, str(e))
        
        await self.logout()
    
    async def test_v2_4_features(self):
        """测试V2.4新功能"""
        print("\n🆕 测试V2.4新功能...")
        
        if not await self.login("admin"):
            print("❌ 无法登录，跳过V2.4功能测试")
            return
        
        # 测试发布历史接口
        try:
            async with self.session.get(f"{BASE_URL}/api/publish/history?limit=10") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        posts = data.get('posts', [])
                        total = data.get('total', 0)
                        print(f"✅ 发布历史获取成功 - 共{total}条记录")
                        
                        # 显示最近几条记录
                        if posts:
                            print("📋 最近发布记录:")
                            for i, post in enumerate(posts[:3]):
                                title = post.get('title', {}).get('rendered', '无标题')
                                status = post.get('status', '未知')
                                date = post.get('date', '未知时间')
                                print(f"  {i+1}. {title[:30]}... [{status}] {date[:10]}")
                        
                        self.add_result("发布历史", True, f"{total}条记录")
                    else:
                        print("❌ 发布历史获取失败")
                        self.add_result("发布历史", False, "获取失败")
                else:
                    print(f"❌ 发布历史获取失败 - HTTP {response.status}")
                    self.add_result("发布历史", False, f"HTTP {response.status}")
        except Exception as e:
            print(f"❌ 发布历史获取异常: {e}")
            self.add_result("发布历史", False, str(e))
        
        # 测试HTML代码模式发布
        html_article = {
            "title": f"HTML代码模式测试 - {datetime.now().strftime('%H%M%S')}",
            "content": """
            <div class="test-article">
                <h2>HTML代码模式测试</h2>
                <p>这是通过<strong>HTML代码模式</strong>创建的测试文章。</p>
                <blockquote>
                    <p>V2.4版本新增了HTML代码编辑器，允许用户直接编辑HTML源码。</p>
                </blockquote>
                <ul>
                    <li>支持完整的HTML标签</li>
                    <li>实时预览功能</li>
                    <li>与富文本编辑器同步</li>
                </ul>
                <p><em>测试时间: """ + datetime.now().isoformat() + """</em></p>
            </div>
            """
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/publish",
                json=html_article,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        post_id = data.get('post_id', '未知')
                        print(f"✅ HTML代码模式发布成功 - ID: {post_id}")
                        self.add_result("HTML代码模式", True, f"ID: {post_id}")
                    else:
                        message = data.get('message', '未知错误')
                        print(f"❌ HTML代码模式发布失败: {message}")
                        self.add_result("HTML代码模式", False, message)
                else:
                    print(f"❌ HTML代码模式发布失败 - HTTP {response.status}")
                    self.add_result("HTML代码模式", False, f"HTTP {response.status}")
        except Exception as e:
            print(f"❌ HTML代码模式发布异常: {e}")
            self.add_result("HTML代码模式", False, str(e))
        
        await self.logout()
    
    async def test_outsource_features(self):
        """测试外包人员功能"""
        print("\n👥 测试外包人员功能...")
        
        if not await self.login("outsource"):
            print("❌ 无法登录外包账户，跳过外包功能测试")
            return
        
        # 测试外包人员权限（应该无法访问配置）
        try:
            async with self.session.get(f"{BASE_URL}/config") as response:
                if response.status == 403:
                    print("✅ 外包人员权限控制正常 - 无法访问配置")
                    self.add_result("权限控制", True, "正常拦截")
                else:
                    print(f"❌ 外包人员权限控制异常 - HTTP {response.status}")
                    self.add_result("权限控制", False, f"HTTP {response.status}")
        except Exception as e:
            print(f"❌ 权限控制测试异常: {e}")
            self.add_result("权限控制", False, str(e))
        
        # 测试外包人员发布功能
        outsource_article = {
            "title": f"外包人员测试文章 - {datetime.now().strftime('%H%M%S')}",
            "content": "<h2>外包人员发布测试</h2><p>这是外包人员发布的测试文章。</p><p>测试时间: " + datetime.now().isoformat() + "</p>"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/publish",
                json=outsource_article,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        post_id = data.get('post_id', '未知')
                        print(f"✅ 外包人员发布成功 - ID: {post_id}")
                        self.add_result("外包人员发布", True, f"ID: {post_id}")
                    else:
                        message = data.get('message', '未知错误')
                        print(f"❌ 外包人员发布失败: {message}")
                        self.add_result("外包人员发布", False, message)
                else:
                    print(f"❌ 外包人员发布失败 - HTTP {response.status}")
                    self.add_result("外包人员发布", False, f"HTTP {response.status}")
        except Exception as e:
            print(f"❌ 外包人员发布异常: {e}")
            self.add_result("外包人员发布", False, str(e))
        
        await self.logout()
    
    async def login(self, user_type):
        """登录指定类型的用户"""
        credentials = TEST_CREDENTIALS.get(user_type)
        if not credentials:
            return False
        
        try:
            async with self.session.post(
                f"{BASE_URL}/login",
                data=credentials,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        self.current_user = user_type
                        return True
        except Exception as e:
            print(f"登录异常: {e}")
        
        return False
    
    async def logout(self):
        """登出当前用户"""
        try:
            async with self.session.post(f"{BASE_URL}/logout") as response:
                if response.status == 200:
                    self.current_user = None
                    return True
        except Exception:
            pass
        return False
    
    def add_result(self, test_name, success, message):
        """添加测试结果"""
        self.test_results.append({
            "name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now()
        })
    
    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        print()
        
        # 详细结果
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['name']}: {result['message']}")
        
        print("\n" + "=" * 60)
        
        if success_rate >= 90:
            print("🎉 测试结果优秀！V2.4版本功能正常")
        elif success_rate >= 70:
            print("👍 测试结果良好，部分功能需要检查")
        else:
            print("⚠️ 测试结果需要改进，请检查失败的功能")

async def main():
    """主函数"""
    tester = V2_4_Tester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())