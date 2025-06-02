// Free AugmentCode - Frontend JavaScript

// Global state
let isOperationRunning = false;

// DOM elements
const elements = {
    apiStatus: null,
    systemInfo: null,
    resultsPanel: null,
    resultsContent: null,
    loadingOverlay: null,
    loadingText: null,
    buttons: {}
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();
    checkAPIStatus();
    loadSystemInfo();
});

// Initialize DOM element references
function initializeElements() {
    elements.apiStatus = document.getElementById('apiStatus');
    elements.systemInfo = document.getElementById('systemInfo');
    elements.resultsPanel = document.getElementById('resultsPanel');
    elements.resultsContent = document.getElementById('resultsContent');
    elements.loadingOverlay = document.getElementById('loadingOverlay');
    elements.loadingText = document.getElementById('loadingText');
    
    // Button references
    elements.buttons = {
        telemetry: document.getElementById('telemetryBtn'),
        database: document.getElementById('databaseBtn'),
        workspace: document.getElementById('workspaceBtn'),
        all: document.getElementById('allBtn')
    };
}

// Show loading overlay
function showLoading(message = '正在处理...') {
    elements.loadingText.textContent = message;
    elements.loadingOverlay.style.display = 'flex';
    setButtonsDisabled(true);
    isOperationRunning = true;
}

// Hide loading overlay
function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
    setButtonsDisabled(false);
    isOperationRunning = false;
}

// Enable/disable all buttons
function setButtonsDisabled(disabled) {
    Object.values(elements.buttons).forEach(btn => {
        if (btn) btn.disabled = disabled;
    });
}

// Check API status
async function checkAPIStatus() {
    try {
        const result = await pywebview.api.get_status();
        if (result.success) {
            elements.apiStatus.textContent = '✅ 就绪';
            elements.apiStatus.style.background = 'rgba(40, 167, 69, 0.2)';
        } else {
            elements.apiStatus.textContent = '❌ 错误';
            elements.apiStatus.style.background = 'rgba(220, 53, 69, 0.2)';
        }
    } catch (error) {
        console.error('API status check failed:', error);
        elements.apiStatus.textContent = '❌ 连接失败';
        elements.apiStatus.style.background = 'rgba(220, 53, 69, 0.2)';
    }
}

// Load system information
async function loadSystemInfo() {
    try {
        const result = await pywebview.api.get_system_info();
        
        if (result.success) {
            displaySystemInfo(result.data);
        } else {
            elements.systemInfo.innerHTML = `
                <div class="error">
                    <strong>错误:</strong> ${result.message || result.error}
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load system info:', error);
        elements.systemInfo.innerHTML = `
            <div class="error">
                <strong>加载失败:</strong> ${error.message}
            </div>
        `;
    }
}

// Display system information
function displaySystemInfo(data) {
    const infoItems = [
        { label: '用户目录', value: data.home_dir },
        { label: '应用数据目录', value: data.app_data_dir },
        { label: 'Storage 文件', value: data.storage_path },
        { label: '数据库文件', value: data.db_path },
        { label: '机器 ID 文件', value: data.machine_id_path },
        { label: '工作区存储', value: data.workspace_storage_path }
    ];

    elements.systemInfo.innerHTML = infoItems.map(item => `
        <div class="info-item">
            <div class="info-label">${item.label}:</div>
            <div class="info-value">${item.value}</div>
        </div>
    `).join('');
}

// Modify telemetry IDs
async function modifyTelemetry() {
    if (isOperationRunning) return;
    
    showLoading('正在修改 Telemetry ID...');
    
    try {
        const result = await pywebview.api.modify_telemetry();
        displayResults('Telemetry ID 修改', result);
    } catch (error) {
        displayResults('Telemetry ID 修改', {
            success: false,
            error: error.message,
            message: '操作失败'
        });
    } finally {
        hideLoading();
    }
}

// Clean database
async function cleanDatabase() {
    if (isOperationRunning) return;
    
    showLoading('正在清理数据库...');
    
    try {
        const result = await pywebview.api.clean_database();
        displayResults('数据库清理', result);
    } catch (error) {
        displayResults('数据库清理', {
            success: false,
            error: error.message,
            message: '操作失败'
        });
    } finally {
        hideLoading();
    }
}

// Clean workspace
async function cleanWorkspace() {
    if (isOperationRunning) return;
    
    showLoading('正在清理工作区...');
    
    try {
        const result = await pywebview.api.clean_workspace();
        displayResults('工作区清理', result);
    } catch (error) {
        displayResults('工作区清理', {
            success: false,
            error: error.message,
            message: '操作失败'
        });
    } finally {
        hideLoading();
    }
}

// Run all operations
async function runAllOperations() {
    if (isOperationRunning) return;
    
    showLoading('正在执行所有清理操作...');
    
    try {
        const result = await pywebview.api.run_all_operations();
        displayAllResults(result);
    } catch (error) {
        displayResults('所有操作', {
            success: false,
            error: error.message,
            message: '操作失败'
        });
    } finally {
        hideLoading();
    }
}

// Display operation results
function displayResults(operationName, result) {
    const resultClass = result.success ? 'success' : 'error';
    const icon = result.success ? '✅' : '❌';
    
    let content = `
        <div class="result-item ${resultClass}">
            <h3>${icon} ${operationName}</h3>
            <p><strong>状态:</strong> ${result.message}</p>
    `;
    
    if (result.success && result.data) {
        content += formatResultData(result.data);
    }
    
    if (!result.success && result.error) {
        content += `<p><strong>错误:</strong> ${result.error}</p>`;
    }
    
    content += '</div>';
    
    elements.resultsContent.innerHTML = content;
    elements.resultsPanel.style.display = 'block';
    elements.resultsPanel.scrollIntoView({ behavior: 'smooth' });
}

// Display results for all operations
function displayAllResults(result) {
    let content = '';
    
    if (result.data) {
        const operations = [
            { key: 'telemetry', name: 'Telemetry ID 修改' },
            { key: 'database', name: '数据库清理' },
            { key: 'workspace', name: '工作区清理' }
        ];
        
        operations.forEach(op => {
            if (result.data[op.key]) {
                const opResult = result.data[op.key];
                const resultClass = opResult.success ? 'success' : 'error';
                const icon = opResult.success ? '✅' : '❌';
                
                content += `
                    <div class="result-item ${resultClass}">
                        <h4>${icon} ${op.name}</h4>
                        <p>${opResult.message}</p>
                `;
                
                if (opResult.success && opResult.data) {
                    content += formatResultData(opResult.data);
                }
                
                content += '</div>';
            }
        });
    }
    
    elements.resultsContent.innerHTML = content;
    elements.resultsPanel.style.display = 'block';
    elements.resultsPanel.scrollIntoView({ behavior: 'smooth' });
}

// Format result data for display
function formatResultData(data) {
    let formatted = '';
    
    if (data.old_machine_id && data.new_machine_id) {
        formatted += `
            <p><strong>旧机器 ID:</strong> ${data.old_machine_id.substring(0, 16)}...</p>
            <p><strong>新机器 ID:</strong> ${data.new_machine_id.substring(0, 16)}...</p>
        `;
    }
    
    if (data.deleted_rows !== undefined) {
        formatted += `<p><strong>删除记录数:</strong> ${data.deleted_rows}</p>`;
    }
    
    if (data.deleted_files_count !== undefined) {
        formatted += `<p><strong>删除文件数:</strong> ${data.deleted_files_count}</p>`;
    }
    
    if (data.storage_backup_path) {
        formatted += `<p><strong>备份位置:</strong> ${data.storage_backup_path}</p>`;
    }
    
    return formatted;
}
