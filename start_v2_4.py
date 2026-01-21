#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布中间件 V2.4 启动脚本
功能优化与审核逻辑调整版本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """启动V2.4版本的应用"""
    
    # 确保在正确的目录中
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🚀 启动 WordPress 软文发布中间件 V2.4")
    print("=" * 50)
    print("📋 版本特性:")
    print("  • 编辑器HTML代码模式")
    print("  • 发布历史面板")
    print("  • AI审核开关优化")
    print("  • Web UI深度重构与极简布局")
    print("  • 本月发布统计功能")
    print("  • 多角色登录系统")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        sys.exit(1)
    
    # 检查必要文件
    required_files = [
        "main_v2_4.py",
        "requirements.txt",
        ".env",
        "templates/index_v2_4.html",
        "static/js/app_v2_4.js"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ 错误: 缺少必要文件:")
        for file in missing_files:
            print(f"  • {file}")
        sys.exit(1)
    
    # 检查环境变量
    print("🔍 检查环境配置...")
    
    # 加载.env文件
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ 错误: 请先安装依赖包")
        print("运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 检查关键配置
    wp_domain = os.getenv("WP_DOMAIN")
    wp_username = os.getenv("WP_USERNAME")
    wp_app_password = os.getenv("WP_APP_PASSWORD")
    admin_user = os.getenv("ADMIN_USER")
    admin_pass = os.getenv("ADMIN_PASS")
    enable_ai_check = os.getenv("ENABLE_AI_CHECK", "true").lower()
    
    if not all([wp_domain, wp_username, wp_app_password, admin_user, admin_pass]):
        print("⚠️  警告: 部分配置未设置，将使用测试模式")
        print("请检查 .env 文件中的以下配置:")
        if not wp_domain: print("  • WP_DOMAIN")
        if not wp_username: print("  • WP_USERNAME")
        if not wp_app_password: print("  • WP_APP_PASSWORD")
        if not admin_user: print("  • ADMIN_USER")
        if not admin_pass: print("  • ADMIN_PASS")
    else:
        print("✅ 环境配置检查完成")
    
    # 显示AI审核状态
    if enable_ai_check == "true":
        baidu_api_key = os.getenv("BAIDU_API_KEY")
        baidu_secret_key = os.getenv("BAIDU_SECRET_KEY")
        if baidu_api_key and baidu_secret_key:
            print("🤖 AI审核: 已启用 (百度AI)")
        else:
            print("⚠️  AI审核: 已启用但缺少百度AI密钥")
    else:
        print("🚫 AI审核: 已禁用")
    
    print("=" * 50)
    
    # 启动应用
    try:
        port = os.getenv("PORT", "8002")  # 在try块开始就定义port变量
        print("🌐 启动Web服务器...")
        print(f"📍 访问地址: http://localhost:{port}")
        print("🔑 管理员登录: admin / admin123456")
        print("👥 外包人员登录: outsource / outsource123456")
        print("=" * 50)
        print("按 Ctrl+C 停止服务器")
        print()
        
        # 使用uvicorn启动
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main_v2_4:app",
            "--host", "0.0.0.0",
            "--port", port,
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()