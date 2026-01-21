// 文章发布系统 V2.3 - 前端脚本
// Web UI深度重构版本，支持本月发布统计和极简布局

// 全局变量
let publishHistory = JSON.parse(localStorage.getItem('publishHistory') || '[]');
let quillEditor = null;
let currentMode = 'edit'; // edit 或 preview
let currentUser = null; // 当前登录用户信息
let monthlyCount = 0; // 本月发布数量

// DOM元素
const publishForm = document.getElementById('publishForm');
const titleInput = document.getElementById('title');
const submitBtn = document.getElementById('submitBtn');
const messageDiv = document.getElementById('message');

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    // 获取用户信息
    loadUserInfo();
    
    // 加载本月统计
    loadMonthlyStats();
    
    // 初始化富文本编辑器
    initializeEditor();
    
    // 绑定表单提交事件
    publishForm.addEventListener('submit', handleFormSubmit);
    
    // 从localStorage恢复表单数据
    restoreFormData();
    
    // 绑定输入事件保存表单数据
    bindFormDataSaving();
    
    // 绑定快捷键
    bindKeyboardShortcuts();
    
    // 定期刷新统计数据
    setInterval(loadMonthlyStats, 300000); // 每5分钟刷新一次
}

// 获取用户信息
async function loadUserInfo() {
    try {
        const response = await fetch('/api/user');
        if (response.ok) {
            const result = await response.json();
            if (result.status === 'success') {
                currentUser = result.user;
                updateUserDisplay();
            }
        } else if (response.status === 401) {
            // 未登录，重定向到登录页
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('获取用户信息失败:', error);
        // 网络错误时也重定向到登录页
        window.location.href = '/login';
    }
}

// 更新用户信息显示
function updateUserDisplay() {
    if (!currentUser) return;
    
    // 更新用户名和角色显示
    const usernameElement = document.getElementById('username');
    const userRoleElement = document.getElementById('userRole');
    const adminLinkElement = document.getElementById('adminLink');
    
    if (usernameElement) {
        usernameElement.textContent = currentUser.username;
    }
    
    if (userRoleElement) {
        const roleText = currentUser.role === 'admin' ? '管理员' : '外包人员';
        userRoleElement.textContent = roleText;
    }
    
    // 只有管理员才显示系统管理链接
    if (adminLinkElement && currentUser.role === 'admin') {
        adminLinkElement.style.display = 'block';
    }
}

// 加载本月发布统计
async function loadMonthlyStats() {
    try {
        const response = await fetch('/api/stats/monthly');
        if (response.ok) {
            const result = await response.json();
            if (result.status === 'success') {
                monthlyCount = result.monthly_count;
                updateMonthlyDisplay(result.monthly_count, result.current_month);
            } else {
                console.error('统计数据获取失败:', result.message);
                updateMonthlyDisplay(0, '未知');
            }
        } else if (response.status === 401) {
            // 会话过期，重定向到登录页
            window.location.href = '/login';
        } else {
            console.error('统计数据请求失败:', response.status);
            updateMonthlyDisplay(0, '未知');
        }
    } catch (error) {
        console.error('统计数据加载异常:', error);
        updateMonthlyDisplay(0, '未知');
    }
}

// 更新本月统计显示
function updateMonthlyDisplay(count, month) {
    const monthlyCountElement = document.getElementById('monthlyCount');
    if (monthlyCountElement) {
        monthlyCountElement.textContent = count;
    }
    
    // 可以在这里添加月份显示，如果需要的话
    console.log(`📊 ${month}已发布: ${count} 篇稿件`);
}

// 用户登出
async function logout() {
    if (!confirm('确定要退出登录吗？')) {
        return;
    }
    
    try {
        const response = await fetch('/logout', {
            method: 'POST'
        });
        
        if (response.ok) {
            // 清除本地数据
            localStorage.removeItem('formData_v2_3');
            
            // 重定向到登录页
            window.location.href = '/login';
        } else {
            showMessage('登出失败，请重试', 'error');
        }
    } catch (error) {
        console.error('登出失败:', error);
        showMessage('网络错误，请重试', 'error');
    }
}

// 初始化富文本编辑器
function initializeEditor() {
    const toolbarOptions = [
        ['bold', 'italic', 'underline', 'strike'],        // 文本格式
        ['blockquote', 'code-block'],                     // 引用和代码
        [{ 'header': 1 }, { 'header': 2 }],              // 标题
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],    // 列表
        [{ 'script': 'sub'}, { 'script': 'super' }],     // 上下标
        [{ 'indent': '-1'}, { 'indent': '+1' }],         // 缩进
        [{ 'direction': 'rtl' }],                         // 文本方向
        [{ 'size': ['small', false, 'large', 'huge'] }], // 字体大小
        [{ 'header': [1, 2, 3, 4, 5, 6, false] }],       // 标题级别
        [{ 'color': [] }, { 'background': [] }],          // 字体颜色和背景色
        [{ 'font': [] }],                                 // 字体
        [{ 'align': [] }],                                // 对齐方式
        ['clean'],                                        // 清除格式
        ['link', 'image']                                 // 链接和图片
    ];

    quillEditor = new Quill('#editor', {
        theme: 'snow',
        modules: {
            toolbar: toolbarOptions
        },
        placeholder: '请输入文章内容...\n\n支持富文本格式：\n• 粗体、斜体、下划线\n• 标题、列表、引用\n• 链接、图片插入\n• 文字颜色、对齐方式\n\n内容将通过百度AI进行审核'
    });

    // 监听编辑器内容变化
    quillEditor.on('text-change', function() {
        updateCharCount();
        saveFormData();
        updatePreview();
    });
}

// 切换编辑/预览模式
function switchMode(mode) {
    const editBtn = document.querySelector('.toolbar-btn[onclick="switchMode(\'edit\')"]');
    const previewBtn = document.querySelector('.toolbar-btn[onclick="switchMode(\'preview\')"]');
    const editorContainer = document.querySelector('.editor-container');
    const previewContainer = document.getElementById('previewContainer');
    
    currentMode = mode;
    
    if (mode === 'edit') {
        editBtn.classList.add('active');
        previewBtn.classList.remove('active');
        editorContainer.style.display = 'block';
        previewContainer.classList.remove('show');
    } else {
        editBtn.classList.remove('active');
        previewBtn.classList.add('active');
        editorContainer.style.display = 'none';
        previewContainer.classList.add('show');
        updatePreview();
    }
}

// 更新预览内容
function updatePreview() {
    if (currentMode === 'preview') {
        const title = titleInput.value || '文章标题预览';
        const content = quillEditor.root.innerHTML || '文章内容预览...';
        
        document.getElementById('previewTitle').textContent = title;
        document.getElementById('previewContent').innerHTML = content;
    }
}

// 清空内容
function clearContent() {
    if (confirm('确定要清空编辑器内容吗？')) {
        quillEditor.setContents([]);
        updateCharCount();
        saveFormData();
    }
}

// 插入模板
function insertTemplate() {
    const templates = {
        '基础文章模板': `<h2>文章标题</h2>
<p>这里是文章的开头段落，简要介绍文章主题。</p>

<h3>主要内容</h3>
<p>这里是文章的主要内容部分。</p>
<ul>
<li>要点一</li>
<li>要点二</li>
<li>要点三</li>
</ul>

<h3>总结</h3>
<p>这里是文章的总结部分。</p>`,
        
        '产品介绍模板': `<h2>产品概述</h2>
<p>产品的基本介绍和特点。</p>

<h3>主要功能</h3>
<ul>
<li><strong>功能一：</strong>功能描述</li>
<li><strong>功能二：</strong>功能描述</li>
<li><strong>功能三：</strong>功能描述</li>
</ul>

<h3>使用场景</h3>
<p>适用的使用场景和目标用户。</p>

<h3>联系我们</h3>
<p>如需了解更多信息，请联系我们。</p>`,
        
        '新闻资讯模板': `<p><em>发布时间：${new Date().toLocaleDateString()}</em></p>

<h2>新闻标题</h2>
<p>新闻导语，简要概括新闻要点。</p>

<h3>详细内容</h3>
<p>新闻的详细内容描述。</p>

<blockquote>
<p>重要引用或声明</p>
</blockquote>

<p>更多相关信息和背景介绍。</p>`
    };
    
    const templateNames = Object.keys(templates);
    const selectedTemplate = prompt(`请选择模板：\n${templateNames.map((name, index) => `${index + 1}. ${name}`).join('\n')}\n\n请输入数字选择：`);
    
    if (selectedTemplate && selectedTemplate >= 1 && selectedTemplate <= templateNames.length) {
        const templateName = templateNames[selectedTemplate - 1];
        const templateContent = templates[templateName];
        
        // 插入模板内容
        const delta = quillEditor.clipboard.convert(templateContent);
        quillEditor.setContents(delta);
        
        showMessage(`已插入"${templateName}"模板`, 'success');
    }
}

// 处理表单提交
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = {
        title: titleInput.value.trim(),
        content: quillEditor.root.innerHTML.trim()
        // V2.3版本：不再需要author_token，通过登录状态验证
    };
    
    // 表单验证
    if (!validateForm(formData)) {
        return;
    }
    
    // 显示加载状态
    setLoadingState(true);
    
    try {
        const response = await fetch('/publish', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (response.status === 401) {
            // 会话过期，重定向到登录页
            showMessage('登录已过期，请重新登录', 'error');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            return;
        }
        
        const result = await response.json();
        
        // 处理响应
        handlePublishResponse(result, response.status);
        
        // 保存到历史记录
        saveToHistory(formData, result, response.status);
        
        // 发布成功后更新本月统计
        if (result.status === 'success') {
            monthlyCount += 1;
            updateMonthlyDisplay(monthlyCount, new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit' }));
        }
        
    } catch (error) {
        console.error('发布失败:', error);
        showMessage('网络错误，请检查服务器连接', 'error');
        
        // 保存错误到历史记录
        saveToHistory(formData, { status: 'error', message: '网络连接失败' }, 0);
    } finally {
        setLoadingState(false);
    }
}

// 表单验证
function validateForm(data) {
    if (!data.title) {
        showMessage('请输入文章标题', 'warning');
        titleInput.focus();
        return false;
    }
    
    if (!data.content || data.content === '<p><br></p>') {
        showMessage('请输入文章内容', 'warning');
        quillEditor.focus();
        return false;
    }
    
    if (data.title.length > 200) {
        showMessage('标题长度不能超过200个字符', 'warning');
        titleInput.focus();
        return false;
    }
    
    const textLength = quillEditor.getText().length;
    if (textLength > 50000) {
        showMessage('内容长度不能超过50000个字符', 'warning');
        quillEditor.focus();
        return false;
    }
    
    return true;
}

// 处理发布响应 - 适配V2.3格式
function handlePublishResponse(result, status) {
    if (result.status === 'success') {
        showMessage(`文章发布成功！文章ID: ${result.post_id || '未知'}`, 'success');
        
        // 清空表单
        resetForm();
        
        // 显示审核结果
        if (result.audit_result) {
            showAuditResult(result.audit_result);
        }
        
    } else {
        let errorMessage = result.message || '发布失败';
        
        // 如果是审核失败，显示详细信息
        if (result.violations && result.violations.length > 0) {
            showViolationDetails(result.violations);
        }
        
        showMessage(errorMessage, 'error');
    }
}

// 显示违规详情
function showViolationDetails(violations) {
    const violationHtml = violations.map(violation => `
        <div class="violation-item">
            <div class="violation-words">违规词汇: ${violation.违规词汇?.join(', ') || '未知'}</div>
            <div>违规类型: ${violation.违规类型 || '未知'}</div>
            <div>违规描述: ${violation.违规描述 || '无描述'}</div>
        </div>
    `).join('');
    
    const violationDiv = document.createElement('div');
    violationDiv.className = 'violation-details';
    violationDiv.innerHTML = `
        <h4>内容审核详情</h4>
        ${violationHtml}
    `;
    
    messageDiv.appendChild(violationDiv);
}

// 显示审核结果
function showAuditResult(auditResult) {
    const auditDiv = document.createElement('div');
    auditDiv.className = 'message success';
    auditDiv.innerHTML = `
        <h4>审核结果</h4>
        <p>审核状态: ${auditResult.conclusion_type === 1 ? '✅ 审核通过' : '❌ 审核未通过'}</p>
        <p>${auditResult.message || ''}</p>
    `;
    
    messageDiv.appendChild(auditDiv);
}

// 重置表单
function resetForm() {
    titleInput.value = '';
    quillEditor.setContents([]);
    clearFormData();
    updateCharCount();
    showMessage('表单已重置', 'success');
}

// 保存草稿
function saveDraft() {
    saveFormData();
    showMessage('草稿已保存到本地', 'success');
}

// 设置加载状态
function setLoadingState(loading) {
    if (loading) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '📤 发布中... <span class="loading"><span class="spinner"></span></span>';
    } else {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '📤 发布文章';
    }
}

// 显示消息
function showMessage(message, type = 'info') {
    messageDiv.innerHTML = `<div class="message ${type} show">${message}</div>`;
    
    // 3秒后自动隐藏成功消息
    if (type === 'success') {
        setTimeout(() => {
            const msgElement = messageDiv.querySelector('.message');
            if (msgElement) {
                msgElement.classList.remove('show');
            }
        }, 3000);
    }
}

// 保存到历史记录
function saveToHistory(formData, result, httpStatus) {
    const historyItem = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        title: formData.title,
        success: result.status === 'success',
        message: result.message,
        postId: result.post_id,
        status: httpStatus,
        user: currentUser ? currentUser.username : '未知用户'
    };
    
    publishHistory.unshift(historyItem);
    
    // 只保留最近50条记录
    if (publishHistory.length > 50) {
        publishHistory = publishHistory.slice(0, 50);
    }
    
    localStorage.setItem('publishHistory', JSON.stringify(publishHistory));
}

// 保存表单数据到localStorage
function saveFormData() {
    const formData = {
        title: titleInput.value,
        content: quillEditor.root.innerHTML
    };
    localStorage.setItem('formData_v2_3', JSON.stringify(formData));
}

// 从localStorage恢复表单数据
function restoreFormData() {
    const savedData = localStorage.getItem('formData_v2_3');
    if (savedData) {
        try {
            const formData = JSON.parse(savedData);
            titleInput.value = formData.title || '';
            if (formData.content) {
                const delta = quillEditor.clipboard.convert(formData.content);
                quillEditor.setContents(delta);
            }
            updateCharCount();
        } catch (error) {
            console.error('恢复表单数据失败:', error);
        }
    }
}

// 清空表单数据
function clearFormData() {
    localStorage.removeItem('formData_v2_3');
}

// 绑定表单数据保存事件
function bindFormDataSaving() {
    titleInput.addEventListener('input', saveFormData);
}

// 字符计数功能
function updateCharCount() {
    const titleCount = titleInput.value.length;
    const contentCount = quillEditor.getText().length;
    
    const titleCountElement = document.getElementById('titleCount');
    const contentCountElement = document.getElementById('contentCount');
    
    titleCountElement.textContent = `${titleCount}/200`;
    contentCountElement.textContent = `${contentCount}/50000`;
    
    // 超出限制时显示警告
    titleCountElement.className = 'char-count';
    contentCountElement.className = 'char-count';
    
    if (titleCount > 180) {
        titleCountElement.className += titleCount > 200 ? ' error' : ' warning';
    }
    
    if (contentCount > 45000) {
        contentCountElement.className += contentCount > 50000 ? ' error' : ' warning';
    }
}

// 绑定字符计数事件
titleInput.addEventListener('input', updateCharCount);

// 绑定快捷键
function bindKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl+Enter 快速发布
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            if (!submitBtn.disabled) {
                publishForm.dispatchEvent(new Event('submit'));
            }
        }
        
        // Ctrl+S 保存草稿
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
            event.preventDefault();
            saveDraft();
        }
        
        // Ctrl+P 切换预览
        if ((event.ctrlKey || event.metaKey) && event.key === 'p') {
            event.preventDefault();
            switchMode(currentMode === 'edit' ? 'preview' : 'edit');
        }
        
        // Ctrl+L 登出
        if ((event.ctrlKey || event.metaKey) && event.key === 'l') {
            event.preventDefault();
            logout();
        }
    });
}

// 全局函数，供HTML调用
window.logout = logout;
window.switchMode = switchMode;
window.clearContent = clearContent;
window.insertTemplate = insertTemplate;
window.resetForm = resetForm;
window.saveDraft = saveDraft;