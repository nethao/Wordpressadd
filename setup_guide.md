# WordPress软文发布中间件 V2.1 - 部署指南

## 🚀 快速部署

### 1. 环境准备
```bash
# 确保Python 3.8+已安装
python --version

# 克隆项目
git clone https://github.com/nethao/Wordpressadd.git
cd Wordpressadd
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 复制配置模板
cp .env.template .env

# 编辑配置文件
# 填入您的WordPress和百度AI配置信息
```

### 4. 启动服务
```bash
# 启动V2.1版本（推荐）
python main_v2.py

# 或启动V1.0版本
python main.py
```

### 5. 访问系统
- 📝 发布页面：http://localhost:8001
- ⚙️ 管理后台：http://localhost:8001/admin
- 📚 API文档：http://localhost:8001/docs

## 🔧 配置说明

### WordPress配置
```bash
WP_DOMAIN=192.168.0.42          # 您的WordPress域名或IP
WP_USERNAME=waibao              # WordPress用户名
WP_APP_PASSWORD=your_app_pass   # WordPress应用密码
```

### 百度AI配置
```bash
BAIDU_API_KEY=your_api_key      # 百度智能云API Key
BAIDU_SECRET_KEY=your_secret    # 百度智能云Secret Key
```

### 安全配置
```bash
CLIENT_AUTH_TOKEN=secure_token  # 外包身份验证令牌
TEST_MODE=false                 # 生产环境设为false
```

## 🧪 测试验证

### 测试WordPress连接
```bash
python wordpress_client_requests.py
```

### 运行完整测试
```bash
python test_v2.py
```

### 测试发布功能
1. 访问 http://localhost:8001
2. 输入测试文章内容
3. 点击发布按钮
4. 检查WordPress后台是否收到文章

## 🛠️ 故障排除

### 常见问题

1. **WordPress连接失败**
   - 检查WP_DOMAIN配置是否正确
   - 确认WordPress应用密码是否有效
   - 验证网络连接是否正常

2. **百度AI审核失败**
   - 检查API Key和Secret Key是否正确
   - 确认百度智能云账户余额充足
   - 可以设置TEST_MODE=true跳过审核测试

3. **端口占用问题**
   - 修改.env文件中的PORT配置
   - 或使用命令：`netstat -ano | findstr :8001`

### 日志查看
系统会在控制台输出详细的运行日志，包括：
- API请求响应
- 错误信息和堆栈跟踪
- WordPress连接状态
- 百度AI审核结果

## 📞 技术支持

如遇问题请查看：
- [WordPress插件修复指南](WordPress插件修复指南.md)
- [问题诊断报告](WordPress问题诊断报告.md)
- [项目汇报](汇报.md)

---
**部署成功后，您就可以开始使用这个强大的WordPress软文发布中间件了！** 🎉