#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布中间件 V2.4 功能测试脚本
测试代码模式、发布历史面板及AI审核开关优化功能
"""

import requests
import json
import time
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8004"
TEST_CREDENTIALS = {
    "admin": {"username": "admin", "password": "admin123456"},
    "outsource": {"username": "outsource", "password": "outsource123456"}
}

class V2_4_Tester:
    """V2.4版本功能测试器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """记录测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")
        
    def test_health_check(self):
        """测试健康检查接口"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                # 检查V2.4版本信息
                if data.get("version") == "2.4.0":
                    # 检查AI审核状态
                    ai_enabled = data.get("ai_check_enabled", True)
                    self.log_test("健康检查", True, f"V2.4服务正常运行，AI审核状态: {'启用' if ai_enabled else '禁用'}")
                    return True
                else:
                    self.log_test("健康检查", False, f"版本不匹配: {data.get('version')}")
                    return False
            else:
                self.log_test("健康检查", False, f"HTTP状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("健康检查", False, f"连接失败: {str(e)}")
            return False
    
    def test_login(self, role="admin"):
        """测试用户登录"""
        try:
            credentials = TEST_CREDENTIALS[role]
            response = self.session.post(f"{BASE_URL}/login", data=credentials)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test(f"{role}登录", True, f"登录成功，角色: {data.get('role')}")
                    return True
                else:
                    self.log_test(f"{role}登录", False, data.get("message", "未知错误"))
                    return False
            else:
                self.log_test(f"{role}登录", False, f"HTTP状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"{role}登录", False, f"登录失败: {str(e)}")
            return False
    
    def test_monthly_stats(self):
        """测试本月统计功能"""
        try:
            response = self.session.get(f"{BASE_URL}/api/stats/monthly")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    count = data.get("monthly_count", 0)
                    month = data.get("current_month", "未知")
                    self.log_test("本月统计", True, f"{month}发布数量: {count}")
                    return True
                else:
                    self.log_test("本月统计", False, data.get("message", "未知错误"))
                    return False
            else:
                self.log_test("本月统计", False, f"HTTP状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("本月统计", False, f"统计失败: {str(e)}")
            return False
    
    def test_publish_history(self):
        """测试发布历史功能（V2.4新增）"""
        try:
            response = self.session.get(f"{BASE_URL}/api/publish/history")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    posts = data.get("posts", [])
                    total = data.get("total", 0)
                    self.log_test("发布历史", True, f"获取到 {total} 条历史记录")
                    return True
                else:
                    self.log_test("发布历史", False, data.get("message", "未知错误"))
                    return False
            else:
                self.log_test("发布历史", False, f"HTTP状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("发布历史", False, f"历史获取失败: {str(e)}")
            return False
    
    def test_publish_with_ai_disabled(self):
        """测试AI审核禁用时的文章发布"""
        try:
            # 测试文章数据
            article_data = {
                "title": "V2.4测试文章 - AI审核已禁用",
                "content": "<h2>测试内容</h2><p>这是一篇测试文章，用于验证V2.4版本的AI审核开关功能。</p><p>当AI审核被禁用时，文章应该直接发布到WordPress，跳过百度AI审核步骤。</p>"
            }
            
            response = self.session.post(f"{BASE_URL}/publish", json=article_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    # 检查是否跳过了AI审核
                    audit_result = data.get("audit_result", {})
                    ai_disabled = audit_result.get("ai_check_disabled", False)
                    
                    if ai_disabled:
                        self.log_test("AI审核开关", True, "AI审核已禁用，文章直接发布")
                    else:
                        self.log_test("AI审核开关", False, "AI审核开关未生效")
                    
                    post_id = data.get("post_id")
                    self.log_test("文章发布", True, f"发布成功，文章ID: {post_id}")
                    return True
                else:
                    self.log_test("文章发布", False, data.get("message", "未知错误"))
                    return False
            else:
                self.log_test("文章发布", False, f"HTTP状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("文章发布", False, f"发布失败: {str(e)}")
            return False
    
    def test_frontend_pages(self):
        """测试前端页面是否正确加载V2.4版本"""
        try:
            # 测试主页面
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                content = response.text
                # 检查是否包含V2.4特有的元素
                v2_4_features = [
                    "文章发布系统 V2.4",  # 页面标题
                    "💻 代码模式",        # 代码模式按钮
                    "📋 发布历史",        # 发布历史面板
                    "app_v2_4.js"        # V2.4 JavaScript文件
                ]
                
                missing_features = []
                for feature in v2_4_features:
                    if feature not in content:
                        missing_features.append(feature)
                
                if not missing_features:
                    self.log_test("前端页面", True, "V2.4前端功能完整")
                    return True
                else:
                    self.log_test("前端页面", False, f"缺少功能: {', '.join(missing_features)}")
                    return False
            else:
                self.log_test("前端页面", False, f"页面加载失败: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("前端页面", False, f"页面测试失败: {str(e)}")
            return False
    
    def test_admin_dashboard(self):
        """测试管理后台是否包含AI审核开关"""
        try:
            response = self.session.get(f"{BASE_URL}/admin/dashboard")
            if response.status_code == 200:
                content = response.text
                # 检查是否包含AI审核开关
                ai_switch_features = [
                    "启用AI内容审核",      # AI审核开关标签
                    "enableAiCheck",      # AI审核开关ID
                    "V2.4",              # 版本标识
                    "AI审核："            # AI审核状态显示
                ]
                
                missing_features = []
                for feature in ai_switch_features:
                    if feature not in content:
                        missing_features.append(feature)
                
                if not missing_features:
                    self.log_test("管理后台", True, "AI审核开关功能完整")
                    return True
                else:
                    self.log_test("管理后台", False, f"缺少功能: {', '.join(missing_features)}")
                    return False
            else:
                self.log_test("管理后台", False, f"后台加载失败: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("管理后台", False, f"后台测试失败: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始V2.4功能测试")
        print("=" * 60)
        
        # 1. 健康检查
        if not self.test_health_check():
            print("❌ 服务器未正常运行，停止测试")
            return False
        
        # 2. 用户登录测试
        if not self.test_login("admin"):
            print("❌ 管理员登录失败，停止测试")
            return False
        
        # 3. 前端页面测试
        self.test_frontend_pages()
        
        # 4. 管理后台测试
        self.test_admin_dashboard()
        
        # 5. API功能测试
        self.test_monthly_stats()
        self.test_publish_history()
        
        # 6. 文章发布测试（AI审核禁用）
        self.test_publish_with_ai_disabled()
        
        # 7. 外包用户登录测试
        self.test_login("outsource")
        
        print("=" * 60)
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """打印测试总结"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 测试总结:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过数量: {passed_tests}")
        print(f"   失败数量: {failed_tests}")
        print(f"   成功率: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        # 保存测试报告
        report_file = f"test_report_v2_4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "version": "V2.4",
                "test_time": datetime.now().isoformat(),
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": success_rate
                },
                "results": self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试报告已保存: {report_file}")

def main():
    """主函数"""
    tester = V2_4_Tester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()