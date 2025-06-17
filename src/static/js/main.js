document.addEventListener('DOMContentLoaded', function() {
    // 初始化代码编辑器
    initCodeEditors();
    
    // 初始化标签页切换
    initTabs();
    
    // 绑定功能按钮
    bindButtons();
    
    // 初始化WebSocket连接（用于实时反馈）
    initWebSocketConnection();
});

// 全局变量
let codeCompletionEditor = null;
let codeCheckEditor = null;
let ws = null;
let streamingResponse = false;
let userSettings = loadUserSettings();

/**
 * 初始化代码编辑器
 */
function initCodeEditors() {
    // 如果CodeMirror可用，使用它来增强文本域
    if (typeof CodeMirror !== 'undefined') {
        const completionTextarea = document.getElementById('code-editor');
        if (completionTextarea) {
            codeCompletionEditor = CodeMirror.fromTextArea(completionTextarea, {
                mode: 'python',
                theme: userSettings.darkMode ? 'dracula' : 'default',
                lineNumbers: true,
                autoCloseBrackets: true,
                matchBrackets: true,
                indentUnit: 4,
                tabSize: 4,
                lineWrapping: true,
                extraKeys: {"Ctrl-Space": "autocomplete"},
                hintOptions: {
                    completeSingle: false
                }
            });
            
            // 监听编辑器变化，实现实时补全
            codeCompletionEditor.on('change', debounce(function(cm) {
                if (!streamingResponse && userSettings.realTimeCompletion) {
                    requestCompletion(cm.getValue(), true);
                }
            }, 500));
        }
        
        // 错误检查编辑器
        const checkTextarea = document.getElementById('check-editor');
        if (checkTextarea) {
            codeCheckEditor = CodeMirror.fromTextArea(checkTextarea, {
                mode: 'python',
                theme: userSettings.darkMode ? 'dracula' : 'default',
                lineNumbers: true,
                autoCloseBrackets: true,
                matchBrackets: true,
                indentUnit: 4,
                tabSize: 4,
                lineWrapping: true
            });
        }
        
        // 设置语言下拉菜单改变事件
        const langSelector = document.getElementById('language-selector');
        if (langSelector) {
            langSelector.addEventListener('change', function() {
                const mode = getModeForLanguage(this.value);
                if (codeCompletionEditor) {
                    codeCompletionEditor.setOption('mode', mode);
                }
            });
        }
        
        // 错误检查语言选择器
        const checkLangSelector = document.getElementById('check-language-selector');
        if (checkLangSelector) {
            checkLangSelector.addEventListener('change', function() {
                const mode = getModeForLanguage(this.value);
                if (codeCheckEditor) {
                    codeCheckEditor.setOption('mode', mode);
                }
            });
        }
    } else {
        console.warn('CodeMirror未加载，使用普通文本域');
    }
}

/**
 * 初始化标签页切换
 */
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有活动标签
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // 隐藏所有内容
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // 激活当前选中的标签和内容
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
            
            // 如果有编辑器，触发刷新以解决布局问题
            if (codeCompletionEditor && tabId === 'code-completion') {
                setTimeout(() => codeCompletionEditor.refresh(), 10);
            }
            if (codeCheckEditor && tabId === 'error-check') {
                setTimeout(() => codeCheckEditor.refresh(), 10);
            }
            
            // 保存用户偏好
            userSettings.lastActiveTab = tabId;
            saveUserSettings();
        });
    });
    
    // 根据保存的用户偏好加载上次的标签页
    if (userSettings.lastActiveTab) {
        const lastTab = document.querySelector(`[data-tab="${userSettings.lastActiveTab}"]`);
        if (lastTab) {
            lastTab.click();
        }
    }
}

/**
 * 绑定功能按钮
 */
function bindButtons() {
    // 代码补全按钮
    const completeBtn = document.getElementById('complete-btn');
    if (completeBtn) {
        completeBtn.addEventListener('click', function() {
            let code = codeCompletionEditor ? 
                codeCompletionEditor.getValue() : 
                document.getElementById('code-editor').value;
                
            requestCompletion(code, false);
        });
    }
    
    // 错误检查按钮
    const checkBtn = document.getElementById('check-btn');
    if (checkBtn) {
        checkBtn.addEventListener('click', function() {
            let code = codeCheckEditor ? 
                codeCheckEditor.getValue() : 
                document.getElementById('check-editor').value;
                
            requestErrorCheck(code);
        });
    }
    
    // 分析文件按钮
    const analyzeFileBtn = document.getElementById('analyze-file-btn');
    if (analyzeFileBtn) {
        analyzeFileBtn.addEventListener('click', function() {
            const filePath = document.getElementById('file-path').value;
            if (filePath) {
                requestFileAnalysis(filePath);
            } else {
                showMessage('请输入文件路径', 'error');
            }
        });
    }
    
    // 分析项目按钮
    const analyzeProjectBtn = document.getElementById('analyze-project-btn');
    if (analyzeProjectBtn) {
        analyzeProjectBtn.addEventListener('click', function() {
            const projectPath = document.getElementById('project-path').value;
            if (projectPath) {
                requestProjectAnalysis(projectPath);
            } else {
                showMessage('请输入项目路径', 'error');
            }
        });
    }
    
    // 知识库搜索按钮
    const kbSearchBtn = document.getElementById('kb-search-btn');
    if (kbSearchBtn) {
        kbSearchBtn.addEventListener('click', function() {
            const query = document.getElementById('kb-query').value;
            if (query) {
                searchKnowledgeBase(query);
            } else {
                showMessage('请输入搜索内容', 'error');
            }
        });
    }
    
    // 上传文档表单
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('file-upload');
            if (fileInput.files.length > 0) {
                uploadDocument(fileInput.files[0]);
            } else {
                showMessage('请选择要上传的文档', 'error');
            }
        });
    }
}

/**
 * 初始化WebSocket连接
 */
function initWebSocketConnection() {
    // 检查浏览器是否支持WebSocket
    if (window.WebSocket) {
        // 从当前URL构建WebSocket地址
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/completion`;
        
        try {
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('已连接到实时补全服务');
            };
            
            ws.onmessage = function(event) {
                handleStreamingResponse(event.data);
            };
            
            ws.onclose = function() {
                console.log('已断开与实时补全服务的连接');
                // 尝试重新连接
                setTimeout(initWebSocketConnection, 2000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket错误:', error);
            };
        } catch (e) {
            console.error('无法建立WebSocket连接:', e);
        }
    } else {
        console.warn('浏览器不支持WebSocket，无法使用实时补全功能');
    }
}

/**
 * 请求代码补全
 * @param {string} code - 代码内容
 * @param {boolean} isRealTime - 是否为实时请求
 */
function requestCompletion(code, isRealTime = false) {
    if (!code) return;
    
    const language = document.getElementById('language-selector').value;
    const outputElem = document.getElementById('completion-output');
    
    if (isRealTime && !ws) {
        // 如果是实时请求但WebSocket不可用，则不执行
        return;
    }
    
    // 设置请求状态
    streamingResponse = true;
    
    // 显示加载指示器
    if (!isRealTime) {
        outputElem.textContent = '正在生成补全...';
    }
    
    if (isRealTime && ws && ws.readyState === WebSocket.OPEN) {
        // 通过WebSocket发送实时请求
        ws.send(JSON.stringify({
            action: 'completion',
            code: code,
            language: language
        }));
    } else {
        // 通过HTTP请求
        fetch('/api/code/completion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                language: language
            })
        })
        .then(response => response.json())
        .then(data => {
            streamingResponse = false;
            if (data.success) {
                outputElem.textContent = data.completion;
                highlightOutputCode(outputElem, language);
            } else {
                outputElem.textContent = '错误: ' + data.error;
            }
        })
        .catch(error => {
            streamingResponse = false;
            outputElem.textContent = '请求失败: ' + error.message;
            console.error('请求失败:', error);
        });
    }
}

/**
 * 处理流式响应
 * @param {string} data - 接收到的数据
 */
function handleStreamingResponse(data) {
    try {
        const response = JSON.parse(data);
        
        if (response.action === 'completion') {
            // 更新补全输出
            const outputElem = document.getElementById('completion-output');
            
            if (response.status === 'streaming') {
                // 追加内容
                outputElem.textContent += response.token;
            } else if (response.status === 'done') {
                // 完成
                streamingResponse = false;
                // 高亮显示代码
                highlightOutputCode(outputElem, response.language || 'python');
            } else if (response.status === 'error') {
                streamingResponse = false;
                outputElem.textContent = '错误: ' + response.error;
            }
        }
    } catch (e) {
        console.error('处理WebSocket响应失败:', e);
    }
}

/**
 * 请求代码错误检查
 * @param {string} code - 代码内容
 */
function requestErrorCheck(code) {
    if (!code) return;
    
    const language = document.getElementById('check-language-selector').value;
    const outputElem = document.getElementById('check-output');
    
    // 显示加载指示器
    outputElem.innerHTML = '<div class="loading">正在检查代码...</div>';
    
    fetch('/api/code/check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: code,
            language: language
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 清空输出容器
            outputElem.innerHTML = '';
            
            if (data.issues && data.issues.length > 0) {
                // 创建问题列表
                const issueList = document.createElement('ul');
                issueList.className = 'issue-list';
                
                data.issues.forEach(issue => {
                    const issueItem = document.createElement('li');
                    issueItem.className = `issue-item ${issue.severity}`;
                    
                    const issueTitle = document.createElement('div');
                    issueTitle.className = 'issue-title';
                    issueTitle.innerHTML = `<span class="issue-line">第 ${issue.line} 行:</span> ${issue.message}`;
                    
                    const issueCode = document.createElement('pre');
                    issueCode.className = 'issue-code';
                    issueCode.textContent = issue.code_snippet || '';
                    
                    const issueFix = document.createElement('div');
                    issueFix.className = 'issue-fix';
                    issueFix.innerHTML = issue.fix_suggestion ? 
                        `<strong>修复建议:</strong> ${issue.fix_suggestion}` : '';
                    
                    issueItem.appendChild(issueTitle);
                    issueItem.appendChild(issueCode);
                    if (issue.fix_suggestion) {
                        issueItem.appendChild(issueFix);
                    }
                    
                    issueList.appendChild(issueItem);
                });
                
                outputElem.appendChild(issueList);
            } else {
                // 没有问题
                outputElem.innerHTML = '<div class="success-message">未发现问题，代码看起来不错!</div>';
            }
        } else {
            outputElem.innerHTML = `<div class="error-message">错误: ${data.error}</div>`;
        }
    })
    .catch(error => {
        outputElem.innerHTML = `<div class="error-message">请求失败: ${error.message}</div>`;
        console.error('请求失败:', error);
    });
}

/**
 * 请求文件分析
 * @param {string} filePath - 文件路径
 */
function requestFileAnalysis(filePath) {
    const outputElem = document.getElementById('analysis-output');
    
    // 显示加载指示器
    outputElem.innerHTML = '<div class="loading">正在分析文件...</div>';
    
    fetch('/api/code/analyze/file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            file_path: filePath
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 渲染分析结果
            renderAnalysisResult(data.analysis, outputElem);
        } else {
            outputElem.innerHTML = `<div class="error-message">错误: ${data.error}</div>`;
        }
    })
    .catch(error => {
        outputElem.innerHTML = `<div class="error-message">请求失败: ${error.message}</div>`;
        console.error('请求失败:', error);
    });
}

/**
 * 请求项目分析
 * @param {string} projectPath - 项目路径
 */
function requestProjectAnalysis(projectPath) {
    const outputElem = document.getElementById('analysis-output');
    
    // 显示加载指示器
    outputElem.innerHTML = '<div class="loading">正在分析项目，这可能需要一些时间...</div>';
    
    fetch('/api/code/analyze/project', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            project_path: projectPath
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 渲染分析结果
            renderAnalysisResult(data.analysis, outputElem);
        } else {
            outputElem.innerHTML = `<div class="error-message">错误: ${data.error}</div>`;
        }
    })
    .catch(error => {
        outputElem.innerHTML = `<div class="error-message">请求失败: ${error.message}</div>`;
        console.error('请求失败:', error);
    });
}

/**
 * 渲染代码分析结果
 * @param {Object} analysis - 分析结果数据
 * @param {Element} container - 容器元素
 */
function renderAnalysisResult(analysis, container) {
    // 清空容器
    container.innerHTML = '';
    
    // 创建分析结果DOM结构
    const resultElem = document.createElement('div');
    resultElem.className = 'analysis-result-container';
    
    // 摘要部分
    const summaryElem = document.createElement('div');
    summaryElem.className = 'analysis-summary';
    summaryElem.innerHTML = `
        <h3>分析摘要</h3>
        <div class="summary-item">
            <span class="summary-label">复杂度得分:</span>
            <span class="summary-value ${getComplexityClass(analysis.complexity_score)}">${analysis.complexity_score}/10</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">可维护性:</span>
            <span class="summary-value ${getMaintainabilityClass(analysis.maintainability)}">${analysis.maintainability}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">代码行数:</span>
            <span class="summary-value">${analysis.total_lines}</span>
        </div>
    `;
    
    // 问题列表
    const issuesElem = document.createElement('div');
    issuesElem.className = 'analysis-issues';
    issuesElem.innerHTML = `<h3>发现的问题 (${analysis.issues.length})</h3>`;
    
    if (analysis.issues.length > 0) {
        const issueList = document.createElement('ul');
        issueList.className = 'issue-list';
        
        analysis.issues.forEach(issue => {
            const issueItem = document.createElement('li');
            issueItem.className = `issue-item ${issue.severity}`;
            
            const issueTitle = document.createElement('div');
            issueTitle.className = 'issue-title';
            let locationInfo = issue.file ? `${issue.file}:` : '';
            locationInfo += issue.line ? `第 ${issue.line} 行` : '';
            
            issueTitle.innerHTML = locationInfo ? 
                `<span class="issue-location">${locationInfo}:</span> ${issue.message}` :
                issue.message;
            
            const issueDescription = document.createElement('div');
            issueDescription.className = 'issue-description';
            issueDescription.textContent = issue.description || '';
            
            issueItem.appendChild(issueTitle);
            issueItem.appendChild(issueDescription);
            
            issueList.appendChild(issueItem);
        });
        
        issuesElem.appendChild(issueList);
    } else {
        issuesElem.innerHTML += '<div class="success-message">未发现问题!</div>';
    }
    
    // 代码结构
    const structureElem = document.createElement('div');
    structureElem.className = 'analysis-structure';
    structureElem.innerHTML = `<h3>代码结构</h3>`;
    
    if (analysis.structure) {
        const structureList = document.createElement('ul');
        structureList.className = 'structure-list';
        
        Object.entries(analysis.structure).forEach(([category, items]) => {
            const categoryItem = document.createElement('li');
            categoryItem.className = 'structure-category';
            
            const categoryTitle = document.createElement('div');
            categoryTitle.className = 'structure-category-title';
            categoryTitle.textContent = `${category} (${items.length})`;
            
            const itemsList = document.createElement('ul');
            itemsList.className = 'structure-items';
            
            items.forEach(item => {
                const listItem = document.createElement('li');
                listItem.textContent = item.name;
                if (item.location) {
                    listItem.setAttribute('title', item.location);
                }
                itemsList.appendChild(listItem);
            });
            
            categoryItem.appendChild(categoryTitle);
            categoryItem.appendChild(itemsList);
            structureList.appendChild(categoryItem);
        });
        
        structureElem.appendChild(structureList);
    } else {
        structureElem.innerHTML += '<div class="info-message">无结构信息可用</div>';
    }
    
    // 组合所有元素
    resultElem.appendChild(summaryElem);
    resultElem.appendChild(issuesElem);
    resultElem.appendChild(structureElem);
    
    // 添加到容器
    container.appendChild(resultElem);
}

/**
 * 搜索知识库
 * @param {string} query - 搜索查询
 */
function searchKnowledgeBase(query) {
    const resultsElem = document.getElementById('kb-results');
    
    // 显示加载指示器
    resultsElem.innerHTML = '<div class="loading">正在搜索...</div>';
    
    fetch('/api/kb/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: query
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 清空结果容器
            resultsElem.innerHTML = '';
            
            if (data.results && data.results.length > 0) {
                // 创建结果列表
                const resultsList = document.createElement('div');
                resultsList.className = 'kb-results-list';
                
                data.results.forEach((result, index) => {
                    const resultItem = document.createElement('div');
                    resultItem.className = 'kb-result-item';
                    
                    const resultHeader = document.createElement('div');
                    resultHeader.className = 'kb-result-header';
                    
                    const resultTitle = document.createElement('h4');
                    resultTitle.className = 'kb-result-title';
                    resultTitle.textContent = result.title || `结果 ${index + 1}`;
                    
                    const resultScore = document.createElement('span');
                    resultScore.className = 'kb-result-score';
                    resultScore.textContent = `相关度: ${Math.round(result.score * 100)}%`;
                    
                    resultHeader.appendChild(resultTitle);
                    resultHeader.appendChild(resultScore);
                    
                    const resultContent = document.createElement('div');
                    resultContent.className = 'kb-result-content';
                    resultContent.textContent = result.text || '';
                    
                    const resultMeta = document.createElement('div');
                    resultMeta.className = 'kb-result-meta';
                    
                    if (result.metadata && result.metadata.source) {
                        const resultSource = document.createElement('span');
                        resultSource.className = 'kb-result-source';
                        resultSource.textContent = `来源: ${result.metadata.source}`;
                        resultMeta.appendChild(resultSource);
                    }
                    
                    resultItem.appendChild(resultHeader);
                    resultItem.appendChild(resultContent);
                    resultItem.appendChild(resultMeta);
                    
                    resultsList.appendChild(resultItem);
                });
                
                resultsElem.appendChild(resultsList);
            } else {
                resultsElem.innerHTML = '<div class="info-message">未找到相关内容</div>';
            }
        } else {
            resultsElem.innerHTML = `<div class="error-message">错误: ${data.error}</div>`;
        }
    })
    .catch(error => {
        resultsElem.innerHTML = `<div class="error-message">请求失败: ${error.message}</div>`;
        console.error('请求失败:', error);
    });
}

/**
 * 上传文档到知识库
 * @param {File} file - 要上传的文件
 */
function uploadDocument(file) {
    const uploadForm = document.getElementById('upload-form');
    const formData = new FormData();
    formData.append('file', file);
    
    // 显示上传状态
    showMessage('正在上传文档...', 'info');
    
    fetch('/api/kb/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 上传成功
            showMessage(`文档 "${file.name}" 上传成功！`, 'success');
            // 清空文件输入
            document.getElementById('file-upload').value = '';
        } else {
            // 上传失败
            showMessage(`上传失败: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        showMessage(`请求错误: ${error.message}`, 'error');
        console.error('上传请求失败:', error);
    });
}

/**
 * 显示消息提示
 * @param {string} message - 消息内容 
 * @param {string} type - 消息类型 (info, success, error, warning)
 */
function showMessage(message, type = 'info') {
    // 检查是否已有提示框容器
    let container = document.querySelector('.message-container');
    
    if (!container) {
        // 创建容器
        container = document.createElement('div');
        container.className = 'message-container';
        document.body.appendChild(container);
    }
    
    // 创建提示框
    const messageBox = document.createElement('div');
    messageBox.className = `message ${type}`;
    messageBox.textContent = message;
    
    // 添加关闭按钮
    const closeBtn = document.createElement('span');
    closeBtn.className = 'message-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', () => {
        container.removeChild(messageBox);
    });
    
    messageBox.appendChild(closeBtn);
    container.appendChild(messageBox);
    
    // 3秒后自动关闭
    setTimeout(() => {
        if (container.contains(messageBox)) {
            container.removeChild(messageBox);
        }
    }, 3000);
}

/**
 * 高亮显示输出的代码
 * @param {Element} element - 包含代码的元素
 * @param {string} language - 代码语言
 */
function highlightOutputCode(element, language) {
    if (typeof hljs !== 'undefined') {
        // 创建pre和code元素
        const pre = document.createElement('pre');
        const code = document.createElement('code');
        
        // 设置语言类
        code.className = `language-${language}`;
        code.textContent = element.textContent;
        
        // 清空并重建结构
        element.innerHTML = '';
        pre.appendChild(code);
        element.appendChild(pre);
        
        // 应用高亮
        hljs.highlightBlock(code);
    }
}

/**
 * 获取编程语言对应的CodeMirror模式
 * @param {string} language - 编程语言名
 * @returns {string} CodeMirror模式
 */
function getModeForLanguage(language) {
    const modeMap = {
        'python': 'python',
        'javascript': 'javascript',
        'typescript': 'text/typescript',
        'java': 'text/x-java',
        'c': 'text/x-csrc',
        'cpp': 'text/x-c++src',
        'csharp': 'text/x-csharp',
        'go': 'text/x-go',
        'rust': 'rust',
        'php': 'php',
        'ruby': 'ruby',
        'swift': 'swift'
    };
    
    return modeMap[language] || language;
}

/**
 * 加载用户设置
 * @returns {Object} 用户设置对象
 */
function loadUserSettings() {
    // 从本地存储获取设置
    const settings = localStorage.getItem('codeAssistantSettings');
    
    // 默认设置
    const defaultSettings = {
        darkMode: false,
        realTimeCompletion: true,
        fontSize: 14,
        tabSize: 4,
        lastActiveTab: null
    };
    
    // 如果有保存的设置，解析它
    if (settings) {
        try {
            return {...defaultSettings, ...JSON.parse(settings)};
        } catch (e) {
            console.error('解析设置失败:', e);
        }
    }
    
    return defaultSettings;
}

/**
 * 保存用户设置
 */
function saveUserSettings() {
    localStorage.setItem('codeAssistantSettings', JSON.stringify(userSettings));
}

/**
 * 设置深色模式
 * @param {boolean} enabled - 是否启用深色模式
 */
function setDarkMode(enabled) {
    userSettings.darkMode = enabled;
    
    // 更新主题
    document.body.classList.toggle('dark-mode', enabled);
    
    // 更新编辑器主题
    if (codeCompletionEditor) {
        codeCompletionEditor.setOption('theme', enabled ? 'dracula' : 'default');
    }
    if (codeCheckEditor) {
        codeCheckEditor.setOption('theme', enabled ? 'dracula' : 'default');
    }
    
    // 保存设置
    saveUserSettings();
}

/**
 * 获取复杂度评分的CSS类
 * @param {number} score - 复杂度得分
 * @returns {string} CSS类名
 */
function getComplexityClass(score) {
    if (score <= 3) return 'good';
    if (score <= 7) return 'moderate';
    return 'bad';
}

/**
 * 获取可维护性评级的CSS类
 * @param {string} rating - 可维护性评级
 * @returns {string} CSS类名
 */
function getMaintainabilityClass(rating) {
    rating = rating.toLowerCase();
    if (rating.includes('高') || rating.includes('good')) return 'good';
    if (rating.includes('中') || rating.includes('moderate')) return 'moderate';
    return 'bad';
}

/**
 * 防抖函数，避免频繁调用
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间(ms)
 * @returns {Function} 包装后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
} 