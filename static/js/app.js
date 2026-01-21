// 全局变量
let publishHistory = JSON.parse(localStorage.getItem('publishHistory') || '[]');

// DOM元素
const publishForm = document.getElementById('publishForm');
const titleInput = document.getElementById('title');
const contentInput = document.getElementById('content');
const authorTokenInput = document.getElementById('authorToken');
const submitBtn = document.getElementById('submitBtn');
const messageDiv = document.getElementById('message');

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
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
}

// 处理表单提交
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = {
        title: titleInput.value.trim(),
        content: contentInput.value.trim(),
        author_token: authorTokenInput.value.trim()
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
        saveToHistory(formData, { success: false, message: '网络连接失败' }, 0);
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
    
    if (!data.content) {
        showMessage('请输入文章内容', 'warning');
        contentInput.focus();
        return false;
    }
    
    if (!data.author_token) {
        showMessage('请输入作者令牌', 'warning');
        authorTokenInput.focus();
        return false;
    }
    
    if (data.title.length > 200) {
        showMessage('标题长度不能超过200个字符', 'warning');
        titleInput.focus();
        return false;
    }
    
    if (data.content.length > 50000) {
        showMessage('内容长度不能超过50000个字符', 'warning');
        contentInput.focus();
        return false;
    }
    
    return true;
}

// 处理发布响应
function handlePublishResponse(result, status) {
    if (result.success) {
        showMessage(`文章发布成功！文章ID: ${result.post_id || '未知'}`, 'success');
        
        // 清空表单
        publishForm.reset();
        clearFormData();
        
        // 显示审核结果
        if (result.audit_result) {
            showAuditResult(result.audit_result);
        }
        
    } else {
        let errorMessage = result.message || '发布失败';
        
        // 如果是审核失败，显示详细信息
        if (result.audit_result && result.audit_result.violations) {
            errorMessage += '\n\n违规详情：';
            showViolationDetails(result.audit_result.violations);
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
    const statusDot = statusElement.querySelector('.status-dot');
    const statusText = statusElement.querySelector('span:last-child');
    
    if (online) {
        statusElement.className = 'status-indicator status-online';
        statusText.textContent = '服务正常运行';
        
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
        success: result.success,
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
        content: contentInput.value,
        author_token: authorTokenInput.value
    };
    localStorage.setItem('formData', JSON.stringify(formData));
}

// 从localStorage恢复表单数据
function restoreFormData() {
    const savedData = localStorage.getItem('formData');
    if (savedData) {
        try {
            const formData = JSON.parse(savedData);
            titleInput.value = formData.title || '';
            contentInput.value = formData.content || '';
            authorTokenInput.value = formData.author_token || '';
        } catch (error) {
            console.error('恢复表单数据失败:', error);
        }
    }
}

// 清空表单数据
function clearFormData() {
    localStorage.removeItem('formData');
}

// 绑定表单数据保存事件
function bindFormDataSaving() {
    [titleInput, contentInput, authorTokenInput].forEach(input => {
        input.addEventListener('input', saveFormData);
    });
}

// 字符计数功能
function updateCharCount() {
    const titleCount = titleInput.value.length;
    const contentCount = contentInput.value.length;
    
    document.getElementById('titleCount').textContent = `${titleCount}/200`;
    document.getElementById('contentCount').textContent = `${contentCount}/50000`;
    
    // 超出限制时显示警告
    if (titleCount > 200) {
        document.getElementById('titleCount').style.color = '#e53e3e';
    } else {
        document.getElementById('titleCount').style.color = '#718096';
    }
    
    if (contentCount > 50000) {
        document.getElementById('contentCount').style.color = '#e53e3e';
    } else {
        document.getElementById('contentCount').style.color = '#718096';
    }
}

// 绑定字符计数事件
titleInput.addEventListener('input', updateCharCount);
contentInput.addEventListener('input', updateCharCount);

// 快捷键支持
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
        saveFormData();
        showMessage('草稿已保存', 'success');
    }
});

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
    link.setAttribute('download', `发布历史_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}