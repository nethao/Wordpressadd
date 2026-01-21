#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布中间件 V2.4 安全审计脚本
检查系统安全配置和潜在风险
"""

import os
import re
import hashlib
import secrets
from pathlib import Path
from typing import List, Dict, Any

class SecurityAuditor:
    """安全审计器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.recommendations = []
        
    def log_issue(self, severity: str, message: str, recommendation: str = ""):
        """记录安全问题"""
        issue = {
            "severity": severity,
            "message": message,
            "recommendation": recommendation
        }
        
        if severity == "HIGH":
            self.issues.append(issue)
        elif severity == "MEDIUM":
            self.warnings.append(issue)
        else:
            self.recommendations.append(issue)
    
    def check_env_security(self):
        """检查环境变量安全性"""
        print("🔐 检查环境变量安全性...")
        
        env_file = self.project_root / ".env"
        if not env_file.exists():
            self.log_issue("HIGH", ".env文件不存在", "创建.env文件并设置安全配置")
            return
            
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查默认密码
        default_patterns = [
            (r"ADMIN_PASS=admin123456", "管理员使用默认密码"),
            (r"OUTSOURCE_PASS=outsource123456", "外包用户使用默认密码"),
            (r"SESSION_SECRET_KEY=default-secret-key", "使用默认会话密钥"),
            (r"CLIENT_AUTH_TOKEN=.*test.*", "使用测试认证令牌")
        ]
        
        for pattern, message in default_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.log_issue("HIGH", message, "修改为强密码")
                
        # 检查密码强度
        password_patterns = [
            (r"ADMIN_PASS=(.+)", "管理员密码"),
            (r"OUTSOURCE_PASS=(.+)", "外包用户密码")
        ]
        
        for pattern, desc in password_patterns:
            match = re.search(pattern, content)
            if match:
                password = match.group(1)
                if len(password) < 12:
                    self.log_issue("MEDIUM", f"{desc}长度不足12位", "使用更长的密码")
                if not re.search(r'[A-Z]', password):
                    self.log_issue("MEDIUM", f"{desc}缺少大写字母", "添加大写字母")
                if not re.search(r'[0-9]', password):
                    self.log_issue("MEDIUM", f"{desc}缺少数字", "添加数字")
                if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                    self.log_issue("LOW", f"{desc}缺少特殊字符", "添加特殊字符增强安全性")
    
    def check_file_permissions(self):
        """检查文件权限"""
        print("📁 检查文件权限...")
        
        sensitive_files = [
            ".env",
            ".env.production", 
            "main_v2_4.py"
        ]
        
        for file_name in sensitive_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                # 在Windows上跳过权限检查
                if os.name == 'nt':
                    continue
                    
                stat = file_path.stat()
                mode = oct(stat.st_mode)[-3:]
                
                if file_name == ".env" and mode != "600":
                    self.log_issue("HIGH", f"{file_name}权限过于宽松({mode})", "设置为600权限")
                elif mode.endswith("7"):  # 其他用户有写权限
                    self.log_issue("MEDIUM", f"{file_name}其他用户有写权限", "移除其他用户写权限")
    
    def check_code_security(self):
        """检查代码安全性"""
        print("💻 检查代码安全性...")
        
        main_file = self.project_root / "main_v2_4.py"
        if not main_file.exists():
            return
            
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查潜在的安全问题
        security_patterns = [
            (r'eval\s*\(', "使用eval()函数", "避免使用eval()，使用安全的替代方案"),
            (r'exec\s*\(', "使用exec()函数", "避免使用exec()，使用安全的替代方案"),
            (r'shell=True', "使用shell=True", "避免shell注入，使用参数列表"),
            (r'DEBUG\s*=\s*True', "调试模式开启", "生产环境关闭调试模式"),
            (r'allow_origins=\["?\*"?\]', "CORS允许所有来源", "限制CORS来源到特定域名")
        ]
        
        for pattern, message, recommendation in security_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.log_issue("MEDIUM", message, recommendation)
                
        # 检查SQL注入风险（如果有数据库操作）
        sql_patterns = [
            r'f".*SELECT.*{.*}"',
            r'".*SELECT.*" \+ ',
            r'%.*SELECT.*%'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.log_issue("HIGH", "潜在SQL注入风险", "使用参数化查询")
    
    def check_dependencies(self):
        """检查依赖包安全性"""
        print("📦 检查依赖包...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.log_issue("MEDIUM", "requirements.txt文件不存在", "创建依赖包列表")
            return
            
        with open(requirements_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查是否固定版本
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if '==' not in line and '>=' not in line:
                    package = line.split()[0]
                    self.log_issue("MEDIUM", f"依赖包{package}未固定版本", "使用==固定版本号")
    
    def check_session_security(self):
        """检查会话安全性"""
        print("🔑 检查会话安全性...")
        
        main_file = self.project_root / "main_v2_4.py"
        if not main_file.exists():
            return
            
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查会话配置
        if 'httponly=True' not in content.lower():
            self.log_issue("MEDIUM", "Cookie未设置HttpOnly", "设置HttpOnly防止XSS")
            
        if 'secure=False' in content:
            self.log_issue("MEDIUM", "Cookie未设置Secure标志", "生产环境启用Secure标志")
            
        if 'samesite=' not in content.lower():
            self.log_issue("LOW", "Cookie未设置SameSite", "设置SameSite防止CSRF")
    
    def generate_secure_config(self):
        """生成安全配置建议"""
        print("🛡️ 生成安全配置建议...")
        
        # 生成强密码
        admin_password = secrets.token_urlsafe(16)
        outsource_password = secrets.token_urlsafe(16)
        session_key = secrets.token_urlsafe(32)
        auth_token = secrets.token_urlsafe(24)
        
        secure_config = f"""# 安全配置建议 - 请复制到.env文件

# 强密码配置
ADMIN_PASS={admin_password}
OUTSOURCE_PASS={outsource_password}
SESSION_SECRET_KEY={session_key}
CLIENT_AUTH_TOKEN={auth_token}

# 安全设置
DEBUG=false
TEST_MODE=false
ENABLE_AI_CHECK=false
SECURE_COOKIES=true
CORS_ORIGINS=https://your-domain.com

# 生产环境端口
PORT=8001
"""
        
        config_file = self.project_root / "secure_config_suggestion.txt"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(secure_config)
            
        self.log_issue("LOW", "已生成安全配置建议", f"查看文件: {config_file}")
    
    def run_audit(self):
        """运行完整安全审计"""
        print("🔒 开始安全审计...")
        print("=" * 50)
        
        self.check_env_security()
        self.check_file_permissions()
        self.check_code_security()
        self.check_dependencies()
        self.check_session_security()
        self.generate_secure_config()
        
        print("=" * 50)
        self.print_report()
    
    def print_report(self):
        """打印审计报告"""
        print("📊 安全审计报告")
        print("=" * 50)
        
        if self.issues:
            print("🚨 高风险问题:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue['message']}")
                if issue['recommendation']:
                    print(f"     建议: {issue['recommendation']}")
            print()
            
        if self.warnings:
            print("⚠️ 中等风险问题:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning['message']}")
                if warning['recommendation']:
                    print(f"     建议: {warning['recommendation']}")
            print()
            
        if self.recommendations:
            print("💡 优化建议:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"  {i}. {rec['message']}")
                if rec['recommendation']:
                    print(f"     建议: {rec['recommendation']}")
            print()
            
        # 总结
        total_issues = len(self.issues) + len(self.warnings)
        if total_issues == 0:
            print("✅ 未发现严重安全问题")
        else:
            print(f"📈 发现 {len(self.issues)} 个高风险问题，{len(self.warnings)} 个中等风险问题")
            
        print("=" * 50)
        print("🔐 安全检查完成")

def main():
    """主函数"""
    auditor = SecurityAuditor()
    
    try:
        auditor.run_audit()
    except KeyboardInterrupt:
        print("\n⏹️ 安全审计被用户中断")
    except Exception as e:
        print(f"\n❌ 安全审计过程中发生错误: {e}")

if __name__ == "__main__":
    main()