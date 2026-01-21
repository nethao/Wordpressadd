# WordPress插件修复指南

## 🎯 问题确认
根据错误信息，问题出现在：
```
文件：G:\xampp\htdocs\wp-content\plugins\wp-adv-manager\wp-adv-manager.php
行号：164
错误：Call to undefined method WP_REST_Request::get_path()
```

## 🛠️ 修复步骤

### 步骤1：打开插件文件
使用文本编辑器打开：
```
G:\xampp\htdocs\wp-content\plugins\wp-adv-manager\wp-adv-manager.php
```

### 步骤2：找到第164行
查找类似这样的代码：
```php
$path = $request->get_path();
```

### 步骤3：替换为正确的方法
将第164行替换为以下任一方案：

#### 方案A：使用get_route()方法
```php
$path = $request->get_route();
```

#### 方案B：使用兼容性检查
```php
if (method_exists($request, 'get_path')) {
    $path = $request->get_path();
} else {
    $path = $request->get_route();
}
```

#### 方案C：直接获取路径
```php
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
```

### 步骤4：保存文件并测试

## 🚀 快速修复脚本

如果您想要快速修复，可以创建一个PHP脚本：

```php
<?php
// 快速修复脚本 - fix_plugin.php
$file_path = 'G:\xampp\htdocs\wp-content\plugins\wp-adv-manager\wp-adv-manager.php';

// 读取文件内容
$content = file_get_contents($file_path);

// 替换错误的方法调用
$content = str_replace(
    '$request->get_path()',
    '$request->get_route()',
    $content
);

// 写回文件
file_put_contents($file_path, $content);

echo "插件修复完成！\n";
?>
```

## 🧪 验证修复

修复后，运行Python测试：
```bash
# 关闭测试模式
# 在.env中设置：TEST_MODE=false

# 运行测试
python test_v2.py
```

## 📋 备用方案

如果插件修复困难，可以临时使用标准WordPress端点：

### 修改Python代码使用posts端点
在 `main_v2.py` 中找到：
```python
url = f"{self.api_base}/adv_posts"
```

替换为：
```python
url = f"{self.api_base}/posts"
```

这样就使用标准的WordPress文章端点，绕过自定义插件。

## ⚠️ 注意事项

1. **备份插件文件**：修改前先备份原文件
2. **测试环境**：建议先在测试环境中验证修复
3. **插件更新**：插件更新时可能会覆盖修改，需要重新修复

## 🎯 预期结果

修复后应该看到：
```
✅ WordPress连接成功
📄 文章发布成功  
🎉 Python认证正常工作
```