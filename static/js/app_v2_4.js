// 文章发布系统 V2.4 - 前端脚本
// 功能优化版本，增加代码模式、发布历史面板及审核开关优化

// 全局变量
let publishHistory = JSON.parse(localStorage.getItem('publishHistory') || '[]');
let quillEditor = null;
let currentMode = 'edit'; // edit, code, preview
let currentUser = null; // 当前登录用户信息
let monthlyCount = 0; // 本月发布数量

// DOM元素
const publishForm = document.getElementById('publishForm');
const titleInput = document.getElementById('title');
const submitBtn = document.getElementById('submitBtn');
const messageDiv = document.getElementById('message');
const codeEditor = document.getElementById('codeEditor'); // V2.4新增

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
    
    // V2.4新增：加载发布历史
    loadPublishHistory();
    
    // 定期刷新统计数据和历史
    setInterval(loadMonthlyStats, 300000); // 每5分钟刷新一次
    setInterval(loadPublishHistory, 600000); // 每10分钟刷新一次历史
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

// V2.4新增：加载发布历史
async function loadPublishHistory() {
    const historyContent = document.getElementById('historyContent');
    
    try {
        const response = await fetch('/api/publish/history?limit=20');
        if (response.ok) {
            const result = await response.json();
            if (result.status === 'success') {
                displayPublishHistory(result.posts);
            } else {
                console.error('发布历史获取失败:', result.message);
                displayHistoryError('发布历史获取失败: ' + result.message);
            }
        } else if (response.status === 401) {
            // 会话过期，重定向到登录页
            window.location.href = '/login';
        } else {
            console.error('发布历史请求失败:', response.status);
            displayHistoryError('发布历史请求失败');
        }
    } catch (error) {
        console.error('发布历史加载异常:', error);
        displayHistoryError('网络连接失败');
    }
}

// V2.4新增：显示发布历史
function displayPublishHistory(posts) {
    const historyContent = document.getElementById('historyContent');
    
    if (!posts || posts.length === 0) {
        historyContent.innerHTML = `
            <div class="history-empty">
                📝 暂无发布历史
                <div style="margin-top: 10px; font-size: 0.9rem;">
                    发布第一篇文章后，历史记录将显示在这里
                </div>
            </div>
        `;
        return;
    }
    
    const historyHtml = posts.map(post => {
        const date = new Date(post.date);
        const formattedDate = date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const statusText = getStatusText(post.status);
        const statusClass = getStatusClass(post.status);
        
        return `
            <div class="history-item">
                <div class="history-item-left">
                    <div class="history-item-title">${post.title?.rendered || '无标题'}</div>
                    <div class="history-item-meta">
                        📅 ${formattedDate} | ID: ${post.id}
                    </div>
                </div>
                <div class="history-item-right">
                    <span class="status-badge ${statusClass}">${statusText}</span>
                    ${post.link ? `<a href="${post.link}" target="_blank" class="btn btn-secondary" style="padding: 4px 8px; font-size: 0.8rem;">🔗 查看</a>` : ''}
                </div>
            </div>
        `;
    }).join('');
    
    historyContent.innerHTML = `<div class="history-list">${historyHtml}</div>`;
}

// V2.4新增：获取状态文本
function getStatusText(status) {
    const statusMap = {
        'publish': '已发布',
        'pending': '待审核',
        'draft': '草稿',
        'private': '私有',
        'trash': '已删除'
    };
    return statusMap[status] || status;
}

// V2.4新增：获取状态样式类
function getStatusClass(status) {
    const classMap = {
        'publish': 'status-publish',
        'pending': 'status-pending',
        'draft': 'status-draft',
        'private': 'status-draft',
        'trash': 'status-draft'
    };
    return classMap[status] || 'status-draft';
}

// V2.4新增：显示历史加载错误
function displayHistoryError(message) {
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = `
        <div class="history-empty">
            ❌ ${message}
            <div style="margin-top: 10px;">
                <button onclick="loadPublishHistory()" class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.8rem;">
                    🔄 重试
                </button>
            </div>
        </div>
    `;
}

// V2.4新增：刷新发布历史
function refreshHistory() {
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = `
        <div class="history-loading">
            <div class="spinner" style="display: inline-block; border-color: #667eea; border-top-color: transparent;"></div>
            <span style="margin-left: 10px;">正在刷新发布历史...</span>
        </div>
    `;
    loadPublishHistory();
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
            localStorage.removeItem('formData_v2_4');
            
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
        placeholder: '请输入文章内容...\n\n支持富文本格式：\n• 粗体、斜体、下划线\n• 标题、列表、引用\n• 链接、图片插入\n• 文字颜色、对齐方式\n\n内容将通过百度AI进行审核（如已启用）'
    });

    // 监听编辑器内容变化
    quillEditor.on('text-change', function() {
        updateCharCount();
        saveFormData();
        updatePreview();
        syncToCodeEditor(); // V2.4新增：同步到代码编辑器
    });
    
    // V2.4新增：监听代码编辑器变化
    codeEditor.addEventListener('input', function() {
        updateCharCount();
        saveFormData();
        updatePreview();
        syncToRichEditor(); // 同步到富文本编辑器
    });
}

// V2.4新增：切换编辑模式（编辑/代码/预览）
function switchMode(mode) {
    const editBtn = document.querySelector('.toolbar-btn[onclick="switchMode(\'edit\')"]');
    const codeBtn = document.querySelector('.toolbar-btn[onclick="switchMode(\'code\')"]');
    const previewBtn = document.querySelector('.toolbar-btn[onclick="switchMode(\'preview\')"]');
    const richEditor = document.getElementById('richEditor');
    const codeEditorElement = document.getElementById('codeEditor');
    const previewContainer = document.getElementById('previewContainer');
    
    // 重置所有按钮状态
    editBtn.classList.remove('active');
    codeBtn.classList.remove('active');
    previewBtn.classList.remove('active');
    
    // 隐藏所有编辑器
    richEditor.style.display = 'none';
    codeEditorElement.style.display = 'none';
    previewContainer.classList.remove('show');
    
    currentMode = mode;
    
    if (mode === 'edit') {
        editBtn.classList.add('active');
        richEditor.style.display = 'block';
    } else if (mode === 'code') {
        codeBtn.classList.add('active');
        codeEditorElement.style.display = 'block';
        // 同步富文本编辑器内容到代码编辑器
        syncToCodeEditor();
    } else if (mode === 'preview') {
        previewBtn.classList.add('active');
        previewContainer.classList.add('show');
        updatePreview();
    }
}

// V2.4新增：同步富文本编辑器内容到代码编辑器
function syncToCodeEditor() {
    if (currentMode === 'code' && quillEditor) {
        const htmlContent = quillEditor.root.innerHTML;
        // 移除Quill默认的空段落标签
        const cleanContent = htmlContent === '<p><br></p>' ? '' : htmlContent;
        codeEditor.value = cleanContent;
    }
}

// V2.4新增：同步代码编辑器内容到富文本编辑器
function syncToRichEditor() {
    if (currentMode === 'code' && quillEditor) {
        const htmlContent = codeEditor.value;
        try {
            // 使用Quill的clipboard模块来安全地插入HTML
            const delta = quillEditor.clipboard.convert(htmlContent);
            quillEditor.setContents(delta);
        } catch (error) {
            console.warn('HTML内容同步失败:', error);
            // 如果HTML格式有问题，直接设置文本内容
            quillEditor.setText(htmlContent);
        }
    }
}

// 更新预览内容
function updatePreview() {
    if (currentMode === 'preview') {
        const title = titleInput.value || '文章标题预览';
        let content = '';
        
        if (currentMode === 'code') {
            content = codeEditor.value || '文章内容预览...';
        } else {
            content = quillEditor.root.innerHTML || '文章内容预览...';
        }
        
        document.getElementById('previewTitle').textContent = title;
        document.getElementById('previewContent').innerHTML = content;
    }
}

// 清空内容
function clearContent() {
    if (confirm('确定要清空编辑器内容吗？')) {
        if (currentMode === 'code') {
            codeEditor.value = '';
        } else {
            quillEditor.setContents([]);
        }
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

<p>更多相关信息和背景介绍。</p>`,

        'HTML代码模板': `<!-- HTML代码模板 -->
<div class="article-container">
    <header class="article-header">
        <h1>文章标题</h1>
        <p class="article-meta">发布时间：${new Date().toLocaleDateString()}</p>
    </header>
    
    <main class="article-content">
        <section>
            <h2>章节标题</h2>
            <p>这里是段落内容。支持<strong>粗体</strong>、<em>斜体</em>和<u>下划线</u>格式。</p>
            
            <ul>
                <li>列表项目一</li>
                <li>列表项目二</li>
                <li>列表项目三</li>
            </ul>
        </section>
        
        <section>
            <h3>子章节</h3>
            <blockquote>
                <p>这是一个引用块，用于突出重要内容。</p>
            </blockquote>
            
            <p>更多内容描述...</p>
        </section>
    </main>
    
    <footer class="article-footer">
        <p>文章结尾或版权信息</p>
    </footer>
</div>`
    };
    
    const templateNames = Object.keys(templates);
    const selectedTemplate = prompt(`请选择模板：\n${templateNames.map((name, index) => `${index + 1}. ${name}`).join('\n')}\n\n请输入数字选择：`);
    
    if (selectedTemplate && selectedTemplate >= 1 && selectedTemplate <= templateNames.length) {
        const templateName = templateNames[selectedTemplate - 1];
        const templateContent = templates[templateName];
        
        // 根据当前模式插入模板内容
        if (currentMode === 'code') {
            codeEditor.value = templateContent;
            syncToRichEditor();
        } else {
            const delta = quillEditor.clipboard.convert(templateContent);
            quillEditor.setContents(delta);
            syncToCodeEditor();
        }
        
        showMessage(`已插入"${templateName}"模板`, 'success');
        updateCharCount();
        saveFormData();
    }
}

// 处理表单提交
async function handleFormSubmit(event) {
    event.preventDefault();
    
    // 获取内容（根据当前模式）
    let content = '';
    if (currentMode === 'code') {
        content = codeEditor.value.trim();
    } else {
        content = quillEditor.root.innerHTML.trim();
    }
    
    const formData = {
        title: titleInput.value.trim(),
        content: content,
        publish_type: 'normal' // 普通发布，随机分配栏目
        // V2.4版本：不再需要author_token，通过登录状态验证
    };
    
    // 表单验证
    if (!validateForm(formData)) {
        return;
    }
    
    // 显示加载状态
    setLoadingState(true, 'normal');
    
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
        handlePublishResponse(result, response.status, 'normal');
        
        // 保存到历史记录
        saveToHistory(formData, result, response.status);
        
        // 发布成功后更新本月统计和历史
        if (result.status === 'success') {
            monthlyCount += 1;
            updateMonthlyDisplay(monthlyCount, new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit' }));
            // 延迟刷新历史，给WordPress一些时间处理
            setTimeout(loadPublishHistory, 2000);
        }
        
    } catch (error) {
        console.error('发布失败:', error);
        showMessage('网络错误，请检查服务器连接', 'error');
        
        // 保存错误到历史记录
        saveToHistory(formData, { status: 'error', message: '网络连接失败' }, 0);
    } finally {
        setLoadingState(false, 'normal');
    }
}

// 新增：发布到头条功能
async function publishToHeadline() {
    // 获取内容（根据当前模式）
    let content = '';
    if (currentMode === 'code') {
        content = codeEditor.value.trim();
    } else {
        content = quillEditor.root.innerHTML.trim();
    }
    
    const formData = {
        title: titleInput.value.trim(),
        content: content,
        publish_type: 'headline' // 头条发布，分配到ID=16035，草稿状态
    };
    
    // 表单验证
    if (!validateForm(formData)) {
        return;
    }
    
    // 显示加载状态
    setLoadingState(true, 'headline');
    
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
        handlePublishResponse(result, response.status, 'headline');
        
        // 保存到历史记录
        saveToHistory(formData, result, response.status);
        
        // 头条文章不计入月度统计，但需要刷新历史
        if (result.status === 'success') {
            setTimeout(loadPublishHistory, 2000);
        }
        
    } catch (error) {
        console.error('发布到头条失败:', error);
        showMessage('网络错误，请检查服务器连接', 'error');
        
        // 保存错误到历史记录
        saveToHistory(formData, { status: 'error', message: '网络连接失败' }, 0);
    } finally {
        setLoadingState(false, 'headline');
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
        if (currentMode === 'code') {
            codeEditor.focus();
        } else {
            quillEditor.focus();
        }
        return false;
    }
    
    if (data.title.length > 200) {
        showMessage('标题长度不能超过200个字符', 'warning');
        titleInput.focus();
        return false;
    }
    
    // 计算内容长度（根据模式）
    let textLength = 0;
    if (currentMode === 'code') {
        textLength = data.content.length;
    } else {
        textLength = quillEditor.getText().length;
    }
    
    if (textLength > 50000) {
        showMessage('内容长度不能超过50000个字符', 'warning');
        if (currentMode === 'code') {
            codeEditor.focus();
        } else {
            quillEditor.focus();
        }
        return false;
    }
    
    return true;
}

// 处理发布响应 - 适配V2.5格式，支持头条发布
function handlePublishResponse(result, status, publishType = 'normal') {
    if (result.status === 'success') {
        let message = '';
        
        if (publishType === 'headline') {
            message = `📋 头条文章保存成功！文章ID: ${result.post_id || '未知'}（已保存为草稿）`;
        } else {
            message = `📤 文章发布成功！文章ID: ${result.post_id || '未知'}`;
        }
        
        // V2.4新增：显示AI审核状态
        if (result.audit_result && result.audit_result.ai_check_disabled) {
            message += '（AI审核已禁用）';
        }
        
        showMessage(message, 'success');
        
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
    
    let auditMessage = '';
    if (auditResult.ai_check_disabled) {
        auditMessage = '⚠️ AI审核已禁用，内容直接发布';
    } else {
        auditMessage = `✅ 审核状态: ${auditResult.conclusion_type === 1 ? '审核通过' : '审核未通过'}`;
    }
    
    auditDiv.innerHTML = `
        <h4>审核结果</h4>
        <p>${auditMessage}</p>
        <p>${auditResult.message || ''}</p>
    `;
    
    messageDiv.appendChild(auditDiv);
}

// 重置表单
function resetForm() {
    titleInput.value = '';
    if (currentMode === 'code') {
        codeEditor.value = '';
    } else {
        quillEditor.setContents([]);
    }
    clearFormData();
    updateCharCount();
    showMessage('表单已重置', 'success');
}

// 保存草稿
function saveDraft() {
    saveFormData();
    showMessage('草稿已保存到本地', 'success');
}

// 设置加载状态 - 支持不同按钮类型
function setLoadingState(loading, buttonType = 'normal') {
    const submitBtn = document.getElementById('submitBtn');
    const headlineBtn = document.getElementById('headlineBtn');
    
    if (buttonType === 'normal') {
        if (loading) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '📤 发布中... <span class="loading"><span class="spinner"></span></span>';
            // 禁用头条按钮防止重复提交
            headlineBtn.disabled = true;
        } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '📤 发布文章';
            headlineBtn.disabled = false;
        }
    } else if (buttonType === 'headline') {
        if (loading) {
            headlineBtn.disabled = true;
            headlineBtn.innerHTML = '📋 保存中... <span class="loading"><span class="spinner"></span></span>';
            // 禁用普通发布按钮防止重复提交
            submitBtn.disabled = true;
        } else {
            headlineBtn.disabled = false;
            headlineBtn.innerHTML = '📋 发布到头条';
            submitBtn.disabled = false;
        }
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
    let content = '';
    if (currentMode === 'code') {
        content = codeEditor.value;
    } else if (quillEditor) {
        content = quillEditor.root.innerHTML;
    }
    
    const formData = {
        title: titleInput.value,
        content: content,
        mode: currentMode // V2.4新增：保存当前编辑模式
    };
    localStorage.setItem('formData_v2_4', JSON.stringify(formData));
}

// 从localStorage恢复表单数据
function restoreFormData() {
    const savedData = localStorage.getItem('formData_v2_4');
    if (savedData) {
        try {
            const formData = JSON.parse(savedData);
            titleInput.value = formData.title || '';
            
            if (formData.content) {
                if (formData.mode === 'code') {
                    // 恢复代码模式
                    codeEditor.value = formData.content;
                    switchMode('code');
                } else {
                    // 恢复富文本模式
                    const delta = quillEditor.clipboard.convert(formData.content);
                    quillEditor.setContents(delta);
                }
            }
            updateCharCount();
        } catch (error) {
            console.error('恢复表单数据失败:', error);
        }
    }
}

// 清空表单数据
function clearFormData() {
    localStorage.removeItem('formData_v2_4');
}

// 绑定表单数据保存事件
function bindFormDataSaving() {
    titleInput.addEventListener('input', saveFormData);
}

// 字符计数功能
function updateCharCount() {
    const titleCount = titleInput.value.length;
    let contentCount = 0;
    
    // 根据当前模式计算内容长度
    if (currentMode === 'code') {
        contentCount = codeEditor.value.length;
    } else if (quillEditor) {
        contentCount = quillEditor.getText().length;
    }
    
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
            switchMode(currentMode === 'preview' ? 'edit' : 'preview');
        }
        
        // Ctrl+Shift+C 切换代码模式
        if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'C') {
            event.preventDefault();
            switchMode(currentMode === 'code' ? 'edit' : 'code');
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
window.refreshHistory = refreshHistory;
window.publishToHeadline = publishToHeadline; // 新增：发布到头条功能