// Free AugmentCode - Frontend JavaScript

// Global state
let isOperationRunning = false;
let isDetecting = false;
let detectedIDEs = [];
let currentLanguage = 'zh_CN';
let translations = {};
let isShowingDetectedIDEs = false; // Flag to track if we're showing detected IDEs

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

// Translation functions
function t(key, params = {}) {
    const keys = key.split('.');
    let value = translations;

    for (const k of keys) {
        if (value && typeof value === 'object' && k in value) {
            value = value[k];
        } else {
            return key; // Return key if translation not found
        }
    }

    // Handle parameter substitution
    if (typeof value === 'string' && Object.keys(params).length > 0) {
        return value.replace(/\{(\w+)\}/g, (match, paramKey) => {
            return params[paramKey] || match;
        });
    }

    return value || key;
}

async function loadTranslations() {
    try {
        if (typeof pywebview !== 'undefined') {
            const result = await pywebview.api.get_current_language();
            if (result.success) {
                currentLanguage = result.data.current_language;
            }

            const translationsResult = await pywebview.api.get_translations();
            if (translationsResult.success) {
                translations = translationsResult.data.translations;
                updateUILanguage();
            }
        }
    } catch (error) {
        console.error('Failed to load translations:', error);
    }
}

async function switchLanguage(langCode) {
    try {
        if (typeof pywebview !== 'undefined') {
            // Store current status state before language change
            const currentStatusText = elements.apiStatus ? elements.apiStatus.textContent : '';
            const isReady = currentStatusText.includes('✅');
            const isChecking = currentStatusText.includes('⏳');
            const isError = currentStatusText.includes('❌');

            const result = await pywebview.api.set_language(langCode);
            if (result.success) {
                currentLanguage = langCode;
                await loadTranslations();

                // Restore status with proper translation after language change
                if (elements.apiStatus) {
                    if (isReady) {
                        const ideCount = detectedIDEs.length;
                        if (ideCount > 0) {
                            elements.apiStatus.textContent = `✅ ${t('ui.header.status_ready')} (${ideCount} IDEs)`;
                        } else {
                            elements.apiStatus.textContent = '✅ ' + t('ui.header.status_ready');
                        }
                        elements.apiStatus.style.background = 'rgba(40, 167, 69, 0.2)';
                    } else if (isChecking) {
                        elements.apiStatus.textContent = '⏳ ' + t('ui.header.status_checking');
                        elements.apiStatus.style.background = 'rgba(255, 193, 7, 0.2)';
                    } else if (isError) {
                        elements.apiStatus.textContent = '❌ ' + t('ui.header.status_error');
                        elements.apiStatus.style.background = 'rgba(220, 53, 69, 0.2)';
                    }
                }

                showMessage(t('messages.success.language_changed'), 'success');
            } else {
                showMessage(t('messages.error.language_change_failed'), 'error');
            }
        }
    } catch (error) {
        console.error('Failed to switch language:', error);
        showMessage(t('messages.error.language_change_failed'), 'error');
    }
}

function updateUILanguage() {
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translatedText = t(key);

        if (element.tagName === 'INPUT' && element.type === 'text') {
            element.placeholder = translatedText;
        } else {
            element.textContent = translatedText;
        }
    });

    // Update elements with data-i18n-title attribute
    document.querySelectorAll('[data-i18n-title]').forEach(element => {
        const key = element.getAttribute('data-i18n-title');
        const translatedText = t(key);
        element.title = translatedText;
    });

    // Update title and subtitle
    document.title = t('app.title');

    // Update specific elements that need special handling
    updateDynamicContent();

    // Force update all operation buttons and content
    updateOperationTexts();

    // Update footer text
    updateFooterText();

    // Update detect button tooltip
    const detectBtn = document.getElementById('detectBtn');
    if (detectBtn) {
        detectBtn.title = t('ui.header.detect_tooltip');
    }
}

async function toggleLanguage() {
    const newLang = currentLanguage === 'zh_CN' ? 'en_US' : 'zh_CN';
    await switchLanguage(newLang);
}

function updateDynamicContent() {
    // Update loading text if currently visible
    const loadingText = document.getElementById('loadingText');
    if (loadingText && elements.loadingOverlay && elements.loadingOverlay.style.display !== 'none') {
        loadingText.textContent = t('ui.loading.processing');
    }

    // Don't update API status here - let the status checking function handle it
    // This prevents interference with the status checking process during language switching

    // Update footer text with current editor name
    updateFooterText();
}

function updateFooterText() {
    const footerEditorName1 = document.getElementById('footerEditorName1');
    const footerEditorName2 = document.getElementById('footerEditorName2');
    const footerWarningText = document.getElementById('footerWarningText');
    const footerTipText = document.getElementById('footerTipText');

    if (footerWarningText && footerTipText) {
        const editorName = (footerEditorName1 && footerEditorName1.textContent) || 'VS Code';

        // Update warning text with proper interpolation
        const warningText = t('ui.footer.warning.text', { editor: editorName });
        footerWarningText.innerHTML = warningText.replace(editorName, `<span id="footerEditorName1">${editorName}</span>`);

        // Update tip text with proper interpolation
        const tipText = t('ui.footer.tip.text', { editor: editorName });
        footerTipText.innerHTML = tipText.replace(editorName, `<span id="footerEditorName2">${editorName}</span>`);
    }
}

function updateOperationTexts() {
    // Update operation titles, descriptions, and buttons
    const operations = [
        {
            titleSelector: '[data-i18n="ui.operations.telemetry.title"]',
            descSelector: '[data-i18n="ui.operations.telemetry.description"]',
            buttonSelector: '#telemetryBtn',
            titleKey: 'ui.operations.telemetry.title',
            descKey: 'ui.operations.telemetry.description',
            buttonKey: 'ui.operations.telemetry.button'
        },
        {
            titleSelector: '[data-i18n="ui.operations.database.title"]',
            descSelector: '[data-i18n="ui.operations.database.description"]',
            buttonSelector: '#databaseBtn',
            titleKey: 'ui.operations.database.title',
            descKey: 'ui.operations.database.description',
            buttonKey: 'ui.operations.database.button'
        },
        {
            titleSelector: '[data-i18n="ui.operations.workspace.title"]',
            descSelector: '[data-i18n="ui.operations.workspace.description"]',
            buttonSelector: '#workspaceBtn',
            titleKey: 'ui.operations.workspace.title',
            descKey: 'ui.operations.workspace.description',
            buttonKey: 'ui.operations.workspace.button'
        },
        {
            titleSelector: '[data-i18n="ui.operations.all.title"]',
            descSelector: '[data-i18n="ui.operations.all.description"]',
            buttonSelector: '#allBtn',
            titleKey: 'ui.operations.all.title',
            descKey: 'ui.operations.all.description',
            buttonKey: 'ui.operations.all.button'
        }
    ];

    operations.forEach(op => {
        const titleEl = document.querySelector(op.titleSelector);
        const descEl = document.querySelector(op.descSelector);
        const buttonEl = document.querySelector(op.buttonSelector);

        if (titleEl) titleEl.textContent = t(op.titleKey);
        if (descEl) descEl.textContent = t(op.descKey);
        if (buttonEl) buttonEl.textContent = t(op.buttonKey);
    });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeElements();

    // Set initial IDE count
    if (elements.ideCount) {
        elements.ideCount.textContent = '0';
    }

    // Initialize with proper loading sequence
    setTimeout(async () => {
        console.log('Starting application initialization...');

        // Step 1: Load translations first
        await loadTranslations();
        console.log('Translations loaded');

        // Step 2: Check API status (this will retry until ready)
        await checkAPIStatus();
        console.log('API status checked');

        // Step 3: Auto-detect IDEs first (this will populate the system info)
        await autoDetectIDEsOnStartup();
        console.log('IDE detection completed');

        // Step 4: If no IDEs detected, load default system info
        if (!detectedIDEs || detectedIDEs.length === 0) {
            await loadSystemInfo();
            console.log('Default system info loaded');
        }

        // Step 5: Check if this is the first time using the app
        checkFirstTimeUse();

        console.log('Application initialization complete');
    }, 1000); // Increased delay to ensure pywebview is ready
});

// Auto-detect IDEs on startup
async function autoDetectIDEsOnStartup() {
    try {
        if (!checkAPIAvailable()) return;

        console.log('Auto-detecting IDEs on startup...');
        const result = await pywebview.api.detect_ides();

        if (result.success && result.ides && result.ides.length > 0) {
            detectedIDEs = result.ides;

            // Update IDE count display
            if (elements.ideCount) {
                elements.ideCount.textContent = detectedIDEs.length;
            }

            // Update system info to show all detected IDEs
            displayDetectedIDEs(detectedIDEs);

            console.log(`Auto-detected ${detectedIDEs.length} IDEs:`, detectedIDEs);

            // Update detect status briefly
            const detectStatus = elements.detectStatus;
            if (detectStatus) {
                detectStatus.textContent = `✅ ${t('messages.info.ides_detected', { count: detectedIDEs.length })}`;
                detectStatus.className = 'detect-status show success';

                setTimeout(() => {
                    detectStatus.textContent = 'By vagmr';
                    detectStatus.className = 'detect-status';
                }, 3000);
            }

            // Update status with IDE count
            updateStatusWithIDECount();
        } else {
            console.log('No IDEs auto-detected, using defaults');
            if (elements.ideCount) {
                elements.ideCount.textContent = '0';
            }
        }
    } catch (error) {
        console.error('Auto-detection failed:', error);
    }
}

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
    elements.ideCount = document.getElementById('ideCount');
    elements.detectStatus = document.getElementById('detectStatus');
}

// This function is no longer needed as we removed the editor selector

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

    // Update footer text with new editor name
    updateFooterText();
}

// Update operations for IDE type
function updateOperationsForIDE(ideInfo) {
    const isJetBrains = ideInfo && ideInfo.ide_type === 'jetbrains';

    // Update telemetry operation text
    const telemetryTitle = document.querySelector('[data-i18n="ui.operations.telemetry.title"]');
    const telemetryDesc = document.querySelector('[data-i18n="ui.operations.telemetry.description"]');
    const telemetryBtn = document.getElementById('telemetryBtn');

    if (telemetryTitle && telemetryDesc && telemetryBtn) {
        if (isJetBrains) {
            telemetryTitle.textContent = t('ui.operations.telemetry.title_jetbrains');
            telemetryDesc.textContent = t('ui.operations.telemetry.description_jetbrains');
            telemetryBtn.textContent = t('ui.operations.telemetry.button_jetbrains');
        } else {
            telemetryTitle.textContent = t('ui.operations.telemetry.title');
            telemetryDesc.textContent = t('ui.operations.telemetry.description');
            telemetryBtn.textContent = t('ui.operations.telemetry.button');
        }
    }

    // Hide/show database and workspace operations for JetBrains
    const databaseOperation = document.querySelector('.operation-item-compact:nth-child(2)');
    const workspaceOperation = document.querySelector('.operation-item-compact:nth-child(3)');

    if (databaseOperation && workspaceOperation) {
        if (isJetBrains) {
            databaseOperation.style.display = 'none';
            workspaceOperation.style.display = 'none';
        } else {
            databaseOperation.style.display = 'flex';
            workspaceOperation.style.display = 'flex';
        }
    }
}

// Toast management
let activeToasts = [];

// Simple message display function with no overlap
function showMessage(message, type = 'info') {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    // Calculate position based on existing toasts
    const topPosition = 20 + (activeToasts.length * 70); // 70px spacing between toasts

    toast.style.cssText = `
        position: fixed;
        top: ${topPosition}px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        opacity: 0;
        transition: all 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
        transform: translateX(100%);
    `;

    if (type === 'success') {
        toast.style.backgroundColor = '#28a745';
    } else if (type === 'error') {
        toast.style.backgroundColor = '#dc3545';
    } else {
        toast.style.backgroundColor = '#007bff';
    }

    document.body.appendChild(toast);
    activeToasts.push(toast);

    // Slide in and fade in
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, 100);

    // Remove after 3 seconds
    setTimeout(() => {
        removeToast(toast);
    }, 3000);
}

// Remove toast and reposition remaining toasts
function removeToast(toastToRemove) {
    const index = activeToasts.indexOf(toastToRemove);
    if (index > -1) {
        // Slide out and fade out
        toastToRemove.style.opacity = '0';
        toastToRemove.style.transform = 'translateX(100%)';

        // Remove from active toasts array
        activeToasts.splice(index, 1);

        // Reposition remaining toasts
        activeToasts.forEach((toast, i) => {
            const newTop = 20 + (i * 70);
            toast.style.top = `${newTop}px`;
        });

        // Remove from DOM after animation
        setTimeout(() => {
            if (toastToRemove.parentNode) {
                toastToRemove.parentNode.removeChild(toastToRemove);
            }
        }, 300);
    }
}

// Show loading overlay
function showLoading(message = null) {
    const loadingMessage = message || t('ui.loading.processing');
    elements.loadingText.textContent = loadingMessage;
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

// Check API status with improved retry mechanism
async function checkAPIStatus() {
    let retryCount = 0;
    const maxRetries = 15;
    let isChecking = false;

    const performCheck = async () => {
        if (isChecking) return; // Prevent multiple simultaneous checks
        isChecking = true;

        try {
            // Wait for pywebview to be ready
            if (typeof pywebview === 'undefined' || !pywebview.api) {
                if (retryCount < maxRetries) {
                    elements.apiStatus.textContent = '⏳ ' + t('ui.header.status_checking');
                    elements.apiStatus.style.background = 'rgba(255, 193, 7, 0.2)';
                    retryCount++;
                    isChecking = false;
                    setTimeout(performCheck, 1500); // Increased delay
                    return;
                } else {
                    elements.apiStatus.textContent = '❌ ' + t('ui.header.status_error');
                    elements.apiStatus.style.background = 'rgba(220, 53, 69, 0.2)';
                    isChecking = false;
                    return;
                }
            }

            // Try to call the API with timeout
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('API call timeout')), 5000)
            );

            const apiPromise = pywebview.api.get_status();
            const result = await Promise.race([apiPromise, timeoutPromise]);

            if (result && result.success) {
                // Show IDE count in status
                const ideCount = detectedIDEs.length;
                if (ideCount > 0) {
                    elements.apiStatus.textContent = `✅ ${t('ui.header.status_ready')} (${ideCount} IDEs)`;
                } else {
                    elements.apiStatus.textContent = '✅ ' + t('ui.header.status_ready');
                }
                elements.apiStatus.style.background = 'rgba(40, 167, 69, 0.2)';

                // Start auto-refresh for system info
                startAutoRefresh();
                console.log('API status check successful');
            } else {
                throw new Error('API returned unsuccessful status');
            }
        } catch (error) {
            console.error('API status check failed:', error);
            if (retryCount < maxRetries) {
                elements.apiStatus.textContent = '⏳ ' + t('ui.header.status_checking');
                elements.apiStatus.style.background = 'rgba(255, 193, 7, 0.2)';
                retryCount++;
                isChecking = false;
                setTimeout(performCheck, 2000);
            } else {
                elements.apiStatus.textContent = '❌ ' + t('ui.header.status_error');
                elements.apiStatus.style.background = 'rgba(220, 53, 69, 0.2)';
                console.error('API status check failed after maximum retries');
            }
        }

        isChecking = false;
    };

    await performCheck();
}

// Auto-refresh system information
let autoRefreshInterval = null;

function startAutoRefresh() {
    // Clear existing interval
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }

    // Refresh every 30 seconds
    autoRefreshInterval = setInterval(async () => {
        if (typeof pywebview !== 'undefined' && !isOperationRunning) {
            // If we have detected IDEs, refresh their information instead of reverting to default
            if (detectedIDEs && detectedIDEs.length > 0) {
                await refreshSystemInfo();
            } else {
                await loadSystemInfo();
            }

            // Also update IDE count if needed
            if (detectedIDEs.length > 0) {
                updateStatusWithIDECount();
            }
        }
    }, 30000);
}

// Update status with IDE count
function updateStatusWithIDECount() {
    if (elements.apiStatus && elements.apiStatus.textContent.includes('✅')) {
        const ideCount = detectedIDEs.length;
        if (ideCount > 0) {
            elements.apiStatus.textContent = `✅ ${t('ui.header.status_ready')} (${ideCount} IDEs)`;
        } else {
            elements.apiStatus.textContent = '✅ ' + t('ui.header.status_ready');
        }
    }
}

// Load system information
async function loadSystemInfo() {
    try {
        // Don't override detected IDEs display unless explicitly requested
        if (isShowingDetectedIDEs) {
            return;
        }

        // Check if pywebview is available
        if (typeof pywebview === 'undefined') {
            elements.systemInfo.innerHTML = `
                <div class="loading">${t('ui.system.loading')}</div>
            `;
            return;
        }

        const result = await pywebview.api.get_system_info();

        if (result.success) {
            displaySystemInfo(result.data);
        } else {
            elements.systemInfo.innerHTML = `
                <div class="error">
                    <strong>${t('messages.error.system_info_failed')}:</strong> ${result.message || result.error}
                </div>
            `;
        }
    } catch (error) {
        console.error('Failed to load system info:', error);
        elements.systemInfo.innerHTML = `
            <div class="error">
                <strong>${t('messages.error.system_info_failed')}:</strong> ${error.message}
            </div>
        `;
    }
}

// Refresh system information (preserves detected IDEs display)
async function refreshSystemInfo() {
    try {
        // If we have detected IDEs, refresh their information
        if (detectedIDEs && detectedIDEs.length > 0) {
            // Re-detect IDEs to get updated information
            const result = await pywebview.api.detect_ides();
            if (result.success && result.ides && result.ides.length > 0) {
                detectedIDEs = result.ides;
                displayDetectedIDEs(detectedIDEs);

                // Update IDE count
                if (elements.ideCount) {
                    elements.ideCount.textContent = detectedIDEs.length;
                }

                // Update status with IDE count
                updateStatusWithIDECount();

                showMessage(t('ui.system.refresh_success'), 'success');
            } else {
                // If detection fails, fall back to regular system info
                await loadSystemInfo();
            }
        } else {
            // No IDEs detected, just refresh regular system info
            await loadSystemInfo();
        }
    } catch (error) {
        console.error('Failed to refresh system info:', error);
        showMessage(t('ui.system.refresh_failed'), 'error');
        // Fall back to regular system info load
        await loadSystemInfo();
    }
}

// Display system information
function displaySystemInfo(data) {
    // Reset the flag since we're showing default system info
    isShowingDetectedIDEs = false;

    let infoItems = [];

    // Common info
    infoItems.push({
        label: t('ui.system.editor_type'),
        value: data.editor_type || 'VSCodium',
        icon: '🎯'
    });

    if (data.ide_type === 'jetbrains') {
        // JetBrains IDE info
        infoItems.push(
            {
                label: t('ui.system.jetbrains_config_path'),
                value: data.jetbrains_config_path || t('ui.system.not_found'),
                icon: '📁'
            },
            {
                label: t('ui.system.permanent_device_id_path'),
                value: data.permanent_device_id_path || t('ui.system.not_found'),
                icon: '🔑'
            },
            {
                label: t('ui.system.permanent_user_id_path'),
                value: data.permanent_user_id_path || t('ui.system.not_found'),
                icon: '👤'
            }
        );
    } else {
        // VSCode series info
        infoItems.push(
            {
                label: t('ui.system.storage_path'),
                value: data.storage_path,
                icon: '💾'
            },
            {
                label: t('ui.system.db_path'),
                value: data.db_path,
                icon: '🗃️'
            },
            {
                label: t('ui.system.machine_id_path'),
                value: data.machine_id_path,
                icon: '🔑'
            },
            {
                label: t('ui.system.workspace_storage_path'),
                value: data.workspace_storage_path,
                icon: '📁'
            }
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

    // Update footer editor names
    updateFooterEditorNames(data.editor_type || 'VSCodium');
}

// Note: Path generation is now handled by the backend with actual file system verification

// Display detected IDEs in system information with copy functionality
function displayDetectedIDEs(ides) {
    if (!ides || ides.length === 0) {
        // Show message when no IDEs detected
        isShowingDetectedIDEs = false;
        elements.systemInfo.innerHTML = `
            <div class="info-item">
                <div class="info-icon">❌</div>
                <div class="info-content">
                    <div class="info-label">${t('ui.system.no_ides_detected')}</div>
                    <div class="info-value">${t('ui.system.click_detect_button')}</div>
                </div>
            </div>
        `;
        return;
    }

    // Set flag to indicate we're showing detected IDEs
    isShowingDetectedIDEs = true;

    let infoSections = [];

    // Add each detected IDE as a separate section
    ides.forEach((ide, index) => {
        let ideItems = [];

        // Use verified paths from backend
        const requiredFields = [
            {
                key: 'editor_type',
                label: t('ui.system.editor_type'),
                value: `${ide.display_name || ide.name} ${ide.version ? `(${ide.version})` : ''}`,
                icon: ide.icon || '🎯'
            },
            {
                key: 'storage_path',
                label: t('ui.system.storage_path'),
                value: ide.storage_path || ide.config_path || t('ui.system.not_found'),
                icon: '📁'
            },
            {
                key: 'db_path',
                label: t('ui.system.db_path'),
                value: ide.db_path || t('ui.system.not_found'),
                icon: '🗃️'
            },
            {
                key: 'machine_id_path',
                label: t('ui.system.machine_id_path'),
                value: ide.machine_id_path || t('ui.system.not_found'),
                icon: '🔑'
            },
            {
                key: 'workspace_storage_path',
                label: t('ui.system.workspace_storage_path'),
                value: ide.workspace_storage_path || t('ui.system.not_found'),
                icon: '📁'
            }
        ];

        // Add all required fields
        requiredFields.forEach(field => {
            ideItems.push({
                label: field.label,
                value: field.value,
                icon: field.icon,
                copyable: field.value !== t('ui.system.not_found') && field.value !== null && field.value !== undefined
            });
        });

        // Add JetBrains specific paths if applicable
        if (ide.ide_type === 'jetbrains') {
            ideItems.push({
                label: t('ui.system.permanent_device_id_path'),
                value: ide.permanent_device_id_path || t('ui.system.not_found'),
                icon: '🔑',
                copyable: ide.permanent_device_id_path ? true : false
            });
            ideItems.push({
                label: t('ui.system.permanent_user_id_path'),
                value: ide.permanent_user_id_path || t('ui.system.not_found'),
                icon: '👤',
                copyable: ide.permanent_user_id_path ? true : false
            });
        }

        infoSections.push({
            title: `${t('ui.system.ide_section')} ${index + 1}: ${ide.display_name || ide.name}`,
            items: ideItems
        });
    });

    // Render the sections
    elements.systemInfo.innerHTML = infoSections.map(section => `
        <div class="ide-section">
            <div class="ide-section-header">
                <h4>${section.title}</h4>
            </div>
            <div class="ide-section-content">
                ${section.items.map((item, itemIndex) => `
                    <div class="info-item">
                        <div class="info-icon">${item.icon}</div>
                        <div class="info-content">
                            <div class="info-label">${item.label}</div>
                            <div class="info-value" title="${item.value}">${truncateText(item.value, 50)}</div>
                        </div>
                        ${item.copyable ? `<button class="copy-btn" data-copy-text="${item.value}" title="${t('ui.system.copy_tooltip')}">📋</button>` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');

    // Add event listeners for copy buttons
    setupCopyButtonListeners();
}

// Helper function to truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Setup event listeners for copy buttons
function setupCopyButtonListeners() {
    // Remove existing listeners first
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.removeEventListener('click', handleCopyClick);
    });

    // Add new listeners
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', handleCopyClick);
    });
}

// Handle copy button click
function handleCopyClick(event) {
    const button = event.target;
    const textToCopy = button.getAttribute('data-copy-text');
    if (textToCopy) {
        copyToClipboard(textToCopy);
    }
}

// Helper function to escape text for HTML attributes (no longer used for copy)
function escapeForAttribute(text) {
    return text
        .replace(/\\/g, '\\\\')  // Escape backslashes first
        .replace(/'/g, '&#39;')   // Escape single quotes
        .replace(/"/g, '&quot;'); // Escape double quotes
}

// Copy to clipboard function
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showMessage(t('ui.system.copy_success'), 'success');
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showMessage(t('ui.system.copy_success'), 'success');
        } catch (fallbackErr) {
            showMessage(t('ui.system.copy_failed'), 'error');
        }
        document.body.removeChild(textArea);
    }
}

// Check if API is available
function checkAPIAvailable() {
    if (typeof pywebview === 'undefined') {
        alert(t('messages.error.api_not_connected') || 'API未连接，请等待应用完全加载后再试！');
        return false;
    }
    return true;
}

// Modify telemetry IDs with preview
async function modifyTelemetry() {
    if (isOperationRunning || !checkAPIAvailable()) return;

    // Show preview of what will be changed
    await showOperationPreview('telemetry');

    showLoading(t('ui.loading.resetting'));

    try {
        const result = await pywebview.api.modify_telemetry();
        displayResults(t('ui.operations.telemetry.title'), result);

        // Refresh system info after operation
        setTimeout(() => {
            loadSystemInfo();
        }, 1000);
    } catch (error) {
        displayResults(t('ui.operations.telemetry.title'), {
            success: false,
            error: error.message,
            message: t('messages.error.telemetry_failed')
        });
    } finally {
        hideLoading();
    }
}

// Show operation preview
async function showOperationPreview(operationType) {
    try {
        const result = await pywebview.api.get_operation_preview(operationType);
        if (result.success && result.data) {
            displayOperationPreview(operationType, result.data);
        }
    } catch (error) {
        console.error('Failed to get operation preview:', error);
    }
}

// Display operation preview
function displayOperationPreview(operationType, previewData) {
    let previewContent = '';

    switch (operationType) {
        case 'telemetry':
            previewContent = `
                <div class="preview-section">
                    <h4>${t('ui.operations.preview.current_values')}</h4>
                    ${previewData.current ? Object.entries(previewData.current).map(([key, value]) => `
                        <div class="preview-item">
                            <span class="preview-label">${key}:</span>
                            <span class="preview-value current">${value || t('ui.operations.preview.not_found')}</span>
                        </div>
                    `).join('') : ''}
                </div>
                <div class="preview-section">
                    <h4>${t('ui.operations.preview.new_values')}</h4>
                    ${previewData.new ? Object.entries(previewData.new).map(([key, value]) => `
                        <div class="preview-item">
                            <span class="preview-label">${key}:</span>
                            <span class="preview-value new">${value}</span>
                        </div>
                    `).join('') : ''}
                </div>
            `;
            break;
        case 'database':
            previewContent = `
                <div class="preview-section">
                    <h4>${t('ui.operations.preview.database_info')}</h4>
                    <div class="preview-item">
                        <span class="preview-label">${t('ui.operations.preview.records_found')}:</span>
                        <span class="preview-value">${previewData.recordsFound || 0}</span>
                    </div>
                    <div class="preview-item">
                        <span class="preview-label">${t('ui.operations.preview.database_path')}:</span>
                        <span class="preview-value">${previewData.databasePath || t('ui.operations.preview.not_found')}</span>
                    </div>
                </div>
            `;
            break;
        case 'workspace':
            previewContent = `
                <div class="preview-section">
                    <h4>${t('ui.operations.preview.workspace_info')}</h4>
                    <div class="preview-item">
                        <span class="preview-label">${t('ui.operations.preview.files_found')}:</span>
                        <span class="preview-value">${previewData.filesFound || 0}</span>
                    </div>
                    <div class="preview-item">
                        <span class="preview-label">${t('ui.operations.preview.workspace_path')}:</span>
                        <span class="preview-value">${previewData.workspacePath || t('ui.operations.preview.not_found')}</span>
                    </div>
                </div>
            `;
            break;
    }

    // Show preview in a temporary overlay
    showPreviewModal(previewContent);
}

// Show preview modal
function showPreviewModal(content) {
    const modal = document.createElement('div');
    modal.className = 'preview-modal-overlay';
    modal.innerHTML = `
        <div class="preview-modal">
            <div class="preview-modal-header">
                <h3>${t('ui.operations.preview.title')}</h3>
                <button class="preview-modal-close" onclick="closePreviewModal()">✕</button>
            </div>
            <div class="preview-modal-body">
                ${content}
            </div>
            <div class="preview-modal-footer">
                <button class="btn btn-secondary" onclick="closePreviewModal()">${t('ui.operations.preview.close')}</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Auto-close after 5 seconds
    setTimeout(() => {
        closePreviewModal();
    }, 5000);
}

// Close preview modal
function closePreviewModal() {
    const modal = document.querySelector('.preview-modal-overlay');
    if (modal) {
        modal.remove();
    }
}

// Clean database with preview
async function cleanDatabase() {
    if (isOperationRunning || !checkAPIAvailable()) return;

    // Show preview of what will be cleaned
    await showOperationPreview('database');

    showLoading(t('ui.loading.cleaning'));

    try {
        const result = await pywebview.api.clean_database();
        displayResults(t('ui.operations.database.title'), result);

        // Refresh system info after operation
        setTimeout(() => {
            loadSystemInfo();
        }, 1000);
    } catch (error) {
        displayResults(t('ui.operations.database.title'), {
            success: false,
            error: error.message,
            message: t('messages.error.database_failed')
        });
    } finally {
        hideLoading();
    }
}

// Clean workspace with preview
async function cleanWorkspace() {
    if (isOperationRunning || !checkAPIAvailable()) return;

    // Show preview of what will be cleaned
    await showOperationPreview('workspace');

    showLoading(t('ui.loading.cleaning'));

    try {
        const result = await pywebview.api.clean_workspace();
        displayResults(t('ui.operations.workspace.title'), result);

        // Refresh system info after operation
        setTimeout(() => {
            loadSystemInfo();
        }, 1000);
    } catch (error) {
        displayResults(t('ui.operations.workspace.title'), {
            success: false,
            error: error.message,
            message: t('messages.error.workspace_failed')
        });
    } finally {
        hideLoading();
    }
}

// Run all operations with preview
async function runAllOperations() {
    if (isOperationRunning || !checkAPIAvailable()) return;

    showLoading(t('ui.loading.processing'));

    try {
        const result = await pywebview.api.run_all_operations();
        displayAllResults(result);

        // Refresh system info after all operations
        setTimeout(() => {
            loadSystemInfo();
            // Re-detect IDEs to update counts
            autoDetectIDEsOnStartup();
        }, 2000);
    } catch (error) {
        displayResults(t('ui.operations.all.title'), {
            success: false,
            error: error.message,
            message: t('messages.error.some_operations_failed')
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
            <p><strong>${t('ui.results.status')}:</strong> ${result.message}</p>
    `;

    if (result.success && result.data) {
        content += formatResultData(result.data);
    }

    if (!result.success && result.error) {
        content += `<p><strong>${t('ui.results.error')}:</strong> ${result.error}</p>`;
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
            { key: 'telemetry', name: t('ui.operations.telemetry.title') },
            { key: 'database', name: t('ui.operations.database.title') },
            { key: 'workspace', name: t('ui.operations.workspace.title') }
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
    detectBtn.title = t('ui.loading.detecting');

    // Show status
    detectStatus.textContent = t('ui.loading.detecting');
    detectStatus.className = 'detect-status show';

    try {
        const result = await pywebview.api.detect_ides();

        if (result.success) {
            detectedIDEs = result.ides || [];

            // Update IDE count display
            elements.ideCount.textContent = detectedIDEs.length;

            // Update system info to show all detected IDEs
            displayDetectedIDEs(detectedIDEs);

            // Show success status with translation
            const successMsg = t('messages.info.ides_detected', { count: result.count || detectedIDEs.length });
            detectStatus.textContent = `✅ ${successMsg}`;
            detectStatus.className = 'detect-status show success';

            // Update button
            detectBtn.textContent = '🔍';
            detectBtn.title = t('ui.header.detect_tooltip');

            console.log('IDE detection successful:', result);

            // Show success message
            showMessage(successMsg, 'success');

            // Update status with IDE count
            updateStatusWithIDECount();
        } else {
            detectedIDEs = [];
            elements.ideCount.textContent = '0';

            // Show error status
            detectStatus.textContent = `❌ ${result.message || t('messages.error.ide_detection_failed')}`;
            detectStatus.className = 'detect-status show error';

            // Reset button
            detectBtn.textContent = '🔍';
            detectBtn.title = t('ui.header.detect_tooltip');

            console.error('IDE detection failed:', result);
            showMessage(result.message || t('messages.error.ide_detection_failed'), 'error');

            // Update status with IDE count
            updateStatusWithIDECount();
        }
    } catch (error) {
        console.error('Error detecting IDEs:', error);

        // Show error status
        detectStatus.textContent = `❌ ${t('messages.error.ide_detection_failed')}`;
        detectStatus.className = 'detect-status show error';

        // Reset button
        detectBtn.textContent = '🔍';
        detectBtn.title = t('ui.header.detect_tooltip');

        showMessage(t('messages.error.ide_detection_failed'), 'error');
    } finally {
        detectBtn.disabled = false;
        isDetecting = false;

        // Hide status after 5 seconds
        setTimeout(() => {
            detectStatus.textContent = 'By vagmr';
            detectStatus.className = 'detect-status';
        }, 5000);
    }
}

// This function is no longer needed as we removed the editor selector

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
