# WordPress 软文发布中间件 V2.1

## 🆕 V2.1版本更新

### 主要新特性
- ✅ **适配WordPress插件V2.1版本**：使用新的`/adv_posts`端点
- ✅ **富文本编辑器**：集成Quill.js，支持所见即所得编辑
- ✅ **配置管理界面**：在管理后台直接配置所有API和账号信息
- ✅ **增强容错机制**：自动Token刷新，完善的错误处理
- ✅ **本地测试优化**：禁用SSL验证，隐藏警告信息
- ✅ **外包身份验证**：使用`CLIENT_AUTH_TOKEN`进行身份验证

### 技术改进
- 🔧 **API路径更新**：`/wp-json/wp/v2/adv_posts`
- 🔧 **自动文章分类**：插件自动处理，无需手动指定分类ID
- 🔧 **强制待审核状态**：所有文章自动设为`pending`状态
- 🔧 **SSL优化**：本地测试环境使用`verify=False`和`urllib3.disable_warnings()`

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆或下载项目
cd wordpress-publisher-v2

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制并编辑配置文件：
```bash
cp .env.template .env
```

编辑`.env`文件：
```bash
# WordPress配置 - V2.1版本
WP_DOMAIN=your-wordpress-domain.com
WP_USERNAME=your_wp_username
WP_APP_PASSWORD=your_wp_application_password

# 百度AI内容审核配置
BAIDU_API_KEY=your_baidu_api_key_here
BAIDU_SECRET_KEY=your_baidu_secret_key_here

# 外包身份验证令牌（V2.1新增）
CLIENT_AUTH_TOKEN=your_secure_client_token_here

# 服务配置
PORT=8001
DEBUG=false
TEST_MODE=true  # 开启测试模式，无需真实API配置
```

### 3. 启动服务

```bash
# 使用V2.1版本
python main_v2.py
```

服务将在 `http://localhost:8001` 启动

### 4. 访问界面

- **📝 发布页面**：http://localhost:8001
- **⚙️ 管理后台**：http://localhost:8001/admin
- **📚 API文档**：http://localhost:8001/docs
- **🔍 健康检查**：http://localhost:8001/health

## 🔧 配置说明

### WordPress插件V2.1要求

确保您的WordPress安装了支持以下功能的插件：

1. **自定义文章类型**：`adv_posts`
2. **REST API端点**：`/wp-json/wp/v2/adv_posts`
3. **自动分类功能**：插件自动处理文章分类
4. **Application Password支持**：本地环境已强制开启

### 百度AI配置

1. 访问 [百度智能云控制台](https://console.bce.baidu.com/ai/#/ai/antiporn/overview/index)
2. 创建"文本内容审核"应用
3. 获取API Key和Secret Key
4. 在管理后台或`.env`文件中配置

### 外包身份验证

V2.1版本使用`CLIENT_AUTH_TOKEN`进行外包身份验证：

```bash
# 设置一个安全的令牌
CLIENT_AUTH_TOKEN=MySecureToken2024!@#
```

外包人员使用此令牌作为`author_token`进行发布。

## 🎨 富文本编辑器功能

### 支持的格式
- **文本格式**：粗体、斜体、下划线、删除线
- **标题**：H1-H6标题级别
- **列表**：有序列表、无序列表
- **引用**：块引用、代码块
- **链接**：超链接插入
- **图片**：图片插入（支持URL）
- **颜色**：文字颜色、背景色
- **对齐**：左对齐、居中、右对齐

### 编辑器快捷键
- `Ctrl+Enter`：快速发布文章
- `Ctrl+S`：保存草稿到本地
- `Ctrl+P`：切换预览模式

### 模板功能
编辑器内置多种文章模板：
- 基础文章模板
- 产品介绍模板
- 新闻资讯模板

## 📊 管理后台功能

### 统计面板
- 总发布数统计
- 成功率分析
- 今日发布数量
- 审核拒绝统计

### 配置管理
- **WordPress配置**：域名、用户名、应用密码
- **百度AI配置**：API Key、Secret Key
- **安全配置**：外包身份令牌、测试模式开关

### 系统监控
- 实时服务状态
- 发布趋势图表
- 系统日志查看
- 配置状态检查

## 🧪 测试功能

### 运行测试脚本

```bash
# 测试V2.1版本功能
python test_v2.py
```

测试内容包括：
- ✅ 健康检查接口
- ✅ 配置管理API
- ✅ 正常文章发布
- ✅ 敏感内容检测
- ✅ 身份令牌验证

### 测试模式

开启`TEST_MODE=true`后：
- 无需真实的百度AI配置
- 无需真实的WordPress配置
- 使用模拟数据进行测试
- 敏感词检测仍然有效

## 🔒 安全特性

### 身份验证
- 外包身份令牌验证
- WordPress Application Password认证
- 防止未授权访问

### 内容审核
- 百度AI智能审核
- 政治敏感词检测
- 详细违规信息反馈
- 自动拦截违规内容

### 数据保护
- 强制文章待审核状态
- 本地历史记录加密存储
- 配置信息脱敏显示
- 完整的错误日志记录

## 🚨 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查端口占用
   netstat -an | findstr :8001
   
   # 更换端口
   # 修改.env中的PORT=8002
   ```

2. **百度AI调用失败**
   ```bash
   # 检查API密钥配置
   # 确认账户余额充足
   # 检查网络连接
   ```

3. **WordPress连接失败**
   ```bash
   # 确认域名配置正确
   # 检查Application Password
   # 确认插件已安装并激活
   ```

4. **富文本编辑器加载失败**
   ```bash
   # 检查网络连接（需要加载CDN资源）
   # 确认浏览器支持现代JavaScript
   ```

### 日志查看

- **服务日志**：控制台输出
- **系统日志**：管理后台查看
- **发布历史**：本地localStorage存储

## 📈 性能优化

### 生产环境部署

```bash
# 使用Gunicorn部署
pip install gunicorn
gunicorn main_v2:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001

# 使用Nginx反向代理
# 配置SSL证书
# 启用Gzip压缩
```

### 配置优化

```bash
# 生产环境配置
DEBUG=false
TEST_MODE=false

# 启用真实API
BAIDU_API_KEY=real_api_key
BAIDU_SECRET_KEY=real_secret_key
WP_DOMAIN=production-domain.com
```

## 🔄 版本升级

### 从V1.0升级到V2.1

1. **备份数据**
   ```bash
   # 备份.env配置
   cp .env .env.backup
   
   # 导出发布历史
   # 在管理后台点击"导出系统报告"
   ```

2. **更新代码**
   ```bash
   # 使用新的main_v2.py
   # 更新前端文件
   # 安装新依赖
   pip install -r requirements.txt
   ```

3. **迁移配置**
   ```bash
   # 更新.env文件格式
   # 添加CLIENT_AUTH_TOKEN
   # 更新WordPress配置
   ```

## 📞 技术支持

### 联系方式
- 📧 技术支持：通过GitHub Issues
- 📚 文档更新：查看README更新
- 🐛 Bug报告：提交详细错误信息

### 贡献指南
欢迎提交Pull Request和Issue，帮助改进项目功能。

---

**WordPress 软文发布中间件 V2.1** - 让内容发布更智能、更安全、更高效！