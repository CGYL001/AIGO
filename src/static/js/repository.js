/**
 * 仓库管理页面脚本
 */
document.addEventListener('DOMContentLoaded', function() {
    // 初始化标签页切换
    initTabs();
    
    // 绑定按钮事件
    bindButtons();
    
    // 初始化权限状态
    initAuthStatus();
    
    // 加载本地仓库列表
    loadLocalRepositories();
    
    // 初始化仓库权限管理页面
    initPermissionsTabs();
});

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
        });
    });
}

/**
 * 绑定按钮事件
 */
function bindButtons() {
    // 平台认证按钮
    const authBtn = document.getElementById('auth-btn');
    if (authBtn) {
        authBtn.addEventListener('click', authenticatePlatform);
    }
    
    // 获取仓库列表按钮
    const listReposBtn = document.getElementById('list-repos-btn');
    if (listReposBtn) {
        listReposBtn.addEventListener('click', listRemoteRepositories);
    }
    
    // 权限模式切换
    const modeRadios = document.querySelectorAll('input[name="auth-mode"]');
    modeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            setAuthMode(this.value);
        });
    });
    
    // 重置信任状态按钮
    const resetTrustBtn = document.getElementById('reset-trust-btn');
    if (resetTrustBtn) {
        resetTrustBtn.addEventListener('click', resetTrustStatus);
    }
    
    // 对话框按钮
    document.getElementById('confirm-yes').addEventListener('click', confirmDialogYes);
    document.getElementById('confirm-no').addEventListener('click', hideConfirmDialog);
    
    document.getElementById('push-confirm').addEventListener('click', confirmPush);
    document.getElementById('push-cancel').addEventListener('click', hidePushDialog);
    
    document.getElementById('clone-confirm').addEventListener('click', confirmClone);
    document.getElementById('clone-cancel').addEventListener('click', hideCloneDialog);
    
    // 为本地仓库列表中的按钮绑定事件
    bindLocalRepoButtons();
}

/**
 * 为本地仓库列表中的按钮绑定事件
 */
function bindLocalRepoButtons() {
    // 拉取按钮
    document.querySelectorAll('.btn-pull').forEach(btn => {
        btn.addEventListener('click', function() {
            const repoPath = this.getAttribute('data-repo-path');
            pullRepository(repoPath);
        });
    });
    
    // 推送按钮
    document.querySelectorAll('.btn-push').forEach(btn => {
        btn.addEventListener('click', function() {
            const repoPath = this.getAttribute('data-repo-path');
            showPushDialog(repoPath);
        });
    });
    
    // 删除按钮
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', function() {
            const repoPath = this.getAttribute('data-repo-path');
            const repoName = this.closest('.repo-item').querySelector('.repo-name').textContent;
            showConfirmDialog(`确定要删除本地仓库 "${repoName}" 吗？`, function() {
                deleteRepository(repoPath);
            });
        });
    });
}

/**
 * 初始化权限状态
 */
function initAuthStatus() {
    fetch('/api/auth/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateAuthStatus(data.mode, data.trust_status);
            }
        })
        .catch(error => {
            console.error('获取权限状态失败:', error);
        });
}

/**
 * 更新权限状态显示
 */
function updateAuthStatus(mode, trustStatus) {
    // 更新模式选择
    document.getElementById(`mode-${mode}`).checked = true;
    
    // 更新状态显示
    document.getElementById('current-mode').textContent = mode === 'strict' ? '严格模式' : '信任模式';
    document.getElementById('trusted-status').textContent = trustStatus.trusted ? '已信任' : '未信任';
    document.getElementById('confirm-count').textContent = `${trustStatus.confirm_count}/${trustStatus.required_count}`;
}

/**
 * 设置权限模式
 */
function setAuthMode(mode) {
    fetch('/api/auth/mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            mode: mode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            // 刷新权限状态
            initAuthStatus();
        } else {
            showMessage(data.error || '设置权限模式失败', 'error');
        }
    })
    .catch(error => {
        showMessage('请求失败: ' + error.message, 'error');
    });
}

/**
 * 重置信任状态
 */
function resetTrustStatus() {
    // 切换到严格模式，然后再切换回信任模式
    fetch('/api/auth/mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            mode: 'strict'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 如果当前是信任模式，再切换回去
            if (document.getElementById('mode-trust').checked) {
                setAuthMode('trust');
            } else {
                // 刷新权限状态
                initAuthStatus();
                showMessage('已重置信任状态', 'success');
            }
        } else {
            showMessage(data.error || '重置信任状态失败', 'error');
        }
    })
    .catch(error => {
        showMessage('请求失败: ' + error.message, 'error');
    });
}

/**
 * 加载本地仓库列表
 */
function loadLocalRepositories() {
    fetch('/api/repository/local')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderLocalRepositories(data.repositories);
            } else {
                showMessage(data.error || '获取本地仓库列表失败', 'error');
            }
        })
        .catch(error => {
            showMessage('请求失败: ' + error.message, 'error');
        });
}

/**
 * 渲染本地仓库列表
 */
function renderLocalRepositories(repositories) {
    const container = document.getElementById('local-repo-list');
    
    if (!repositories || repositories.length === 0) {
        container.innerHTML = `
            <div class="empty-message">
                <p>暂无本地仓库</p>
                <p>请从远程仓库克隆或导入本地文件夹</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    repositories.forEach(repo => {
        html += `
            <div class="repo-item" data-repo-path="${repo.path}">
                <div class="repo-header">
                    <h4 class="repo-name">${repo.name}</h4>
                    <span class="repo-platform ${repo.platform}">${repo.platform}</span>
                </div>
                <div class="repo-info">
                    <p class="repo-path"><strong>路径:</strong> ${repo.path}</p>
                    <p class="repo-branch"><strong>当前分支:</strong> ${repo.current_branch}</p>
                    ${repo.last_commit ? `
                    <p class="repo-commit"><strong>最后提交:</strong> ${repo.last_commit.message} (${repo.last_commit.author})</p>
                    ` : ''}
                </div>
                <div class="repo-actions">
                    <button class="btn btn-pull" data-repo-path="${repo.path}">拉取更新</button>
                    <button class="btn btn-push" data-repo-path="${repo.path}">推送更改</button>
                    <button class="btn btn-delete" data-repo-path="${repo.path}">删除仓库</button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // 重新绑定按钮事件
    bindLocalRepoButtons();
}

/**
 * 平台认证
 */
function authenticatePlatform() {
    const platform = document.getElementById('platform-select').value;
    const token = document.getElementById('auth-token').value;
    
    if (!token) {
        showMessage('请输入访问令牌', 'error');
        return;
    }
    
    const statusElem = document.getElementById('auth-status');
    statusElem.innerHTML = '<div class="loading">正在认证...</div>';
    
    fetch('/api/repository/authenticate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            platform: platform,
            credentials: {
                token: token
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            statusElem.innerHTML = `<div class="success-message">${data.message}</div>`;
            document.getElementById('auth-token').value = '';
        } else {
            statusElem.innerHTML = `<div class="error-message">${data.error || '认证失败'}</div>`;
        }
    })
    .catch(error => {
        statusElem.innerHTML = `<div class="error-message">请求失败: ${error.message}</div>`;
    });
}

/**
 * 获取远程仓库列表
 */
function listRemoteRepositories() {
    const platform = document.getElementById('platform-select').value;
    const username = document.getElementById('username-input').value;
    
    const container = document.getElementById('remote-repos-container');
    container.innerHTML = '<div class="loading">正在获取仓库列表...</div>';
    
    fetch('/api/repository/list', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            platform: platform,
            username: username || null
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            renderRemoteRepositories(data.repositories, platform);
        } else {
            container.innerHTML = `<div class="error-message">${data.error || '获取仓库列表失败'}</div>`;
        }
    })
    .catch(error => {
        container.innerHTML = `<div class="error-message">请求失败: ${error.message}</div>`;
    });
}

/**
 * 渲染远程仓库列表
 */
function renderRemoteRepositories(repositories, platform) {
    const container = document.getElementById('remote-repos-container');
    
    if (!repositories || repositories.length === 0) {
        container.innerHTML = '<div class="info-message">未找到仓库</div>';
        return;
    }
    
    let html = '<div class="remote-repos-grid">';
    repositories.forEach(repo => {
        html += `
            <div class="remote-repo-item">
                <div class="remote-repo-header">
                    <h4 class="remote-repo-name">${repo.name}</h4>
                    <span class="remote-repo-visibility">${repo.private ? '私有' : '公开'}</span>
                </div>
                <div class="remote-repo-info">
                    <p class="remote-repo-full-name">${repo.full_name}</p>
                    <p class="remote-repo-description">${repo.description || '无描述'}</p>
                    <div class="remote-repo-stats">
                        <span class="remote-repo-language">${repo.language || '未知语言'}</span>
                        <span class="remote-repo-stars">⭐ ${repo.stars}</span>
                        <span class="remote-repo-forks">🍴 ${repo.forks}</span>
                    </div>
                </div>
                <div class="remote-repo-actions">
                    <button class="btn btn-clone" data-platform="${platform}" data-repo-name="${repo.full_name}">克隆仓库</button>
                    <a href="${repo.url}" target="_blank" class="btn btn-view">查看仓库</a>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
    
    // 绑定克隆按钮事件
    document.querySelectorAll('.btn-clone').forEach(btn => {
        btn.addEventListener('click', function() {
            const platform = this.getAttribute('data-platform');
            const repoName = this.getAttribute('data-repo-name');
            showCloneDialog(platform, repoName);
        });
    });
}

/**
 * 拉取仓库更新
 */
function pullRepository(repoPath) {
    fetch('/api/repository/pull', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            repo_path: repoPath
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            // 刷新本地仓库列表
            loadLocalRepositories();
        } else if (data.need_confirmation) {
            // 需要确认权限
            showConfirmDialog(data.message, function() {
                confirmOperation(data.operation, function() {
                    pullRepository(repoPath);
                });
            });
        } else {
            showMessage(data.error || '拉取更新失败', 'error');
        }
    })
    .catch(error => {
        showMessage('请求失败: ' + error.message, 'error');
    });
}

/**
 * 显示推送对话框
 */
function showPushDialog(repoPath) {
    document.getElementById('push-dialog').setAttribute('data-repo-path', repoPath);
    document.getElementById('commit-message').value = '';
    document.getElementById('push-branch').value = '';
    document.getElementById('push-dialog').classList.add('show');
}

/**
 * 隐藏推送对话框
 */
function hidePushDialog() {
    document.getElementById('push-dialog').classList.remove('show');
}

/**
 * 确认推送
 */
function confirmPush() {
    const repoPath = document.getElementById('push-dialog').getAttribute('data-repo-path');
    const message = document.getElementById('commit-message').value;
    const branch = document.getElementById('push-branch').value;
    
    if (!message) {
        showMessage('请输入提交信息', 'error');
        return;
    }
    
    hidePushDialog();
    
    fetch('/api/repository/push', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            repo_path: repoPath,
            message: message,
            branch: branch || null
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            // 刷新本地仓库列表
            loadLocalRepositories();
        } else if (data.need_confirmation) {
            // 需要确认权限
            showConfirmDialog(data.message, function() {
                confirmOperation(data.operation, function() {
                    // 重新显示推送对话框
                    showPushDialog(repoPath);
                });
            });
        } else {
            showMessage(data.error || '推送更改失败', 'error');
        }
    })
    .catch(error => {
        showMessage('请求失败: ' + error.message, 'error');
    });
}

/**
 * 删除仓库
 */
function deleteRepository(repoPath) {
    fetch('/api/repository/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            repo_path: repoPath
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            // 刷新本地仓库列表
            loadLocalRepositories();
        } else if (data.need_confirmation) {
            // 需要确认权限
            showConfirmDialog(data.message, function() {
                confirmOperation(data.operation, function() {
                    deleteRepository(repoPath);
                });
            });
        } else {
            showMessage(data.error || '删除仓库失败', 'error');
        }
    })
    .catch(error => {
        showMessage('请求失败: ' + error.message, 'error');
    });
}

/**
 * 显示克隆对话框
 */
function showCloneDialog(platform, repoName) {
    document.getElementById('clone-dialog').setAttribute('data-platform', platform);
    document.getElementById('clone-dialog').setAttribute('data-repo-name', repoName);
    document.getElementById('clone-repo-name').value = repoName;
    document.getElementById('clone-branch').value = '';
    document.getElementById('clone-dialog').classList.add('show');
}

/**
 * 隐藏克隆对话框
 */
function hideCloneDialog() {
    document.getElementById('clone-dialog').classList.remove('show');
}

/**
 * 确认克隆
 */
function confirmClone() {
    const platform = document.getElementById('clone-dialog').getAttribute('data-platform');
    const repoName = document.getElementById('clone-dialog').getAttribute('data-repo-name');
    const branch = document.getElementById('clone-branch').value;
    
    hideCloneDialog();
    
    fetch('/api/repository/clone', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            platform: platform,
            repo_name: repoName,
            branch: branch || null
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            // 切换到本地仓库标签页
            document.querySelector('[data-tab="local-repos"]').click();
            // 刷新本地仓库列表
            loadLocalRepositories();
        } else if (data.need_confirmation) {
            // 需要确认权限
            showConfirmDialog(data.message, function() {
                confirmOperation(data.operation, function() {
                    // 重新显示克隆对话框
                    showCloneDialog(platform, repoName);
                });
            });
        } else {
            showMessage(data.error || '克隆仓库失败', 'error');
        }
    })
    .catch(error => {
        showMessage('请求失败: ' + error.message, 'error');
    });
}

/**
 * 显示确认对话框
 */
function showConfirmDialog(message, callback) {
    document.getElementById('confirm-message').textContent = message;
    document.getElementById('confirm-dialog').setAttribute('data-callback', callback.toString());
    document.getElementById('confirm-dialog').classList.add('show');
    
    // 获取权限状态
    fetch('/api/auth/status')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.trust_status) {
                const trustStatus = data.trust_status;
                if (data.mode === 'trust' && !trustStatus.trusted) {
                    document.getElementById('trust-progress').textContent = 
                        `信任进度: ${trustStatus.confirm_count}/${trustStatus.required_count}`;
                    document.getElementById('trust-progress').style.display = 'block';
                } else {
                    document.getElementById('trust-progress').style.display = 'none';
                }
            }
        });
}

/**
 * 隐藏确认对话框
 */
function hideConfirmDialog() {
    document.getElementById('confirm-dialog').classList.remove('show');
}

/**
 * 确认对话框确认按钮
 */
function confirmDialogYes() {
    const callbackStr = document.getElementById('confirm-dialog').getAttribute('data-callback');
    hideConfirmDialog();
    
    // 执行回调
    if (callbackStr) {
        const callback = new Function('return ' + callbackStr)();
        callback();
    }
}

/**
 * 确认操作
 */
function confirmOperation(operation, callback) {
    fetch('/api/auth/confirm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            operation: operation
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新权限状态
            if (data.trust_status) {
                updateAuthStatus(data.trust_status.mode, data.trust_status);
            }
            
            // 执行回调
            if (callback) {
                callback();
            }
        } else {
            showMessage(data.error || '确认操作失败', 'error');
        }
    })
    .catch(error => {
        showMessage('请求失败: ' + error.message, 'error');
    });
}

/**
 * 显示消息提示
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
 * 初始化仓库权限管理标签页
 */
function initPermissionsTabs() {
    const tabButtons = document.querySelectorAll('.permission-tab-btn');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有活动标签
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // 隐藏所有内容
            document.querySelectorAll('.permission-tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // 激活当前选中的标签和内容
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // 绑定仓库权限管理按钮
    const loadPermissionsBtn = document.getElementById('load-permissions-btn');
    if (loadPermissionsBtn) {
        loadPermissionsBtn.addEventListener('click', loadRepoPermissions);
    }
    
    const assignRoleBtn = document.getElementById('assign-role-btn');
    if (assignRoleBtn) {
        assignRoleBtn.addEventListener('click', assignUserRole);
    }
    
    const updateProtectionBtn = document.getElementById('update-protection-btn');
    if (updateProtectionBtn) {
        updateProtectionBtn.addEventListener('click', updateProtectionRules);
    }
    
    const refreshAuditBtn = document.getElementById('refresh-audit-btn');
    if (refreshAuditBtn) {
        refreshAuditBtn.addEventListener('click', loadAuditLogs);
    }
}

/**
 * 加载仓库权限设置
 */
function loadRepoPermissions() {
    const repoPath = document.getElementById('permission-repo-select').value;
    
    if (!repoPath) {
        showMessage('请选择仓库', 'error');
        return;
    }
    
    // 加载权限设置
    fetch(`/api/repository/permissions?repo_path=${encodeURIComponent(repoPath)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 更新角色分配列表
                renderRoleAssignments(data.permissions.role_assignments);
                
                // 更新保护规则
                updateProtectionRulesForm(data.permissions.protection_rules);
                
                // 加载审计日志
                loadAuditLogs();
            } else {
                showMessage(data.error || '加载仓库权限设置失败', 'error');
            }
        })
        .catch(error => {
            showMessage('请求失败: ' + error.message, 'error');
        });
}

/**
 * 渲染角色分配列表
 */
function renderRoleAssignments(roleAssignments) {
    const container = document.getElementById('role-assignments-list');
    
    if (!roleAssignments || Object.keys(roleAssignments).length === 0) {
        container.innerHTML = '<p class="info-message">暂无角色分配</p>';
        return;
    }
    
    let html = '<table class="role-assignments-table"><thead><tr><th>用户ID</th><th>角色</th><th>操作</th></tr></thead><tbody>';
    
    for (const userId in roleAssignments) {
        const role = roleAssignments[userId];
        html += `
            <tr>
                <td>${userId}</td>
                <td>${getRoleName(role)}</td>
                <td>
                    <button class="btn btn-small btn-edit-role" data-user-id="${userId}" data-role="${role}">编辑</button>
                </td>
            </tr>
        `;
    }
    
    html += '</tbody></table>';
    container.innerHTML = html;
    
    // 绑定编辑按钮事件
    document.querySelectorAll('.btn-edit-role').forEach(btn => {
        btn.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id');
            const role = this.getAttribute('data-role');
            
            // 填充表单
            document.getElementById('user-id-input').value = userId;
            document.getElementById('role-select').value = role;
        });
    });
}

/**
 * 获取角色名称
 */
function getRoleName(role) {
    switch (role) {
        case 'admin':
            return '管理员';
        case 'developer':
            return '开发者';
        case 'reader':
            return '只读用户';
        default:
            return role;
    }
}

/**
 * 更新保护规则表单
 */
function updateProtectionRulesForm(rules) {
    // 设置要求代码审查复选框
    const requireReviewCheckbox = document.getElementById('require-review-checkbox');
    requireReviewCheckbox.checked = rules.require_review === true;
    
    // 设置禁止强制推送复选框
    const blockForcePushCheckbox = document.getElementById('block-force-push-checkbox');
    blockForcePushCheckbox.checked = rules.block_force_push === true;
    
    // 设置受保护分支
    const protectedBranchesInput = document.getElementById('protected-branches-input');
    if (Array.isArray(rules.protected_branches)) {
        protectedBranchesInput.value = rules.protected_branches.join('\n');
    } else {
        protectedBranchesInput.value = '';
    }
}

/**
 * 分配用户角色
 */
function assignUserRole() {
    const repoPath = document.getElementById('permission-repo-select').value;
    const userId = document.getElementById('user-id-input').value;
    const role = document.getElementById('role-select').value;
    
    if (!repoPath) {
        showMessage('请选择仓库', 'error');
        return;
    }
    
    if (!userId) {
        showMessage('请输入用户ID', 'error');
        return;
    }
    
    fetch('/api/repository/role', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            repo_path: repoPath,
            user_id: userId,
            role: role
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
            // 重新加载权限设置
            loadRepoPermissions();
        } else {
            showMessage(data.error || '分配用户角色失败', 'error');
        }
    })
    .catch(error => {
        showMessage('请求失败: ' + error.message, 'error');
    });
}

/**
 * 更新保护规则
 */
function updateProtectionRules() {
    const repoPath = document.getElementById('permission-repo-select').value;
    
    if (!repoPath) {
        showMessage('请选择仓库', 'error');
        return;
    }
    
    // 获取表单数据
    const requireReview = document.getElementById('require-review-checkbox').checked;
    const blockForcePush = document.getElementById('block-force-push-checkbox').checked;
    const protectedBranchesText = document.getElementById('protected-branches-input').value;
    
    // 解析受保护分支
    const protectedBranches = protectedBranchesText
        .split('\n')
        .map(branch => branch.trim())
        .filter(branch => branch !== '');
    
    fetch('/api/repository/protection', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            repo_path: repoPath,
            rules: {
                require_review: requireReview,
                block_force_push: blockForcePush,
                protected_branches: protectedBranches
            }
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(data.message, 'success');
        } else {
            showMessage(data.error || '更新保护规则失败', 'error');
        }
    })
    .catch(error => {
        showMessage('请求失败: ' + error.message, 'error');
    });
}

/**
 * 加载审计日志
 */
function loadAuditLogs() {
    const repoPath = document.getElementById('permission-repo-select').value;
    const limit = document.getElementById('audit-limit-input').value;
    
    if (!repoPath) {
        showMessage('请选择仓库', 'error');
        return;
    }
    
    fetch(`/api/repository/audit?repo_path=${encodeURIComponent(repoPath)}&limit=${limit}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderAuditLogs(data.logs);
            } else {
                showMessage(data.error || '加载审计日志失败', 'error');
            }
        })
        .catch(error => {
            showMessage('请求失败: ' + error.message, 'error');
        });
}

/**
 * 渲染审计日志
 */
function renderAuditLogs(logs) {
    const tbody = document.getElementById('audit-log-body');
    
    if (!logs || logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="info-message">暂无审计日志</td></tr>';
        return;
    }
    
    let html = '';
    logs.forEach(log => {
        const date = new Date(log.timestamp * 1000).toLocaleString();
        
        html += `
            <tr>
                <td>${date}</td>
                <td>${log.user_id.substring(0, 8)}</td>
                <td>${log.operation_name || log.operation}</td>
                <td>
                    ${log.details && log.details.repo_path ? `仓库路径: ${log.details.repo_path}` : ''}
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
} 