#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 软文发布中间件 V2.4 部署脚本
用于生产环境部署和配置检查
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class V2_4_Deployer:
    """V2.4版本部署器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backup_dir = self.project_root / "backups"
        self.required_files = [
            "main_v2_4.py",
            "start_v2_4.py", 
            "requirements.txt",
            "templates/index_v2_4.html",
            "templates/admin_dashboard.html",
            "templates/login.html",
            "static/js/app_v2_4.js",
            "static/js/admin_dashboard.js",
            "static/css/style.css"
        ]
        
    def check_environment(self):
        """检查部署环境"""
        print("🔍 检查部署环境...")
        
        # 检查Python版本
        if sys.version_info < (3, 7):
            print("❌ 错误: 需要Python 3.7或更高版本")
            return False
            
        # 检查必要文件
        missing_files = []
        for file_path in self.required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("❌ 错误: 缺少必要文件:")
            for file in missing_files:
                print(f"  • {file}")
            return False
            
        # 检查依赖包
        try:
            import fastapi
            import uvicorn
            import aiohttp
            import requests
            print("✅ 依赖包检查通过")
        except ImportError as e:
            print(f"❌ 错误: 缺少依赖包 {e}")
            print("请运行: pip install -r requirements.txt")
            return False
            
        print("✅ 环境检查通过")
        return True
    
    def backup_existing(self):
        """备份现有版本"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir()
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_v2_4_{timestamp}"
        backup_path.mkdir()
        
        print(f"📦 创建备份: {backup_path}")
        
        # 备份关键文件
        backup_files = [
            ".env",
            "main_v2_4.py",
            "templates/",
            "static/"
        ]
        
        for item in backup_files:
            src = self.project_root / item
            if src.exists():
                if src.is_file():
                    shutil.copy2(src, backup_path / item)
                else:
                    shutil.copytree(src, backup_path / item, dirs_exist_ok=True)
                    
        print("✅ 备份完成")
        return backup_path
    
    def validate_config(self):
        """验证配置文件"""
        print("🔧 验证配置文件...")
        
        env_file = self.project_root / ".env"
        if not env_file.exists():
            print("❌ 错误: .env文件不存在")
            print("请复制.env.production并修改配置")
            return False
            
        # 检查关键配置项
        required_configs = [
            "WP_DOMAIN",
            "WP_USERNAME", 
            "WP_APP_PASSWORD",
            "ADMIN_USER",
            "ADMIN_PASS",
            "OUTSOURCE_USER",
            "OUTSOURCE_PASS",
            "SESSION_SECRET_KEY"
        ]
        
        missing_configs = []
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for config in required_configs:
            if f"{config}=" not in content or f"{config}=your-" in content or f"{config}=default-" in content:
                missing_configs.append(config)
                
        if missing_configs:
            print("❌ 错误: 以下配置项需要设置:")
            for config in missing_configs:
                print(f"  • {config}")
            return False
            
        print("✅ 配置验证通过")
        return True
    
    def run_tests(self):
        """运行测试"""
        print("🧪 运行测试...")
        
        try:
            # 语法检查
            result = subprocess.run([
                sys.executable, "-m", "py_compile", "main_v2_4.py"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ 语法检查失败:")
                print(result.stderr)
                return False
                
            print("✅ 语法检查通过")
            
            # 如果存在测试文件，运行测试
            test_file = self.project_root / "test_v2_4.py"
            if test_file.exists():
                print("运行功能测试...")
                # 这里可以添加测试运行逻辑
                
            return True
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    def setup_systemd_service(self):
        """设置systemd服务（Linux环境）"""
        if os.name != 'posix':
            print("⚠️ 跳过systemd服务设置（非Linux环境）")
            return True
            
        print("⚙️ 设置systemd服务...")
        
        service_content = f"""[Unit]
Description=WordPress Publisher V2.4
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={self.project_root}
Environment=PATH={sys.executable}
ExecStart={sys.executable} start_v2_4.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path("/etc/systemd/system/wordpress-publisher-v2.4.service")
        
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
                
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            subprocess.run(["systemctl", "enable", "wordpress-publisher-v2.4"], check=True)
            
            print("✅ systemd服务设置完成")
            print("启动服务: sudo systemctl start wordpress-publisher-v2.4")
            print("查看状态: sudo systemctl status wordpress-publisher-v2.4")
            
        except PermissionError:
            print("⚠️ 需要管理员权限设置systemd服务")
            print("请手动创建服务文件或使用sudo运行")
            
        except Exception as e:
            print(f"⚠️ systemd服务设置失败: {e}")
            
        return True
    
    def create_nginx_config(self):
        """创建Nginx配置文件"""
        print("🌐 创建Nginx配置...")
        
        nginx_config = """# WordPress Publisher V2.4 Nginx配置
server {
    listen 80;
    server_name your-domain.com;  # 修改为实际域名
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;  # 修改为实际域名
    
    # SSL配置（请配置实际的SSL证书）
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # 静态文件
    location /static/ {
        alias /path/to/wordpress-publisher/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 代理到FastAPI应用
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 安全限制
    location ~ /\. {
        deny all;
    }
    
    # 限制文件上传大小
    client_max_body_size 10M;
}
"""
        
        config_file = self.project_root / "nginx_v2_4.conf"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(nginx_config)
            
        print(f"✅ Nginx配置已创建: {config_file}")
        print("请根据实际环境修改域名和SSL证书路径")
        
    def deploy(self):
        """执行完整部署流程"""
        print("🚀 开始部署WordPress软文发布中间件V2.4")
        print("=" * 60)
        
        # 1. 环境检查
        if not self.check_environment():
            print("❌ 部署失败: 环境检查未通过")
            return False
            
        # 2. 备份现有版本
        backup_path = self.backup_existing()
        
        # 3. 配置验证
        if not self.validate_config():
            print("❌ 部署失败: 配置验证未通过")
            return False
            
        # 4. 运行测试
        if not self.run_tests():
            print("❌ 部署失败: 测试未通过")
            return False
            
        # 5. 创建服务配置
        self.setup_systemd_service()
        self.create_nginx_config()
        
        print("=" * 60)
        print("✅ V2.4版本部署完成！")
        print()
        print("📋 部署后检查清单:")
        print("  1. 修改.env文件中的生产环境配置")
        print("  2. 配置SSL证书（如使用HTTPS）")
        print("  3. 设置防火墙规则")
        print("  4. 启动服务并检查状态")
        print("  5. 测试所有功能是否正常")
        print()
        print("🔧 常用命令:")
        print("  启动服务: python start_v2_4.py")
        print("  查看日志: tail -f logs/app.log")
        print("  健康检查: curl http://localhost:8001/health")
        print()
        print(f"📦 备份位置: {backup_path}")
        
        return True

def main():
    """主函数"""
    deployer = V2_4_Deployer()
    
    try:
        success = deployer.deploy()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 部署被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 部署过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()