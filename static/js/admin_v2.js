// WordPress软文发布中间件 V2.1 - 管理后台脚本
// 包含配置管理和系统监控功能

// 全局变量
let publishHistory = JSON.parse(localStorage.getItem('publishHistory') || '[]');
let currentConfig = {};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeAdmin();
});

// 初始化管理后台
function initializeAdmin() {
    loadStatistics();
    loadCurrentConfig();
    loadSystemLogs();
    drawChart();
    
    // 定期刷新数据
    setInterval(refreshAll, 60000); // 每分钟刷新一次
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

// 加载当前配置
async function loadCurrentConfig() {
    try {
        const response = await fetch('/config');
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
        test_mode: document.getElementById('testMode').checked
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
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showConfigMessage('配置保存成功！', 'success');
            // 重新加载配置
            setTimeout(() => {
                loadCurrentConfig();
            }, 1000);
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
        document.getElementById('serviceVersion').textContent = healthData.version || 'V2.1.0';
        document.getElementById('runningStatus').textContent = '✅ 运行正常';
        
        if (healthData.timestamp) {
            const time = new Date(healthData.timestamp).toLocaleString();
            document.getElementById('startTime').textContent = time;
        }
    }
}

// 加载系统日志
function loadSystemLogs() {
    const logsContainer = document.getElementById('systemLogs');
    
    // 模拟系统日志（实际项目中应该从服务器获取）
    const logs = [
        { time: new Date(), level: 'INFO', message: 'WordPress软文发布中间件 V2.1 启动成功' },
        { time: new Date(Date.now() - 300000), level: 'SUCCESS', message: '文章发布成功 - 使用/adv_posts端点' },
        { time: new Date(Date.now() - 600000), level: 'INFO', message: '百度AI Token自动刷新成功' },
        { time: new Date(Date.now() - 900000), level: 'SUCCESS', message: '外包身份令牌验证通过' },
        { time: new Date(Date.now() - 1200000), level: 'INFO', message: '富文本编辑器初始化完成' },
        { time: new Date(Date.now() - 1500000), level: 'SUCCESS', message: '配置管理模块加载成功' }
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
    drawChart();
}

// 导出系统报告
function exportSystemReport() {
    const report = {
        timestamp: new Date().toISOString(),
        version: 'V2.1.0',
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
    link.setAttribute('download', `系统报告_V2.1_${new Date().toISOString().split('T')[0]}.json`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showConfigMessage('系统报告已导出', 'success');
}