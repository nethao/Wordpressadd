# WordPress 软文发布代理 - 配置指南

## 🚨 发布失败的常见原因

### 1. 环境变量未配置
当前您的 `.env` 文件还是模板状态，需要填入真实配置：

```bash
# 当前配置（需要修改）
BAIDU_API_KEY=your_baidu_api_key_here  # ❌ 需要真实API密钥
BAIDU_SECRET_KEY=your_baidu_secret_key_here  # ❌ 需要真实密钥
WP_DOMAIN=your-wordpress-domain.com  # ❌ 需要真实域名
WP_USERNAME=your_wp_username  # ❌ 需要真实用户名
WP_APP_PASSWORD=your_wp_application_password  # ❌ 需要真实密码
VALID_AUTHOR_TOKENS=token1,token2,token3  # ❌ 需要设置真实令牌
```

## 📋 详细配置步骤

### 步骤1：配置百度AI（必需）

1. **注册百度智能云账号**
   - 访问：https://cloud.baidu.com/
   - 注册并完成实名认证

2. **创建文本内容审核应用**
   - 进入控制台：https://console.bce.baidu.com/ai/#/ai/antiporn/overview/index
   - 点击"立即使用" → "创建应用"
   - 应用名称：随意填写（如：软文审核）
   - 应用描述：随意填写
   - 创建成功后获取 API Key 和 Secret Key

3. **更新配置**
   ```bash
   BAIDU_API_KEY=你获取的API_Key
   BAIDU_SECRET_KEY=你获取的Secret_Key
   ```

### 步骤2：配置WordPress（必需）

1. **准备WordPress站点**
   - 确保WordPress版本 >= 5.0
   - 确保支持REST API（默认开启）

2. **创建应用密码**
   - 登录WordPress后台
   - 进入：用户 → 个人资料
   - 滚动到底部"应用密码"部分
   - 应用名称：填写"软文发布代理"
   - 点击"添加新应用密码"
   - 复制生成的密码（格式：xxxx xxxx xxxx xxxx）

3. **检查自定义文章类型**
   - 确保WordPress支持 `adv_posts` 文章类型
   - 如果没有，需要安装相关插件或修改代码

4. **更新配置**
   ```bash
   WP_DOMAIN=你的域名.com  # 不要包含 https://
   WP_USERNAME=你的WordPress用户名
   WP_APP_PASSWORD=刚才生成的应用密码
   ```

### 步骤3：设置作者令牌（必需）

```bash
# 设置允许发布的令牌（可以是任意字符串）
VALID_AUTHOR_TOKENS=abc123,def456,ghi789
```

## 🧪 测试配置

### 方法1：使用测试模式（推荐）

如果您暂时没有百度AI或WordPress配置，可以先使用测试模式：