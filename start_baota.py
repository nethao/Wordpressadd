#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress软文发布系统 - 宝塔面板专用启动脚本
适配宝塔环境的路径和配置
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 WordPress软文发布系统 - 宝塔环境启动")
    print("=" * 50)
    
    # 获取当前目录
    current_dir = Path(__file__).resolve().parent
    os.chdir(current_dir)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        print(f"当前版本: Python {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python版本检查通过: {sys.version}")
    
    # 检查必要文件
    required_files = [
        "main_v2_4_final.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not (current_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        sys.exit(1)
    
    # 检查环境变量文件
    env_files = ['.env', '.env.production']
    env_found = False
    for env_file in env_files:
        if (current_dir / env_file).exists():
            print(f"✅ 找到环境配置文件: {env_file}")
            env_found = True
            break
    
    if not env_found:
        print("⚠️  警告: 未找到环境配置文件(.env 或 .env.production)")
        print("请确保已正确配置环境变量")
    
    # 检查静态文件和模板目录
    static_dir = current_dir / "static"
    template_dir = current_dir / "templates"
    
    if not static_dir.exists():
        print("⚠️  警告: static目录不存在")
    else:
        print("✅ static目录检查通过")
    
    if not template_dir.exists():
        print("⚠️  警告: templates目录不存在")
    else:
        print("✅ templates目录检查通过")
    
    # 尝试安装依赖
    print("\n📦 检查Python依赖包...")
    try:
        import fastapi
        import uvicorn
        import aiohttp
        import jinja2
        print("✅ 核心依赖包检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("正在尝试安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ 依赖包安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖包安装失败，请手动执行: pip install -r requirements.txt")
            sys.exit(1)
    
    # 获取启动参数
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8001))
    
    print(f"\n🌐 启动配置:")
    print(f"   主机: {host}")
    print(f"   端口: {port}")
    print(f"   工作目录: {current_dir}")
    
    # 启动应用
    print(f"\n🚀 启动WordPress软文发布系统...")
    print(f"访问地址: http://{host}:{port}")
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # 使用uvicorn启动
        import uvicorn
        uvicorn.run(
            "main_v2_4_final:app",
            host=host,
            port=port,
            reload=False,  # 生产环境关闭热重载
            access_log=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()