# 文章发布系统 V2.3 - Web UI深度重构与功能增强

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🆕 V2.3版本重大更新

### 🎨 Web UI深度重构
- **极简化设计**：移除开发痕迹，打造专业级发布界面
- **全宽编辑器**：沉浸式写作体验，删除右侧干扰模块
- **视觉降噪**：精简标题和描述，突出核心功能
- **响应式布局**：完美适配桌面和移动设备

### 📊 本月发布统计
- **实时计数器**：头部显示"本月已发布：N 篇稿件"
- **WordPress集成**：直接查询WordPress数据库获取准确统计
- **自动更新**：发布成功后前端立即更新计数，无需刷新
- **智能端点**：支持自定义文章类型和标准文章类型

### 🔐 权限分离优化
- **管理员**：可访问系统管理页面，查看完整统计和配置
- **外包人员**：仅显示发布界面和本月统计，隐藏管理功能
- **独立管理页**：将原侧边栏功能迁移到专门的系统管理页面

## 🚀 快速开始

### 1. 环境准备
```bash
# 确保Python 3.8+已安装
python --version

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置登录凭据
编辑 `.env` 文件：
```bash
# 多角色登录系统配置
ADMIN_USER=admin
ADMIN_PASS=your_admin_password_here
OUTSOURCE_USER=outsource
OUTSOURCE_PASS=your_outsource_password_here
SESSION_SECRET_KEY=your-super-secret-session-key

# WordPress配置
WP_DOMAIN=your-wordpress-domain.com
WP_USERNAME=your_wp_username
WP_APP_PASSWORD=your_wp_application_password

# 百度AI配置
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
```

### 3. 启动服务
```bash
# 方式1：使用启动脚本（推荐）
python start_v2_3.py

# 方式2：直接启动
python main_v2_3.py
```

### 4. 访问系统
- 🔐 **登录页面**：http://localhost:8001/login
- 📝 **发布页面**：http://localhost:8001 （需要登录）
- ⚙️ **系统管理**：http://localhost:8001/admin/dashboard （仅管理员）

## 🎯 核心功能

### 📝 极简发布界面
```
┌─────────────────────────────────────────────────────────┐
│ 📝 文章发布系统                    👤 用户名 🚪 退出登录 │
│ 本月已发布：42 篇稿件              🏷️ 管理员            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✍️ 撰写新文章                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 文章标题: [                              ] 0/200   │ │
│  │                                                     │ │
│  │ 📝编辑 👁️预览 🗑️清空 📄模板                        │ │
│  │ ┌─────────────────────────────────────────────────┐ │ │
│  │ │                                                 │ │ │
│  │ │           富文本编辑器区域                       │ │ │
│  │ │              (全宽显示)                         │ │ │
│  │ │                                                 │ │ │
│  │ └─────────────────────────────────────────────────┘ │ │
│  │                                        0/50000     │ │
│  │                                                     │ │
│  │     📤 发布文章  🔄 重置表单  💾 保存草稿           │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 📊 本月统计功能
- **数据来源**：WordPress REST API查询 `post_type=adv_posts` 且 `status=publish`
- **时间范围**：当前月份1日至月末
- **实时更新**：发布成功后自动+1
- **权限控制**：所有登录用户都可查看

### ⚙️ 系统管理页面（仅管理员）
- **发布统计**：总发布数、成功率、今日发布、审核拒绝
- **发布趋势图**：最近7天的发布数据可视化
- **系统配置**：WordPress、百度AI、安全配置管理
- **发布历史**：详细的发布记录和状态
- **系统日志**：实时系统运行日志
- **数据导出**：系统报告和历史记录导出

## 🔧 API接口

### 新增接口

#### GET /api/stats/monthly
获取本月发布统计
```json
{
  "status": "success",
  "message": "统计数据获取成功",
  "monthly_count": 42,
  "current_month": "2026年01月"
}
```

#### GET /admin/dashboard
系统管理页面（需要管理员权限）

### 现有接口
- `POST /login` - 用户登录
- `POST /logout` - 用户登出
- `POST /publish` - 发布文章
- `GET /api/user` - 获取用户信息
- `GET /config` - 获取配置（管理员）
- `POST /config` - 更新配置（管理员）

## 🎨 UI/UX 改进

### 视觉设计
- **现代化配色**：渐变背景 + 毛玻璃效果
- **极简布局**：去除冗余元素，突出核心功能
- **统一图标**：Emoji图标系统，提升视觉识别
- **响应式设计**：完美适配各种屏幕尺寸

### 交互体验
- **快捷键支持**：
  - `Ctrl+Enter` - 快速发布
  - `Ctrl+S` - 保存草稿
  - `Ctrl+P` - 切换预览
  - `Ctrl+L` - 登出
- **实时反馈**：字符计数、保存状态、发布进度
- **智能提示**：表单验证、错误提示、成功确认

### 权限可视化
- **角色标识**：清晰显示当前用户角色
- **功能隐藏**：外包人员自动隐藏管理功能
- **权限提示**：访问受限时友好提示

## 🧪 测试验证

### 自动化测试
```bash
# 运行V2.3完整测试套件
python test_v2_3.py
```

### 测试覆盖
- ✅ 基础功能：健康检查、未授权访问控制
- ✅ 管理员功能：登录、统计、发布、配置、管理页面
- ✅ 外包人员功能：登录、统计、发布、权限限制
- ✅ 内容审核：敏感词拦截
- ✅ V2.3特性：本月统计、UI重构

### 测试结果
```
总体结果: 17/18 测试通过
成功率: 94.4%
🎉 测试结果优秀！V2.3版本功能正常
```

## 📈 版本对比

| 功能特性 | V2.1 | V2.2 | V2.3 |
|----------|------|------|------|
| 富文本编辑器 | ✅ | ✅ | ✅ |
| 百度AI审核 | ✅ | ✅ | ✅ |
| WordPress集成 | ✅ | ✅ | ✅ |
| 配置管理 | ✅ | ✅ | ✅ |
| 多角色登录 | ❌ | ✅ | ✅ |
| 权限控制 | ❌ | ✅ | ✅ |
| 会话管理 | ❌ | ✅ | ✅ |
| **极简UI设计** | ❌ | ❌ | ✅ |
| **本月发布统计** | ❌ | ❌ | ✅ |
| **全宽编辑器** | ❌ | ❌ | ✅ |
| **权限分离** | ❌ | ❌ | ✅ |

## 🔄 升级指南

### 从V2.2升级到V2.3

1. **备份数据**
   ```bash
   cp .env .env.backup
   cp -r templates templates.backup
   cp -r static static.backup
   ```

2. **部署新版本**
   ```bash
   # 停止V2.2服务
   # 启动V2.3服务
   python main_v2_3.py
   ```

3. **验证功能**
   ```bash
   python test_v2_3.py
   ```

4. **检查界面**
   - 访问 http://localhost:8001/login
   - 确认极简化界面显示正常
   - 验证本月统计功能工作

## 🛠️ 故障排除

### 常见问题

1. **本月统计显示0**
   ```
   问题：WordPress连接失败或无发布文章
   解决：检查WordPress配置和网络连接
   ```

2. **界面显示异常**
   ```
   问题：浏览器缓存或CSS加载失败
   解决：清除浏览器缓存，刷新页面
   ```

3. **管理页面访问被拒绝**
   ```
   问题：非管理员用户尝试访问
   解决：使用管理员账户登录
   ```

### 调试模式
```bash
# 启用调试模式
export DEBUG=true
python main_v2_3.py
```

## 🎯 使用场景

### 外包人员工作流
1. 访问 http://localhost:8001/login
2. 使用外包账户登录
3. 查看本月发布统计
4. 使用全宽编辑器撰写文章
5. 发布文章并查看统计更新

### 管理员工作流
1. 使用管理员账户登录
2. 查看发布页面和本月统计
3. 访问系统管理页面
4. 监控发布趋势和系统状态
5. 管理配置和导出报告

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/V2.3-Enhancement`)
3. 提交更改 (`git commit -m 'Add V2.3 features'`)
4. 推送到分支 (`git push origin feature/V2.3-Enhancement`)
5. 开启Pull Request

## 📞 技术支持

如果您遇到问题或需要帮助：

- 📧 提交 [Issue](https://github.com/your-username/wordpress-publisher-v2/issues)
- 📖 查看 [文档](README.md)
- 🧪 运行 [测试](test_v2_3.py)

---

**文章发布系统 V2.3 - 极简设计，专业体验！** 🚀