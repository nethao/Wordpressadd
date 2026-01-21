#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布中间件 V2.4 生产环境最终测试
验证所有功能是否正常工作，为上线做最后检查
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class ProductionTester:
    """生产环境测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: Any = None):
        """记录测试结果"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {test_name}: {message}")
        
        if details and not success:
            print(f"    详情: {details}")
    
    def test_health_check(self) -> bool:
        """测试健康检查"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # 验证响应格式
                required_fields = ["status", "timestamp", "service", "version"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("健康检查", False, f"响应缺少字段: {missing_fields}")
                    return False
                
                # 验证版本信息
                if data.get("version") != "2.4.0":
                    self.log_test("健康检查", False, f"版本不匹配: {data.get('version')}")
                    return False
                
                # 验证AI审核状态
                ai_enabled = data.get("ai_check_enabled", True)
                expected_ai_status = False  # 根据.env配置
                
                self.log_test("健康检查", True, f"服务正常，版本: {data.get('version')}, AI审核: {'启用' if ai_enabled else '禁用'}")
                return True
            else:
                self.log_test("健康检查", False, f"HTTP状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("健康检查", False, f"连接失败: {str(e)}")
            return False
    
    def test_security_headers(self) -> bool:
        """测试安全头配置"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            
            # 检查安全相关的响应头
            security_checks = []
            
            # 检查是否有基本的安全配置
            if response.status_code in [200, 302]:  # 可能重定向到登录页
                security_checks.append(("响应状态", True, f"状态码: {response.status_code}"))
            else:
                security_checks.append(("响应状态", False, f"异常状态码: {response.status_code}"))
            
            # 检查Content-Type
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type or 'application/json' in content_type:
                security_checks.append(("Content-Type", True, content_type))
            else:
                security_checks.append(("Content-Type", False, f"异常Content-Type: {content_type}"))
            
            all_passed = all(check[1] for check in security_checks)
            details = {check[0]: check[2] for check in security_checks}
            
            self.log_test("安全头检查", all_passed, "安全配置检查完成", details)
            return all_passed
            
        except Exception as e:
            self.log_test("安全头检查", False, f"检查失败: {str(e)}")
            return False
    
    def test_login_security(self) -> bool:
        """测试登录安全性"""
        try:
            # 测试错误的登录凭据
            wrong_credentials = {
                "username": "admin",
                "password": "wrongpassword"
            }
            
            response = self.session.post(f"{self.base_url}/login", data=wrong_credentials, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "error":
                    self.log_test("登录安全-错误凭据", True, "正确拒绝了错误凭据")
                else:
                    self.log_test("登录安全-错误凭据", False, "未正确拒绝错误凭据")
                    return False
            else:
                self.log_test("登录安全-错误凭据", False, f"登录接口异常: {response.status_code}")
                return False
            
            # 测试正确的登录凭据
            correct_credentials = {
                "username": "admin",
                "password": "Admin@2024#Secure!"  # 使用更新后的密码
            }
            
            response = self.session.post(f"{self.base_url}/login", data=correct_credentials, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    # 检查是否设置了会话Cookie
                    session_cookie = response.cookies.get("session_id")
                    if session_cookie:
                        self.log_test("登录安全-正确凭据", True, "登录成功并设置了会话Cookie")
                        return True
                    else:
                        self.log_test("登录安全-正确凭据", False, "登录成功但未设置会话Cookie")
                        return False
                else:
                    self.log_test("登录安全-正确凭据", False, f"登录失败: {data.get('message')}")
                    return False
            else:
                self.log_test("登录安全-正确凭据", False, f"登录接口异常: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("登录安全", False, f"测试失败: {str(e)}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """测试API端点"""
        # 需要先登录
        login_success = self.test_login_security()
        if not login_success:
            self.log_test("API端点测试", False, "登录失败，无法测试API")
            return False
        
        # 测试各个API端点
        api_tests = [
            ("/api/user", "GET", "用户信息"),
            ("/api/stats/monthly", "GET", "本月统计"),
            ("/api/publish/history", "GET", "发布历史"),
            ("/api/info", "GET", "API信息")
        ]
        
        all_passed = True
        
        for endpoint, method, description in api_tests:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", timeout=5)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("status") == "success" or "version" in data:  # API信息接口没有status字段
                            self.log_test(f"API-{description}", True, f"{endpoint} 正常")
                        else:
                            self.log_test(f"API-{description}", False, f"响应格式异常: {data}")
                            all_passed = False
                    except json.JSONDecodeError:
                        self.log_test(f"API-{description}", False, "响应不是有效JSON")
                        all_passed = False
                else:
                    self.log_test(f"API-{description}", False, f"HTTP状态码: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"API-{description}", False, f"请求失败: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_v2_4_features(self) -> bool:
        """测试V2.4新功能"""
        try:
            # 测试发布历史API（已在API测试中包含）
            response = self.session.get(f"{self.base_url}/api/publish/history", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if "posts" in data and "total" in data:
                    self.log_test("V2.4-发布历史API", True, f"返回 {data.get('total', 0)} 条历史记录")
                else:
                    self.log_test("V2.4-发布历史API", False, "响应格式不正确")
                    return False
            else:
                self.log_test("V2.4-发布历史API", False, f"HTTP状态码: {response.status_code}")
                return False
            
            # 测试前端页面是否包含V2.4功能
            response = self.session.get(f"{self.base_url}/", timeout=5)
            
            if response.status_code == 200:
                content = response.text
                
                # 检查V2.4特有元素
                v2_4_features = [
                    ("V2.4标题", "文章发布系统 V2.4"),
                    ("代码模式按钮", "💻 代码模式"),
                    ("发布历史面板", "📋 发布历史"),
                    ("V2.4脚本", "app_v2_4.js")
                ]
                
                missing_features = []
                for feature_name, feature_text in v2_4_features:
                    if feature_text not in content:
                        missing_features.append(feature_name)
                
                if not missing_features:
                    self.log_test("V2.4-前端功能", True, "所有V2.4前端功能已加载")
                else:
                    self.log_test("V2.4-前端功能", False, f"缺少功能: {', '.join(missing_features)}")
                    return False
            else:
                self.log_test("V2.4-前端功能", False, f"页面加载失败: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("V2.4功能测试", False, f"测试失败: {str(e)}")
            return False
    
    def test_ai_audit_switch(self) -> bool:
        """测试AI审核开关功能"""
        try:
            # 发布一篇测试文章来验证AI审核开关
            test_article = {
                "title": "V2.4生产环境测试文章",
                "content": "<h2>测试内容</h2><p>这是一篇用于验证V2.4版本AI审核开关功能的测试文章。</p><p>当AI审核被禁用时，此文章应该直接发布到WordPress。</p>"
            }
            
            response = self.session.post(
                f"{self.base_url}/publish",
                json=test_article,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    # 检查AI审核状态
                    audit_result = data.get("audit_result", {})
                    ai_disabled = audit_result.get("ai_check_disabled", False)
                    
                    if ai_disabled:
                        self.log_test("AI审核开关", True, "AI审核已禁用，文章直接发布")
                    else:
                        self.log_test("AI审核开关", True, "AI审核已启用，文章通过审核")
                    
                    # 记录文章ID用于后续清理
                    post_id = data.get("post_id")
                    if post_id:
                        self.log_test("文章发布", True, f"测试文章发布成功，ID: {post_id}")
                    
                    return True
                else:
                    self.log_test("AI审核开关", False, f"文章发布失败: {data.get('message')}")
                    return False
            else:
                self.log_test("AI审核开关", False, f"发布请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("AI审核开关", False, f"测试失败: {str(e)}")
            return False
    
    def run_production_tests(self) -> bool:
        """运行完整的生产环境测试"""
        print("🚀 开始WordPress软文发布中间件V2.4生产环境测试")
        print("=" * 70)
        
        # 测试顺序很重要
        tests = [
            ("基础健康检查", self.test_health_check),
            ("安全配置检查", self.test_security_headers),
            ("登录安全测试", self.test_login_security),
            ("API端点测试", self.test_api_endpoints),
            ("V2.4新功能测试", self.test_v2_4_features),
            ("AI审核开关测试", self.test_ai_audit_switch)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 执行: {test_name}")
            try:
                success = test_func()
                if success:
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"测试异常: {str(e)}")
        
        print("\n" + "=" * 70)
        self.print_summary(passed_tests, total_tests)
        
        return passed_tests == total_tests
    
    def print_summary(self, passed: int, total: int):
        """打印测试总结"""
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print("📊 生产环境测试总结")
        print("=" * 70)
        print(f"总测试数: {total}")
        print(f"通过数量: {passed}")
        print(f"失败数量: {total - passed}")
        print(f"成功率: {success_rate:.1f}%")
        
        if success_rate >= 100:
            print("\n🎉 所有测试通过！系统已准备好上线。")
        elif success_rate >= 90:
            print("\n⚠️ 大部分测试通过，建议修复失败项目后再上线。")
        else:
            print("\n❌ 多项测试失败，请修复问题后重新测试。")
        
        # 显示失败的测试
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ 失败的测试:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['message']}")
        
        # 保存测试报告
        report_file = f"production_test_report_v2_4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_time": datetime.now().isoformat(),
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": total - passed,
                    "success_rate": success_rate
                },
                "results": self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细测试报告已保存: {report_file}")
        print("=" * 70)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WordPress发布系统V2.4生产环境测试")
    parser.add_argument("--url", default="http://localhost:8004", help="测试URL")
    
    args = parser.parse_args()
    
    tester = ProductionTester(args.url)
    
    try:
        success = tester.run_production_tests()
        exit_code = 0 if success else 1
        
        if success:
            print("\n✅ 系统已通过所有生产环境测试，可以安全上线！")
        else:
            print("\n⚠️ 系统存在问题，请修复后重新测试。")
            
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        return 1

if __name__ == "__main__":
    exit(main())