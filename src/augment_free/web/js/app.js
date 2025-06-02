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

    // Wait a bit for pywebview to be ready
    setTimeout(() => {
        checkAPIStatus();
        loadSystemInfo();
    }, 500);
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

// Change editor type
async function changeEditor() {
    const editorSelect = document.getElementById('editorSelect');
    const selectedEditor = editorSelect.value;

    if (!checkAPIAvailable()) return;

    try {
        const result = await pywebview.api.set_editor_type(selectedEditor);
        if (result.success) {
            console.log(`Editor type changed to: ${selectedEditor}`);
            // Reload system info to show new paths
            loadSystemInfo();
        } else {
            console.error('Failed to change editor type:', result.error);
            alert('切换编辑器失败: ' + result.error);
        }
    } catch (error) {
        console.error('Error changing editor type:', error);
        alert('切换编辑器时发生错误: ' + error.message);
    }
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
        // Wait for pywebview to be ready
        if (typeof pywebview === 'undefined') {
            elements.apiStatus.textContent = '⏳ 等待连接...';
            elements.apiStatus.style.background = 'rgba(255, 193, 7, 0.2)';
            setTimeout(checkAPIStatus, 1000); // Retry after 1 second
            return;
        }

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
        // Retry after a delay
        setTimeout(checkAPIStatus, 2000);
    }
}

// Load system information
async function loadSystemInfo() {
    try {
        // Check if pywebview is available
        if (typeof pywebview === 'undefined') {
            elements.systemInfo.innerHTML = `
                <div class="loading">等待API连接...</div>
            `;
            return;
        }

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
        { label: '当前编辑器', value: data.editor_type || 'VSCodium', icon: '🎯' },
        { label: 'Storage 文件', value: data.storage_path, icon: '💾' },
        { label: '数据库文件', value: data.db_path, icon: '🗃️' },
        { label: '机器 ID 文件', value: data.machine_id_path, icon: '🔑' },
        { label: '工作区存储', value: data.workspace_storage_path, icon: '📁' }
    ];

    elements.systemInfo.innerHTML = infoItems.map(item => `
        <div class="info-item">
            <div class="info-icon">${item.icon}</div>
            <div class="info-content">
                <div class="info-label">${item.label}</div>
                <div class="info-value">${item.value}</div>
            </div>
        </div>
    `).join('');

    // Update editor select to match current editor type
    const editorSelect = document.getElementById('editorSelect');
    if (editorSelect && data.editor_type) {
        editorSelect.value = data.editor_type;
    }
}

// Check if API is available
function checkAPIAvailable() {
    if (typeof pywebview === 'undefined') {
        alert('API未连接，请等待应用完全加载后再试！');
        return false;
    }
    return true;
}

// Modify telemetry IDs
async function modifyTelemetry() {
    if (isOperationRunning || !checkAPIAvailable()) return;

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
    if (isOperationRunning || !checkAPIAvailable()) return;

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
    if (isOperationRunning || !checkAPIAvailable()) return;

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
    if (isOperationRunning || !checkAPIAvailable()) return;

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
