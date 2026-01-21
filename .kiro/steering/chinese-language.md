---
inclusion: always
---

# 中文语言设置

## 语言要求
- 所有对话必须使用中文
- 所有代码注释必须使用中文
- 所有文档和说明必须使用中文
- 变量名和函数名可以使用英文，但注释必须是中文

## 代码注释规范
```javascript
// 这是一个示例函数，用于处理用户数据
function processUserData(userData) {
    // 验证用户输入数据
    if (!userData) {
        throw new Error('用户数据不能为空');
    }
    
    // 处理数据并返回结果
    return userData.map(item => {
        // 格式化每个数据项
        return {
            id: item.id,
            name: item.name.trim(), // 去除名称前后空格
            email: item.email.toLowerCase() // 转换邮箱为小写
        };
    });
}
```

## 响应格式
- 技术解释使用中文
- 错误信息使用中文
- 建议和推荐使用中文
- 代码示例的注释使用中文