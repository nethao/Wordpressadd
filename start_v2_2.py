#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress软文发布中间件 V2.2 启动脚本
快速启动多角色登录版本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """检查依赖包是否安装"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'aiohttp', 'pydantic', 
        'python-dotenv', 'jinja2', 'python-multipart'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_env_file():
    """检查环境配置文件"""
    print("🔍 检查环境配置...")
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env 文件不存在")
        print("请复制 .env.template 为 .env 并配置相关信息")
        return False
    
    # 检查必要的配置项
    required_configs = [
        'ADMIN_USER', 'ADMIN_PASS', 
        'OUTSOURCE_USER', 'OUTSOURCE_PASS',
        'SESSION_SECRET_KEY'
    ]
    
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    missing_configs = []
    for config in required_configs:
        if f"{config}=" not in env_content:
            missing_configs.append(config)
    
    if missing_configs:
        print(f"⚠️ 缺少配置项: {', '.join(missing_configs)}")
        print("请检查 .env 文件配置")
    
    print("✅ 环境配置文件存在")
    return True

def start_server():
    """启动服务器"""
    print("🚀 启动WordPress软文发布中间件 V2.2...")
    print("=" * 50)
    print("版本: V2.2 - 多角色登录系统")
    print("功能: 管理员 vs 外包人员分权访问")
    print("地址: http://localhost:8001")
    print("登录页: http://localhost:8001/login")
    print("管理后台: http://localhost:8001/admin (仅管理员)")
    print("API文档: http://localhost:8001/docs")
    print("=" * 50)
    
    try:
        # 启动服务
        subprocess.run([
            sys.executable, "main_v2_2.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务启动失败: {e}")
    except FileNotFoundError:
        print("❌ main_v2_2.py 文件不存在")

def main():
    """主函数"""
    print("WordPress软文发布中间件 V2.2 启动器")
    print("=" * 40)
    
    # 检查依赖
    if not check_requirements():
        return
    
    # 检查配置
    if not check_env_file():
        return
    
    # 启动服务
    start_server()

if __name__ == "__main__":
    main()