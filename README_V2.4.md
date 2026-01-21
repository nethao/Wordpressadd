# WordPress 软文发布中间件 V2.4

## 版本概述

V2.4版本是功能优化与审核逻辑调整版本，在V2.3版本的基础上增加了编辑器HTML代码模式、发布历史面板以及AI审核开关优化等重要功能。

## 🆕 V2.4 新功能特性

### 1. 编辑器HTML代码模式
- **功能描述**: 在富文本编辑器基础上新增HTML代码编辑模式
- **使用场景**: 
  - 需要插入特定广告代码
  - 自定义HTML格式
  - 精确控制页面布局
- **操作方式**: 
  - 点击工具栏"💻 代码模式"按钮
  - 支持富文本编辑器与代码编辑器实时同步
  - 快捷键: `Ctrl+Shift+C`

### 2. 发布历史面板
- **功能描述**: 页面下方新增发布历史面板，实时同步WordPress文章状态
- **显示内容**:
  - 文章标题和发布时间
  - 文章状态：已发布(Published)、待审核(Pending)、草稿(Draft)
  - 文章ID和查看链接
- **数据来源**: 直接从WordPress REST API获取
- **刷新机制**: 自动刷新 + 手动刷新按钮

### 3. AI审核开关优化
- **背景**: 百度AI对软文广告审核过于严格，导致通过率低
- **解决方案**: 
  - 新增`ENABLE_AI_CHECK`环境变量控制AI审核
  - 当设置为`false`时，跳过百度AI检测，直接发布到WordPress
  - 内容安全保障移交至WordPress后端人工审核
- **配置方式**: 在`.env`文件中设置`ENABLE_AI_CHECK=false`

## 📋 完整功能列表

### 核心功能
- ✅ WordPress REST API集成
- ✅ 百度AI内容审核（可选）
- ✅ 多角色登录系统（管理员 vs 外包人员）
- ✅ 基于Session的身份认证
- ✅ 路由权限控制

### 编辑器功能
- ✅ Quill.js富文本编辑器
- ✅ HTML代码编辑模式 (V2.4新增)
- ✅ 实时预览功能
- ✅ 模板插入功能
- ✅ 字符计数和限制

### 统计与历史
- ✅ 本月发布统计
- ✅ 发布历史面板 (V2.4新增)
- ✅ 文章状态实时同步

### 用户体验
- ✅ 极简化Web UI设计
- ✅ 响应式布局
- ✅ 快捷键支持
- ✅ 本地草稿保存

## 🚀 快速开始

### 1. 环境要求
- Python 3.7+
- WordPress网站（支持REST API）
- 百度AI账号（可选）

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
复制`.env.template`为`.env`并配置：

```env
# WordPress配置
WP_DOMAIN=your-wordpress-domain.com
WP_USERNAME=your-wp-username
WP_APP_PASSWORD=your-wp-app-password

# 百度AI配置（可选）
BAIDU_API_KEY=your-baidu-api-key
BAIDU_SECRET_KEY=your-baidu-secret-key

# V2.4新增：AI审核开关
ENABLE_AI_CHECK=false

# 登录系统配置
ADMIN_USER=admin
ADMIN_PASS=admin123456
OUTSOURCE_USER=outsource
OUTSOURCE_PASS=outsource123456
```

### 4. 启动服务
```bash
# 使用V2.4启动脚本
python start_v2_4.py

# 或直接使用uvicorn
uvicorn main_v2_4:app --host 0.0.0.0 --port 8001 --reload
```

### 5. 访问系统
- 主页面: http://localhost:8001
- 管理后台: http://localhost:8001/admin/dashboard
- API文档: http://localhost:8001/docs

## 🔧 使用指南

### 编辑器模式切换

#### 富文本编辑模式
- 默认模式，提供可视化编辑体验
- 支持格式化文本、列表、链接、图片等
- 适合一般内容创作

#### HTML代码模式 (V2.4新增)
- 直接编辑HTML源码
- 支持完整的HTML标签
- 适合需要精确控制格式的场景
- 与富文本模式实时同步

#### 预览模式
- 实时预览最终效果
- 支持标题和内容预览
- 快捷键: `Ctrl+P`

### 发布历史面板使用

#### 查看历史
- 自动显示最近20条发布记录
- 显示文章标题、状态、发布时间
- 支持点击查看原文链接

#### 状态说明
- **已发布**: 文章已在WordPress前台显示
- **待审核**: 文章等待管理员审核
- **草稿**: 文章保存为草稿状态

#### 刷新数据
- 自动刷新: 每10分钟自动更新
- 手动刷新: 点击"🔄 刷新"按钮
- 发布成功后自动更新

### AI审核开关配置

#### 启用AI审核 (默认)
```env
ENABLE_AI_CHECK=true
```
- 文章发布前通过百度AI审核
- 检测敏感词和违规内容
- 审核不通过的文章不会发布

#### 禁用AI审核 (V2.4推荐)
```env
ENABLE_AI_CHECK=false
```
- 跳过百度AI审核环节
- 文章直接发布到WordPress
- 依靠WordPress后台人工审核

## 🔐 用户角色与权限

### 管理员 (Admin)
- **登录信息**: admin / admin123456
- **访问权限**: 
  - 文章发布页面 (/)
  - 系统管理后台 (/admin/dashboard)
  - 配置管理接口
  - 所有统计数据

### 外包人员 (Outsource)
- **登录信息**: outsource / outsource123456
- **访问权限**:
  - 文章发布页面 (/)
  - 本月统计数据
  - 发布历史查看
- **限制**:
  - 无法访问管理后台
  - 无法修改系统配置
  - 发布的文章强制为pending状态

## 📊 API接口文档

### V2.4新增接口

#### 获取发布历史
```http
GET /api/publish/history?limit=20
Authorization: Cookie (session_id)
```

**响应示例**:
```json
{
  "status": "success",
  "message": "发布历史获取成功",
  "posts": [
    {
      "id": 123,
      "title": {"rendered": "文章标题"},
      "status": "publish",
      "date": "2024-01-20T10:30:00",
      "modified": "2024-01-20T10:30:00",
      "link": "https://example.com/posts/123"
    }
  ],
  "total": 1
}
```

### 现有接口更新

#### 发布文章 (支持AI审核开关)
```http
POST /publish
Content-Type: application/json
Authorization: Cookie (session_id)

{
  "title": "文章标题",
  "content": "<p>文章内容（支持HTML）</p>"
}
```

**响应示例** (AI审核禁用时):
```json
{
  "status": "success",
  "message": "文章发布成功，已提交待审核队列（AI审核已禁用）",
  "post_id": 123,
  "audit_result": {
    "conclusionType": 1,
    "message": "AI审核已禁用，内容直接通过",
    "ai_check_disabled": true
  }
}
```

## 🧪 测试

### 运行测试脚本
```bash
# 确保服务已启动
python start_v2_4.py

# 在另一个终端运行测试
python test_v2_4.py
```

### 测试覆盖范围
- ✅ 健康检查和API信息
- ✅ 登录系统（管理员 + 外包人员）
- ✅ 权限控制
- ✅ 文章发布功能
- ✅ 本月统计
- ✅ 发布历史 (V2.4新增)
- ✅ HTML代码模式 (V2.4新增)
- ✅ AI审核开关 (V2.4新增)

## 🔄 版本升级

### 从V2.3升级到V2.4

1. **备份数据**
   ```bash
   cp .env .env.backup
   cp -r templates templates.backup
   cp -r static static.backup
   ```

2. **更新文件**
   - 复制`main_v2_4.py`
   - 复制`templates/index_v2_4.html`
   - 复制`static/js/app_v2_4.js`

3. **更新环境配置**
   ```bash
   echo "ENABLE_AI_CHECK=false" >> .env
   ```

4. **启动新版本**
   ```bash
   python start_v2_4.py
   ```

### 配置迁移
V2.4版本完全兼容V2.3的配置，只需添加新的AI审核开关配置即可。

## 🐛 故障排除

### 常见问题

#### 1. 发布历史显示为空
- **原因**: WordPress API连接问题或权限不足
- **解决**: 检查WordPress用户权限，确保应用密码正确

#### 2. HTML代码模式内容丢失
- **原因**: HTML格式不正确或包含不支持的标签
- **解决**: 检查HTML语法，使用标准HTML标签

#### 3. AI审核开关不生效
- **原因**: 环境变量未正确加载
- **解决**: 重启服务，确保`.env`文件中的配置正确

#### 4. 权限控制异常
- **原因**: Session管理问题
- **解决**: 清除浏览器Cookie，重新登录

### 日志查看
```bash
# 查看服务日志
python start_v2_4.py

# 查看详细错误信息
tail -f logs/app.log  # 如果配置了日志文件
```

## 📈 性能优化

### 建议配置
- **生产环境**: 使用Redis存储Session
- **数据库**: 配置WordPress数据库连接池
- **缓存**: 启用WordPress对象缓存
- **CDN**: 配置静态资源CDN加速

### 监控指标
- 发布成功率
- API响应时间
- 用户会话数量
- WordPress连接状态

## 🤝 贡献指南

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd wordpress-publisher

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 启动开发服务器
python start_v2_4.py
```

### 代码规范
- 使用中文注释
- 遵循PEP 8代码风格
- 添加类型注解
- 编写单元测试

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 📞 支持与反馈

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 在线文档

---

**WordPress 软文发布中间件 V2.4** - 让内容发布更简单、更高效！