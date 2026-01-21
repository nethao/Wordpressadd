// 文章发布系统 V2.4 - 系统管理页面脚本
// 功能优化版本，增加代码模式、发布历史面板及审核开关优化

// 全局变量
let publishHistory = JSON.parse(localStorage.getItem('publishHistory') || '[]');
let currentConfig = {};
let currentUser = null; // 当前登录用户信息

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeAdmin();
});

// 初始化管理后台
function initializeAdmin() {
    // 获取用户信息
    loadUserInfo();
    
    loadStatistics();
    loadCurrentConfig();
    loadSystemLogs();
    loadPublishHistory();
    drawChart();
    
    // 定期刷新数据
    setInterval(refreshAll, 60000); // 每分钟刷新一次
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
                
                // 检查管理员权限
                if (currentUser.role !== 'admin') {
                    // 非管理员用户，重定向到发布页面
                    alert('您没有访问系统管理的权限');
                    window.location.href = '/';
                    return;
                }
            }
        } else if (response.status === 401) {
            // 未登录，重定向到登录页
            window.location.href = '/login';
        } else if (response.status === 403) {
            // 权限不足，重定向到发布页面
            alert('您没有访问系统管理的权限');
            window.location.href = '/';
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
    
    if (usernameElement) {
        usernameElement.textContent = currentUser.username;
    }
    
    if (userRoleElement) {
        const roleText = currentUser.role === 'admin' ? '管理员' : '外包人员';
        userRoleElement.textContent = roleText;
    }
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
            showConfigMessage('登出失败，请重试', 'error');
        }
    } catch (error) {
        console.error('登出失败:', error);
        showConfigMessage('网络错误，请重试', 'error');
    }
}

// 加载统计数据
function loadStatistics() {
    const total = publishHistory.length;
    const successful = publishHistory.filter(item => item.success).length;
    const successRate = total > 0 ? Math.round((successful / total) * 100) : 0;
    
    // 今日发布数
    const today = new Date().toDateString();
    const todayCount = publishHistory.filter(item => 
        new Date(item.timestamp).toDateString() === today
    ).length;
    
    // 审核拒绝数
    const rejectedCount = publishHistory.filter(item => 
        !item.success && (item.message.includes('审核') || item.message.includes('敏感'))
    ).length;

    document.getElementById('totalPublished').textContent = total;
    document.getElementById('successRate').textContent = successRate + '%';
    document.getElementById('todayPublished').textContent = todayCount;
    document.getElementById('auditRejected').textContent = rejectedCount;
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
                ${item.user ? `<div style="font-size: 0.8rem; color: #718096;">用户: ${item.user}</div>` : ''}
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
        loadStatistics();
        drawChart();
        showConfigMessage('历史记录已清空', 'success');
    }
}

// 导出历史记录
function exportHistory() {
    if (publishHistory.length === 0) {
        showConfigMessage('没有历史记录可导出', 'warning');
        return;
    }
    
    const csvContent = [
        ['时间', '标题', '状态', '消息', '文章ID', '用户'].join(','),
        ...publishHistory.map(item => [
            new Date(item.timestamp).toLocaleString(),
            `"${item.title.replace(/"/g, '""')}"`,
            item.success ? '成功' : '失败',
            `"${item.message.replace(/"/g, '""')}"`,
            item.postId || '',
            item.user || '未知用户'
        ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `发布历史_V2.3_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 加载当前配置
async function loadCurrentConfig() {
    try {
        const response = await fetch('/config');
        
        if (response.status === 401) {
            // 会话过期，重定向到登录页
            window.location.href = '/login';
            return;
        } else if (response.status === 403) {
            // 权限不足
            showConfigMessage('您没有访问配置的权限', 'error');
            return;
        }
        
        const result = await response.json();
        
        if (result.status === 'success' && result.config) {
            currentConfig = result.config;
            updateConfigForm(result.config);
            updateConfigStatus(result.config);
        } else {
            showConfigMessage('配置加载失败: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('配置加载失败:', error);
        showConfigMessage('配置加载失败: 网络错误', 'error');
    }
}

// 更新配置表单
function updateConfigForm(config) {
    // WordPress配置
    document.getElementById('wpDomain').value = config.wp_domain || '';
    document.getElementById('wpUsername').value = config.wp_username || '';
    // 密码字段显示占位符
    document.getElementById('wpAppPassword').placeholder = config.wp_app_password ? '已配置 (点击修改)' : '未配置';
    
    // 百度AI配置
    document.getElementById('baiduApiKey').placeholder = config.baidu_api_key ? '已配置 (点击修改)' : '未配置';
    document.getElementById('baiduSecretKey').placeholder = config.baidu_secret_key ? '已配置 (点击修改)' : '未配置';
    
    // 安全配置
    document.getElementById('clientAuthToken').placeholder = config.client_auth_token ? '已配置 (点击修改)' : '未配置';
    document.getElementById('testMode').checked = config.test_mode || false;
    
    // V2.4新增：AI审核开关
    document.getElementById('enableAiCheck').checked = config.enable_ai_check === true;
}

// 更新配置状态显示
function updateConfigStatus(config) {
    // WordPress状态
    const wpStatus = document.getElementById('wpStatus');
    const wpConfigured = config.wp_domain && config.wp_username && config.wp_app_password;
    wpStatus.className = `config-status ${wpConfigured ? 'configured' : 'not-configured'}`;
    wpStatus.textContent = wpConfigured ? '已配置' : '未配置';
    
    // 百度AI状态
    const baiduStatus = document.getElementById('baiduStatus');
    const baiduConfigured = config.baidu_api_key && config.baidu_secret_key;
    baiduStatus.className = `config-status ${baiduConfigured ? 'configured' : 'not-configured'}`;
    baiduStatus.textContent = baiduConfigured ? '已配置' : '未配置';
    
    // 安全配置状态
    const securityStatus = document.getElementById('securityStatus');
    const securityConfigured = config.client_auth_token;
    securityStatus.className = `config-status ${securityConfigured ? 'configured' : 'not-configured'}`;
    securityStatus.textContent = securityConfigured ? '已配置' : '未配置';
}

// 保存配置
async function saveConfiguration() {
    const configData = {
        wp_domain: document.getElementById('wpDomain').value.trim(),
        wp_username: document.getElementById('wpUsername').value.trim(),
        wp_app_password: document.getElementById('wpAppPassword').value.trim(),
        baidu_api_key: document.getElementById('baiduApiKey').value.trim(),
        baidu_secret_key: document.getElementById('baiduSecretKey').value.trim(),
        client_auth_token: document.getElementById('clientAuthToken').value.trim(),
        test_mode: document.getElementById('testMode').checked,
        enable_ai_check: document.getElementById('enableAiCheck').checked // V2.4新增
    };
    
    // 过滤空值（保留现有配置）
    const filteredConfig = {};
    Object.keys(configData).forEach(key => {
        if (configData[key] !== '' && configData[key] !== null) {
            filteredConfig[key] = configData[key];
        }
    });
    
    try {
        showConfigMessage('正在保存配置...', 'info');
        
        const response = await fetch('/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(filteredConfig)
        });
        
        if (response.status === 401) {
            // 会话过期，重定向到登录页
            showConfigMessage('登录已过期，请重新登录', 'error');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            return;
        } else if (response.status === 403) {
            // 权限不足
            showConfigMessage('您没有修改配置的权限', 'error');
            return;
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showConfigMessage('配置保存成功！', 'success');
            
            // 直接更新当前配置对象，避免重新从服务器加载
            Object.assign(currentConfig, filteredConfig);
            updateConfigStatus(currentConfig);
            
            // 延迟5秒后重新加载配置进行验证（可选）
            setTimeout(() => {
                loadCurrentConfig();
            }, 5000);
        } else {
            showConfigMessage('配置保存失败: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('配置保存失败:', error);
        showConfigMessage('配置保存失败: 网络错误', 'error');
    }
}

// 测试配置
async function testConfiguration() {
    try {
        showConfigMessage('正在测试配置...', 'info');
        
        // 测试健康检查
        const healthResponse = await fetch('/health');
        const healthResult = await healthResponse.json();
        
        if (healthResponse.ok) {
            showConfigMessage('配置测试成功！服务运行正常', 'success');
        } else {
            showConfigMessage('配置测试失败: 服务异常', 'error');
        }
        
        // 更新系统信息
        updateSystemInfo(healthResult);
        
    } catch (error) {
        console.error('配置测试失败:', error);
        showConfigMessage('配置测试失败: 网络错误', 'error');
    }
}

// 显示配置消息
function showConfigMessage(message, type) {
    // 创建消息元素
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type} show`;
    messageDiv.textContent = message;
    messageDiv.style.margin = '10px 0';
    
    // 插入到配置表单后面
    const configForm = document.getElementById('configForm');
    const existingMessage = configForm.parentNode.querySelector('.message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    configForm.parentNode.insertBefore(messageDiv, configForm.nextSibling);
    
    // 3秒后自动隐藏
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
}

// 更新系统信息
function updateSystemInfo(healthData) {
    if (healthData) {
        document.getElementById('serviceVersion').textContent = healthData.version || 'V2.4.0';
        document.getElementById('runningStatus').textContent = '✅ 运行正常';
        
        if (healthData.timestamp) {
            const time = new Date(healthData.timestamp).toLocaleString();
            document.getElementById('startTime').textContent = time;
        }
        
        // 显示活跃会话数
        if (healthData.active_sessions !== undefined) {
            const sessionInfo = document.getElementById('sessionInfo');
            if (sessionInfo) {
                sessionInfo.textContent = `活跃会话: ${healthData.active_sessions}`;
            }
        }
        
        // V2.4新增：显示AI审核状态
        if (healthData.ai_check_enabled !== undefined) {
            const aiCheckStatus = document.getElementById('aiCheckStatus');
            if (aiCheckStatus) {
                aiCheckStatus.textContent = healthData.ai_check_enabled ? '✅ 已启用' : '❌ 已禁用';
                aiCheckStatus.style.color = healthData.ai_check_enabled ? '#38a169' : '#e53e3e';
            }
        }
    }
}

// 加载系统日志
function loadSystemLogs() {
    const logsContainer = document.getElementById('systemLogs');
    
    // 模拟系统日志（实际项目中应该从服务器获取）
    const logs = [
        { time: new Date(), level: 'INFO', message: '文章发布系统 V2.4 启动成功' },
        { time: new Date(Date.now() - 60000), level: 'SUCCESS', message: 'AI审核开关功能已加载' },
        { time: new Date(Date.now() - 120000), level: 'SUCCESS', message: '代码模式编辑器初始化完成' },
        { time: new Date(Date.now() - 180000), level: 'SUCCESS', message: `用户 ${currentUser?.username || '未知'} 登录成功` },
        { time: new Date(Date.now() - 240000), level: 'SUCCESS', message: '发布历史面板加载完成' },
        { time: new Date(Date.now() - 300000), level: 'SUCCESS', message: '文章发布成功 - 使用/adv_posts端点' },
        { time: new Date(Date.now() - 600000), level: 'INFO', message: '本月发布统计API调用成功' },
        { time: new Date(Date.now() - 900000), level: 'SUCCESS', message: 'V2.4功能优化完成' },
        { time: new Date(Date.now() - 1200000), level: 'INFO', message: '富文本编辑器初始化完成' },
        { time: new Date(Date.now() - 1500000), level: 'SUCCESS', message: '配置管理模块加载成功' },
        { time: new Date(Date.now() - 1800000), level: 'INFO', message: 'Session管理器启动成功' }
    ];

    const logsHtml = logs.map(log => {
        const timeStr = log.time.toLocaleTimeString();
        const levelClass = log.level.toLowerCase();
        return `
            <div class="log-entry ${levelClass}">
                <span style="color: #718096;">[${timeStr}]</span>
                <span style="color: #4a5568; font-weight: 600;">[${log.level}]</span>
                ${log.message}
            </div>
        `;
    }).join('');

    logsContainer.innerHTML = logsHtml;
}

// 绘制发布趋势图表
function drawChart() {
    const canvas = document.getElementById('publishChart');
    const ctx = canvas.getContext('2d');
    
    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 准备数据 - 最近7天的发布数据
    const days = [];
    const publishCounts = [];
    const successCounts = [];
    
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        const dateStr = date.toDateString();
        
        days.push(date.getMonth() + 1 + '/' + date.getDate());
        
        const dayItems = publishHistory.filter(item => 
            new Date(item.timestamp).toDateString() === dateStr
        );
        
        publishCounts.push(dayItems.length);
        successCounts.push(dayItems.filter(item => item.success).length);
    }
    
    // 绘制图表
    const maxCount = Math.max(...publishCounts, 1);
    const chartHeight = 150;
    const chartWidth = canvas.width - 80;
    const barWidth = chartWidth / days.length;
    
    // 绘制坐标轴
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    
    // Y轴
    ctx.beginPath();
    ctx.moveTo(40, 20);
    ctx.lineTo(40, chartHeight + 20);
    ctx.stroke();
    
    // X轴
    ctx.beginPath();
    ctx.moveTo(40, chartHeight + 20);
    ctx.lineTo(chartWidth + 40, chartHeight + 20);
    ctx.stroke();
    
    // 绘制柱状图
    publishCounts.forEach((count, index) => {
        const successCount = successCounts[index];
        const failCount = count - successCount;
        
        const x = 40 + index * barWidth + barWidth * 0.2;
        const width = barWidth * 0.6;
        
        // 绘制成功部分（绿色）
        if (successCount > 0) {
            const successHeight = (successCount / maxCount) * chartHeight;
            const successY = chartHeight + 20 - successHeight;
            
            ctx.fillStyle = '#38a169';
            ctx.fillRect(x, successY, width, successHeight);
        }
        
        // 绘制失败部分（红色）
        if (failCount > 0) {
            const failHeight = (failCount / maxCount) * chartHeight;
            const failY = chartHeight + 20 - (successCount + failCount) / maxCount * chartHeight;
            
            ctx.fillStyle = '#e53e3e';
            ctx.fillRect(x, failY, width, failHeight);
        }
        
        // 绘制总数值
        ctx.fillStyle = '#4a5568';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        if (count > 0) {
            const totalY = chartHeight + 20 - (count / maxCount) * chartHeight;
            ctx.fillText(count, x + width / 2, totalY - 5);
        }
        
        // 绘制日期
        ctx.fillStyle = '#718096';
        ctx.fillText(days[index], x + width / 2, chartHeight + 35);
    });
    
    // 绘制图例
    ctx.fillStyle = '#38a169';
    ctx.fillRect(chartWidth - 100, 30, 15, 10);
    ctx.fillStyle = '#4a5568';
    ctx.font = '12px Arial';
    ctx.textAlign = 'left';
    ctx.fillText('成功', chartWidth - 80, 39);
    
    ctx.fillStyle = '#e53e3e';
    ctx.fillRect(chartWidth - 100, 45, 15, 10);
    ctx.fillStyle = '#4a5568';
    ctx.fillText('失败', chartWidth - 80, 54);
}

// 刷新日志
function refreshLogs() {
    loadSystemLogs();
}

// 刷新所有数据
function refreshAll() {
    loadStatistics();
    loadCurrentConfig();
    loadSystemLogs();
    loadPublishHistory();
    drawChart();
}

// 导出系统报告
function exportSystemReport() {
    const report = {
        timestamp: new Date().toISOString(),
        version: 'V2.3.0',
        user: currentUser ? {
            username: currentUser.username,
            role: currentUser.role,
            login_time: currentUser.login_time
        } : null,
        statistics: {
            total: publishHistory.length,
            successful: publishHistory.filter(item => item.success).length,
            failed: publishHistory.filter(item => !item.success).length,
            today: publishHistory.filter(item => 
                new Date(item.timestamp).toDateString() === new Date().toDateString()
            ).length,
            auditRejected: publishHistory.filter(item => 
                !item.success && (item.message.includes('审核') || item.message.includes('敏感'))
            ).length
        },
        configuration: {
            wp_configured: currentConfig.wp_domain && currentConfig.wp_username && currentConfig.wp_app_password,
            baidu_configured: currentConfig.baidu_api_key && currentConfig.baidu_secret_key,
            security_configured: currentConfig.client_auth_token,
            test_mode: currentConfig.test_mode
        },
        history: publishHistory.slice(0, 100), // 最近100条记录
        features: [
            'V2.4功能优化：代码模式、发布历史面板及审核开关优化', // V2.4新增
            'HTML代码编辑器支持', // V2.4新增
            'AI审核开关控制', // V2.4新增
            'Web UI深度重构与极简布局',
            '本月发布统计功能',
            '多角色登录系统（管理员 vs 外包人员）',
            '基于Session的身份认证',
            '路由权限控制',
            '适配WordPress插件V2.1版本',
            '富文本编辑器支持',
            '百度AI内容审核',
            '自动文章分类',
            '配置管理界面',
            '增强容错机制',
            '本地测试环境优化'
        ]
    };
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { 
        type: 'application/json' 
    });
    
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `系统报告_V2.3_${new Date().toISOString().split('T')[0]}.json`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showConfigMessage('系统报告已导出', 'success');
}

// 全局函数，供HTML调用
window.logout = logout;
window.saveConfiguration = saveConfiguration;
window.testConfiguration = testConfiguration;
window.refreshLogs = refreshLogs;
window.refreshAll = refreshAll;
window.exportSystemReport = exportSystemReport;
window.clearHistory = clearHistory;
window.exportHistory = exportHistory;