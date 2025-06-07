// Free AugmentCode - Frontend JavaScript

// Global state
let isOperationRunning = false;
let isDetecting = false;
let detectedIDEs = [];

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

        // Check if this is the first time using the app
        checkFirstTimeUse();
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
        all: document.getElementById('allBtn'),
        detect: document.getElementById('detectBtn')
    };

    // Other elements
    elements.editorSelect = document.getElementById('editorSelect');
    elements.detectStatus = document.getElementById('detectStatus');
}

// Change editor type
async function changeEditor() {
    const editorSelect = document.getElementById('editorSelect');
    const selectedEditor = editorSelect.value;

    if (!checkAPIAvailable()) return;

    // Get IDE info from detected IDEs
    let ideInfo = null;
    const selectedIDE = detectedIDEs.find(ide => ide.name === selectedEditor);
    if (selectedIDE) {
        ideInfo = selectedIDE;
    }

    // Update footer editor names immediately
    updateFooterEditorNames(selectedEditor, ideInfo);

    try {
        const result = await pywebview.api.set_editor_type(selectedEditor, ideInfo);
        if (result.success) {
            console.log(`Editor type changed to: ${selectedEditor}`, ideInfo);
            // Reload system info to show new paths
            loadSystemInfo();
            // Update operations based on IDE type
            updateOperationsForIDE(ideInfo);
        } else {
            console.error('Failed to change editor type:', result.error);
            alert('切换编辑器失败: ' + result.error);
        }
    } catch (error) {
        console.error('Error changing editor type:', error);
        alert('切换编辑器时发生错误: ' + error.message);
    }
}

// Update footer editor names
function updateFooterEditorNames(editorType, ideInfo = null) {
    let editorName = editorType;

    // Use display name if available from IDE info
    if (ideInfo && ideInfo.display_name) {
        editorName = ideInfo.display_name;
    } else {
        // Fallback for default names
        editorName = editorType === 'Code' ? 'VS Code' : editorType;
    }

    const footerEditorName1 = document.getElementById('footerEditorName1');
    const footerEditorName2 = document.getElementById('footerEditorName2');

    if (footerEditorName1) {
        footerEditorName1.textContent = editorName;
    }
    if (footerEditorName2) {
        footerEditorName2.textContent = editorName;
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
            // elements.apiStatus.style.background = 'rgba(40, 167, 69, 0.2)';
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
    let infoItems = [];

    // Common info
    infoItems.push({ label: '当前编辑器', value: data.editor_type || 'VSCodium', icon: '🎯' });

    if (data.ide_type === 'jetbrains') {
        // JetBrains IDE info
        infoItems.push(
            { label: '配置目录', value: data.jetbrains_config_path || '未找到', icon: '📁' },
            { label: '设备 ID 文件', value: data.permanent_device_id_path || '未找到', icon: '🔑' },
            { label: '用户 ID 文件', value: data.permanent_user_id_path || '未找到', icon: '👤' }
        );
    } else {
        // VSCode series info
        infoItems.push(
            { label: 'Storage 文件', value: data.storage_path, icon: '💾' },
            { label: '数据库文件', value: data.db_path, icon: '🗃️' },
            { label: '机器 ID 文件', value: data.machine_id_path, icon: '🔑' },
            { label: '工作区存储', value: data.workspace_storage_path, icon: '📁' }
        );
    }

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

    // Update footer editor names
    updateFooterEditorNames(data.editor_type || 'VSCodium');
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

// Check if this is the first time using the app
async function checkFirstTimeUse() {
    try {
        // Check if pywebview is available
        if (typeof pywebview === 'undefined') {
            console.log('PyWebView not ready, skipping first time check');
            return;
        }

        const result = await pywebview.api.is_first_run();
        if (result.success && result.data.is_first_run) {
            // First time use - show about modal after a delay
            setTimeout(() => {
                showAboutModal(true); // Pass true to indicate this is auto-show
            }, 1500); // Wait 1.5 seconds for app to fully load
        }
    } catch (error) {
        console.error('Error checking first time use:', error);
    }
}

// Mark that user has seen the about modal
async function markAboutAsSeen() {
    try {
        if (typeof pywebview !== 'undefined') {
            await pywebview.api.mark_first_run_complete();
        }
    } catch (error) {
        console.error('Error saving about seen status:', error);
    }
}

// About Modal Functions
function showAboutModal(isAutoShow = false) {
    const modal = document.getElementById('aboutModal');
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);

        // Load version info
        loadVersionInfo();

        // If this is auto-show (first time), mark as seen
        if (isAutoShow) {
            markAboutAsSeen();
        }
    }
}

function hideAboutModal() {
    const modal = document.getElementById('aboutModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}

// Load version information
async function loadVersionInfo() {
    try {
        if (typeof pywebview !== 'undefined') {
            const result = await pywebview.api.get_version_info();
            if (result.success && result.data) {
                const versionElement = document.getElementById('appVersion');
                if (versionElement) {
                    versionElement.textContent = `v${result.data.version}`;
                }
            }
        }
    } catch (error) {
        console.error('Failed to load version info:', error);
    }
}

// Open external links
async function openGitHubRepo() {
    try {
        if (typeof pywebview !== 'undefined') {
            await pywebview.api.open_external_link('https://github.com/vagmr/Augment-free');
        }
    } catch (error) {
        console.error('Failed to open GitHub repo:', error);
        // Fallback: try to open in browser
        window.open('https://github.com/vagmr/Augment-free', '_blank');
    }
}

async function openGitHubReleases() {
    try {
        if (typeof pywebview !== 'undefined') {
            await pywebview.api.open_external_link('https://github.com/vagmr/Augment-free/releases');
        }
    } catch (error) {
        console.error('Failed to open GitHub releases:', error);
        // Fallback: try to open in browser
        window.open('https://github.com/vagmr/Augment-free/releases', '_blank');
    }
}

async function openGitHubIssues() {
    try {
        if (typeof pywebview !== 'undefined') {
            await pywebview.api.open_external_link('https://github.com/vagmr/Augment-free/issues');
        }
    } catch (error) {
        console.error('Failed to open GitHub issues:', error);
        // Fallback: try to open in browser
        window.open('https://github.com/vagmr/Augment-free/issues', '_blank');
    }
}

// Detect IDEs function
async function detectIDEs() {
    if (isDetecting || isOperationRunning || !checkAPIAvailable()) return;

    isDetecting = true;
    const detectBtn = elements.buttons.detect;
    const detectStatus = elements.detectStatus;

    // Update button state
    detectBtn.disabled = true;
    detectBtn.textContent = '🔄';
    detectBtn.title = '检测中...';

    // Show status
    detectStatus.textContent = '检测中...';
    detectStatus.className = 'detect-status show';

    try {
        const result = await pywebview.api.detect_ides();

        if (result.success) {
            detectedIDEs = result.ides;
            updateEditorSelect(result.ides);

            // Show success status
            detectStatus.textContent = `✅ 找到 ${result.count} 个IDE`;
            detectStatus.className = 'detect-status show success';

            // Update button
            detectBtn.textContent = '🔍';
            detectBtn.title = '重新检测IDE';

            console.log('IDE detection successful:', result);
        } else {
            // Show error status
            detectStatus.textContent = `❌ ${result.message}`;
            detectStatus.className = 'detect-status show error';

            // Reset button
            detectBtn.textContent = '🔍';
            detectBtn.title = '自动检测IDE';

            console.error('IDE detection failed:', result);
        }
    } catch (error) {
        console.error('Error detecting IDEs:', error);

        // Show error status
        detectStatus.textContent = '❌ 检测失败';
        detectStatus.className = 'detect-status show error';

        // Reset button
        detectBtn.textContent = '🔍';
        detectBtn.title = '自动检测IDE';
    } finally {
        detectBtn.disabled = false;
        isDetecting = false;

        // Hide status after 5 seconds
        setTimeout(() => {
            detectStatus.textContent = 'By vagmr';
        }, 5000);
    }
}

// Update editor select with detected IDEs
function updateEditorSelect(ides) {
    const editorSelect = elements.editorSelect;
    if (!editorSelect) return;

    // Clear existing options
    editorSelect.innerHTML = '';

    if (ides.length === 0) {
        // No IDEs detected, restore defaults
        editorSelect.innerHTML = `
            <option value="VSCodium">🔷 VSCodium</option>
            <option value="Code">💙 VS Code</option>
        `;
        return;
    }

    // Add detected IDEs
    ides.forEach(ide => {
        const option = document.createElement('option');
        option.value = ide.name;
        option.textContent = `${ide.icon} ${ide.display_name}`;

        // Add path info as title
        if (ide.config_path) {
            option.title = `路径: ${ide.config_path}`;
        }

        editorSelect.appendChild(option);
    });

    // Trigger change event to update system info
    if (ides.length > 0) {
        editorSelect.value = ides[0].name;
        changeEditor();
    } else {
        // No IDEs detected, update operations for default VSCode
        updateOperationsForIDE(null);
    }
}

// Get default IDEs (for reset)
async function getDefaultIDEs() {
    try {
        if (!checkAPIAvailable()) return;

        const result = await pywebview.api.get_default_ides();
        if (result.success) {
            updateEditorSelect(result.ides);
        }
    } catch (error) {
        console.error('Error getting default IDEs:', error);
    }
}

// Update operations based on IDE type
async function updateOperationsForIDE(ideInfo) {
    try {
        if (!checkAPIAvailable()) return;

        const result = await pywebview.api.get_supported_operations();
        if (result.success) {
            updateOperationsUI(result.data);
        }
    } catch (error) {
        console.error('Error getting supported operations:', error);
    }
}

// Update operations UI based on supported operations
function updateOperationsUI(data) {
    const operationsGrid = document.querySelector('.operations-grid-compact');
    if (!operationsGrid) return;

    const operations = data.operations || [];
    const ideType = data.ide_type || 'vscode';

    // Clear existing operations
    operationsGrid.innerHTML = '';

    // Add supported operations
    operations.forEach(op => {
        if (op.supported) {
            const operationHTML = `
                <div class="operation-item-compact">
                    <div class="operation-icon">${op.icon}</div>
                    <div class="operation-content">
                        <h3>${op.name}</h3>
                        <p>${op.description}</p>
                    </div>
                    <button class="operation-btn btn-primary" onclick="${getOperationFunction(op.id)}()" id="${op.id}Btn">
                        ${getOperationButtonText(op.id)}
                    </button>
                </div>
            `;
            operationsGrid.insertAdjacentHTML('beforeend', operationHTML);
        }
    });

    // Update button references
    elements.buttons.telemetry = document.getElementById('telemetryBtn');
    elements.buttons.database = document.getElementById('databaseBtn');
    elements.buttons.workspace = document.getElementById('workspaceBtn');

    console.log(`Operations updated for ${ideType} IDE:`, operations);
}

// Get operation function name
function getOperationFunction(operationId) {
    const functionMap = {
        'telemetry': 'modifyTelemetry',
        'database': 'cleanDatabase',
        'workspace': 'cleanWorkspace'
    };
    return functionMap[operationId] || 'modifyTelemetry';
}

// Get operation button text
function getOperationButtonText(operationId) {
    const textMap = {
        'telemetry': '重置机器码',
        'database': '清理数据库',
        'workspace': '清理工作区'
    };
    return textMap[operationId] || '执行操作';
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('aboutModal');
    if (modal && event.target === modal) {
        hideAboutModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        hideAboutModal();
    }
});
