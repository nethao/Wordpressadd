# WordPress软文发布中间件 V2.2 - 多角色登录系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🆕 V2.2版本新特性

### 🔐 多角色登录系统
- **管理员角色**：拥有完整系统访问权限
  - 可访问发布页面和管理后台
  - 可修改系统配置
  - 可查看系统监控和日志
  
- **外包人员角色**：仅限内容发布权限
  - 只能访问发布页面
  - 无法访问管理后台
  - 无法修改系统配置

### 🛡️ 安全增强
- 基于Session的身份认证
- 24小时会话过期机制
- 路由级权限控制
- 自动登录状态检查

### 🎨 用户体验优化
- 现代化登录界面
- 用户信息实时显示
- 角色权限可视化
- 一键登出功能

## 🚀 快速开始

### 1. 环境准备
```bash
# 确保Python 3.8+已安装
python --version

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置登录凭据
编辑 `.env` 文件，添加登录账户：
```bash
# 多角色登录系统配置
ADMIN_USER=admin
ADMIN_PASS=your_admin_password_here
OUTSOURCE_USER=outsource
OUTSOURCE_PASS=your_outsource_password_here
SESSION_SECRET_KEY=your-super-secret-session-key
```

### 3. 启动服务
```bash
# 方式1：使用启动脚本（推荐）
python start_v2_2.py

# 方式2：直接启动
python main_v2_2.py
```

### 4. 访问系统
- 🔐 **登录页面**：http://localhost:8001/login
- 📝 **发布页面**：http://localhost:8001 （需要登录）
- ⚙️ **管理后台**：http://localhost:8001/admin （仅管理员）
- 📚 **API文档**：http://localhost:8001/docs

## 👥 用户角色说明

### 管理员 (Admin)
```
用户名: admin
密码: [在.env中配置]
权限:
  ✅ 访问发布页面
  ✅ 访问管理后台
  ✅ 修改系统配置
  ✅ 查看系统监控
  ✅ 导出系统报告
```

### 外包人员 (Outsource)
```
用户名: outsource
密码: [在.env中配置]
权限:
  ✅ 访问发布页面
  ❌ 访问管理后台
  ❌ 修改系统配置
  ❌ 查看系统监控
```

## 🔧 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   登录系统       │────│  权限控制中间件   │────│   业务逻辑       │
│  (Session管理)   │    │  (路由守卫)      │    │  (发布/配置)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   用户界面       │    │   API接口        │    │   WordPress     │
│  (登录/发布页)    │    │  (RESTful API)   │    │   (REST API)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🧪 功能测试

### 自动化测试
```bash
# 运行完整测试套件
python test_v2_2.py
```

### 手动测试步骤
1. **登录测试**
   - 访问 http://localhost:8001
   - 应自动重定向到登录页
   - 使用管理员/外包人员账户登录

2. **权限测试**
   - 管理员：可访问所有页面
   - 外包人员：尝试访问 `/admin` 应被拒绝

3. **发布测试**
   - 两种角色都能发布文章
   - 文章状态强制为 `pending`

4. **会话测试**
   - 24小时后会话自动过期
   - 登出后需重新登录

## 📊 监控和日志

### 系统监控
- 活跃会话数量
- 发布成功率统计
- 用户操作日志
- 系统运行状态

### 日志记录
```
[时间] [级别] 消息内容
[14:30:25] [SUCCESS] 用户 admin 登录成功
[14:31:02] [INFO] 文章发布成功 - ID: 123
[14:32:15] [WARNING] 用户 outsource 尝试访问管理后台
```

## 🔒 安全特性

### 身份认证
- 用户名/密码验证
- Session令牌管理
- 自动会话过期

### 权限控制
- 路由级权限检查
- 角色基础访问控制
- API接口权限验证

### 数据保护
- 敏感配置信息脱敏
- 密码字段隐藏显示
- 会话数据安全存储

## 🛠️ 故障排除

### 常见问题

1. **登录失败**
   ```
   问题：用户名或密码错误
   解决：检查 .env 文件中的账户配置
   ```

2. **权限被拒绝**
   ```
   问题：外包人员访问管理后台
   解决：这是正常的权限控制，外包人员无法访问
   ```

3. **会话过期**
   ```
   问题：24小时后自动登出
   解决：重新登录即可，这是安全机制
   ```

4. **配置访问失败**
   ```
   问题：非管理员尝试修改配置
   解决：只有管理员角色可以修改系统配置
   ```

### 调试模式
```bash
# 启用调试模式
export DEBUG=true
python main_v2_2.py
```

## 📈 版本对比

| 功能 | V2.1 | V2.2 |
|------|------|------|
| 富文本编辑器 | ✅ | ✅ |
| 百度AI审核 | ✅ | ✅ |
| WordPress集成 | ✅ | ✅ |
| 配置管理 | ✅ | ✅ |
| 用户登录 | ❌ | ✅ |
| 角色权限 | ❌ | ✅ |
| 会话管理 | ❌ | ✅ |
| 安全增强 | ❌ | ✅ |

## 🔄 升级指南

### 从V2.1升级到V2.2
1. **备份数据**
   ```bash
   cp .env .env.backup
   cp -r static static.backup
   ```

2. **更新配置**
   ```bash
   # 在 .env 文件中添加登录配置
   ADMIN_USER=admin
   ADMIN_PASS=your_password
   OUTSOURCE_USER=outsource
   OUTSOURCE_PASS=your_password
   SESSION_SECRET_KEY=your_secret_key
   ```

3. **启动新版本**
   ```bash
   python main_v2_2.py
   ```

4. **验证功能**
   ```bash
   python test_v2_2.py
   ```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📞 技术支持

如果您遇到问题或需要帮助：

- 📧 提交 [Issue](https://github.com/your-username/wordpress-publisher-v2/issues)
- 📖 查看 [文档](README.md)
- 🧪 运行 [测试](test_v2_2.py)

---

**WordPress软文发布中间件 V2.2 - 让内容发布更安全、更智能！** 🚀