# WordPress 软文发布中间件 V2.1

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个现代化的WordPress软文发布中间件，集成百度AI内容审核功能，为外包人员提供安全、高效的内容发布解决方案。

## ✨ 主要特性

- 🎨 **现代化Web界面** - 集成Quill.js富文本编辑器，支持所见即所得编辑
- 🤖 **智能内容审核** - 集成百度AI文本审核，自动检测敏感内容
- 🔒 **安全发布机制** - 强制待审核状态，多重身份验证
- ⚙️ **可视化配置管理** - 完整的后台管理界面
- 📊 **实时监控统计** - 发布趋势分析和系统状态监控
- 🔄 **智能容错机制** - 自动端点切换，增强系统稳定性

## 🚀 快速开始

### 环境要求

- Python 3.8+
- WordPress 5.0+
- 百度智能云账号（可选，支持测试模式）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/wordpress-publisher-v2.git
cd wordpress-publisher-v2
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.template .env
# 编辑 .env 文件，填入您的配置信息
```

4. **启动服务**
```bash
python main_v2.py
```

5. **访问系统**
- 发布页面：http://localhost:8001
- 管理后台：http://localhost:8001/admin
- API文档：http://localhost:8001/docs

## 📖 详细文档

- [配置指南](README_V2.1.md) - 详细的配置和部署说明
- [WordPress插件修复指南](WordPress插件修复指南.md) - 解决WordPress兼容性问题
- [API文档](http://localhost:8001/docs) - 完整的API接口文档

## 🎯 核心功能

### 富文本编辑器
- 支持多种文本格式（粗体、斜体、标题等）
- 内置文章模板（基础文章、产品介绍、新闻资讯）
- 实时预览功能
- 自动保存草稿

### 内容审核系统
- 百度AI智能审核
- 政治敏感词检测
- 详细违规信息反馈
- 测试模式支持

### 管理后台
- 可视化配置管理
- 发布统计和趋势分析
- 系统状态监控
- 历史记录管理

## 🔧 配置说明

### WordPress配置
```bash
WP_DOMAIN=your-domain.com
WP_USERNAME=your_username
WP_APP_PASSWORD=your_app_password
```

### 百度AI配置
```bash
BAIDU_API_KEY=your_api_key
BAIDU_SECRET_KEY=your_secret_key
```

### 安全配置
```bash
CLIENT_AUTH_TOKEN=your_secure_token
TEST_MODE=false  # 生产环境设为false
```

## 🧪 测试

运行完整测试套件：
```bash
python test_v2.py
```

测试WordPress连接：
```bash
python wordpress_client_requests.py
```

## 📊 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web前端界面    │────│  FastAPI后端服务  │────│   WordPress     │
│  (富文本编辑器)   │    │   (Python 3.8+)  │    │   (REST API)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   百度AI审核API   │
                       │  (内容安全检测)    │
                       └──────────────────┘
```

## 🛡️ 安全特性

- **多重身份验证** - 外包身份令牌 + WordPress应用密码
- **内容安全审核** - 百度AI + WordPress人工审核
- **强制待审核** - 所有文章自动设为pending状态
- **配置信息脱敏** - 敏感信息安全显示

## 📈 版本历史

### V2.1.0 (当前版本)
- ✅ 集成富文本编辑器
- ✅ 添加配置管理界面
- ✅ 智能端点切换机制
- ✅ 增强容错和错误处理
- ✅ 本地测试环境优化

### V1.0.0
- ✅ 基础发布功能
- ✅ 百度AI内容审核
- ✅ WordPress REST API集成

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [Quill.js](https://quilljs.com/) - 强大的富文本编辑器
- [百度智能云](https://cloud.baidu.com/) - AI内容审核服务
- [WordPress](https://wordpress.org/) - 内容管理系统

## 📞 支持

如果您遇到问题或需要帮助：

- 📧 提交 [Issue](https://github.com/your-username/wordpress-publisher-v2/issues)
- 📖 查看 [文档](README_V2.1.md)
- 💬 参与 [讨论](https://github.com/your-username/wordpress-publisher-v2/discussions)

---

**让内容发布更智能、更安全、更高效！** 🚀