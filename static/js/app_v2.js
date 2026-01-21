// WordPress软文发布中间件 V2.1 - 前端脚本
// 支持富文本编辑器和配置管理

// 全局变量
let publishHistory = JSON.parse(localStorage.getItem('publishHistory') || '[]');
let quillEditor = null;
let currentMode = 'edit'; // edit 或 preview

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
    // 初始化富文本编辑器
    initializeEditor();
    
    // 绑定表单提交事件
    publishForm.addEventListener('submit', handleFormSubmit);
    
    // 检查服务状态
    checkServiceStatus();
    
    // 加载发布历史
    loadPublishHistory();
    
    // 定期检查服务状态
    setInterval(checkServiceStatus, 30000); // 每30秒检查一次
    
    // 从localStorage恢复表单数据
    restoreFormData();
    
    // 绑定输入事件保存表单数据
    bindFormDataSaving();
    
    // 绑定快捷键
    bindKeyboardShortcuts();
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
        // 不再需要author_token，后端自动使用配置的令牌
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
        
        const result = await response.json();
        
        // 处理响应
        handlePublishResponse(result, response.status);
        
        // 保存到历史记录
        saveToHistory(formData, result, response.status);
        
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

// 处理发布响应 - 适配V2.1格式
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
        submitBtn.innerHTML = '<span class="loading"></span> 发布中...';
    } else {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '发布文章';
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

// 检查服务状态
async function checkServiceStatus() {
    try {
        const response = await fetch('/health');
        const result = await response.json();
        
        updateServiceStatus(true, result);
        
    } catch (error) {
        console.error('服务状态检查失败:', error);
        updateServiceStatus(false);
    }
}

// 更新服务状态显示
function updateServiceStatus(online, data = null) {
    const statusElement = document.getElementById('serviceStatus');
    const statusText = statusElement.querySelector('span:last-child');
    
    if (online) {
        statusElement.className = 'status-indicator status-online';
        statusText.textContent = 'V2.1服务正常运行';
        
        if (data && data.timestamp) {
            const time = new Date(data.timestamp).toLocaleTimeString();
            statusText.textContent += ` (${time})`;
        }
    } else {
        statusElement.className = 'status-indicator status-offline';
        statusText.textContent = '服务连接失败';
    }
}

// 保存到历史记录
function saveToHistory(formData, result, status) {
    const historyItem = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        title: formData.title,
        success: result.status === 'success',
        message: result.message,
        postId: result.post_id,
        status: status
    };
    
    publishHistory.unshift(historyItem);
    
    // 只保留最近50条记录
    if (publishHistory.length > 50) {
        publishHistory = publishHistory.slice(0, 50);
    }
    
    localStorage.setItem('publishHistory', JSON.stringify(publishHistory));
    loadPublishHistory();
}

// 加载发布历史
function loadPublishHistory() {
    const historyContainer = document.getElementById('historyList');
    
    if (publishHistory.length === 0) {
        historyContainer.innerHTML = '<p style="color: #718096; text-align: center;">暂无发布记录</p>';
        return;
    }
    
    const historyHtml = publishHistory.slice(0, 10).map(item => {
        const time = new Date(item.timestamp).toLocaleString();
        const statusClass = item.success ? 'success' : 'error';
        const statusText = item.success ? '✅ 发布成功' : '❌ 发布失败';
        
        return `
            <div class="history-item ${statusClass}">
                <div class="history-time">${time}</div>
                <div class="history-title">${item.title}</div>
                <div class="history-status">${statusText}</div>
                ${item.postId ? `<div style="font-size: 0.8rem; color: #718096;">ID: ${item.postId}</div>` : ''}
            </div>
        `;
    }).join('');
    
    historyContainer.innerHTML = historyHtml;
}

// 清空历史记录
function clearHistory() {
    if (confirm('确定要清空所有发布历史记录吗？')) {
        publishHistory = [];
        localStorage.removeItem('publishHistory');
        loadPublishHistory();
        showMessage('历史记录已清空', 'success');
    }
}

// 保存表单数据到localStorage
function saveFormData() {
    const formData = {
        title: titleInput.value,
        content: quillEditor.root.innerHTML
    };
    localStorage.setItem('formData_v2', JSON.stringify(formData));
}

// 从localStorage恢复表单数据
function restoreFormData() {
    const savedData = localStorage.getItem('formData_v2');
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
    localStorage.removeItem('formData_v2');
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
    });
}

// 导出历史记录
function exportHistory() {
    if (publishHistory.length === 0) {
        showMessage('没有历史记录可导出', 'warning');
        return;
    }
    
    const csvContent = [
        ['时间', '标题', '状态', '消息', '文章ID'].join(','),
        ...publishHistory.map(item => [
            new Date(item.timestamp).toLocaleString(),
            `"${item.title.replace(/"/g, '""')}"`,
            item.success ? '成功' : '失败',
            `"${item.message.replace(/"/g, '""')}"`,
            item.postId || ''
        ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `发布历史_V2.1_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}