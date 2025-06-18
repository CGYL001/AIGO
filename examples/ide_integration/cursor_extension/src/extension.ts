import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { AIgoApiService } from './api-service';

/**
 * AIgo Cursor扩展
 * 将AIgo智能代码助手集成到Cursor IDE中
 */

// 服务连接状态
let isConnected = false;
let apiService: AIgoApiService;

// 激活扩展
export function activate(context: vscode.ExtensionContext) {
    console.log('AIgo扩展已激活');

    // 加载配置并初始化API服务
    const config = vscode.workspace.getConfiguration('aigo');
    const serverUrl = config.get<string>('server.url') || 'http://localhost:8080/api';
    const authToken = config.get<string>('server.authToken') || '';
    
    apiService = new AIgoApiService(serverUrl, authToken);

    // 注册命令
    context.subscriptions.push(
        vscode.commands.registerCommand('aigo.connect', connectToServer),
        vscode.commands.registerCommand('aigo.scanProject', scanProject),
        vscode.commands.registerCommand('aigo.createContext', createContext),
        vscode.commands.registerCommand('aigo.useLocalModel', toggleLocalModel),
        vscode.commands.registerCommand('aigo.viewMemory', viewMemory)
    );

    // 监听配置变更
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('aigo')) {
                const config = vscode.workspace.getConfiguration('aigo');
                const serverUrl = config.get<string>('server.url') || 'http://localhost:8080/api';
                const authToken = config.get<string>('server.authToken') || '';
                
                apiService.updateConfig(serverUrl, authToken);
            }
        })
    );

    // 自动连接服务器
    connectToServer();
}

// 连接到服务器
async function connectToServer() {
    try {
        const isAvailable = await apiService.checkStatus();

        if (isAvailable) {
            isConnected = true;
            const config = vscode.workspace.getConfiguration('aigo');
            const serverUrl = config.get<string>('server.url') || 'http://localhost:8080/api';
            vscode.window.showInformationMessage(`已连接到AIgo服务器: ${serverUrl}`);
        } else {
            isConnected = false;
            vscode.window.showErrorMessage('无法连接到AIgo服务器');
        }
    } catch (error) {
        isConnected = false;
        vscode.window.showErrorMessage(`连接AIgo服务器失败: ${error instanceof Error ? error.message : String(error)}`);
    }
}

// 扫描项目
async function scanProject() {
    if (!checkConnection()) return;

    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showWarningMessage('没有打开的工作区');
            return;
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: '正在扫描项目...',
            cancellable: true
        }, async (progress, token) => {
            progress.report({ increment: 0 });

            try {
                await apiService.scanFileSystem(rootPath);
                vscode.window.showInformationMessage('项目扫描完成');
                progress.report({ increment: 100 });
            } catch (error) {
                vscode.window.showErrorMessage(`项目扫描异常: ${error instanceof Error ? error.message : String(error)}`);
            }
        });
    } catch (error) {
        vscode.window.showErrorMessage(`扫描项目失败: ${error instanceof Error ? error.message : String(error)}`);
    }
}

// 创建上下文
async function createContext() {
    if (!checkConnection()) return;

    try {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('没有打开的文件');
            return;
        }

        const document = editor.document;
        const fileName = path.basename(document.fileName);
        const content = document.getText();

        await apiService.createContext(fileName, content, 'file');
        vscode.window.showInformationMessage(`已将 ${fileName} 添加到上下文`);
    } catch (error) {
        vscode.window.showErrorMessage(`创建上下文异常: ${error instanceof Error ? error.message : String(error)}`);
    }
}

// 切换本地模型
async function toggleLocalModel() {
    if (!checkConnection()) return;

    try {
        const config = vscode.workspace.getConfiguration('aigo');
        const useLocalModel = config.get<boolean>('aiAssistant.localModels');
        
        await config.update('aiAssistant.localModels', !useLocalModel, vscode.ConfigurationTarget.Global);
        
        await apiService.switchModel(!useLocalModel);
        vscode.window.showInformationMessage(`已${!useLocalModel ? '启用' : '禁用'}本地模型`);
    } catch (error) {
        vscode.window.showErrorMessage(`切换模型异常: ${error instanceof Error ? error.message : String(error)}`);
    }
}

// 查看记忆
async function viewMemory() {
    if (!checkConnection()) return;

    try {
        const memoryData = await apiService.getContextList();

        if (memoryData) {
            const panel = vscode.window.createWebviewPanel(
                'aigoMemory',
                'AIgo记忆',
                vscode.ViewColumn.One,
                { enableScripts: true }
            );

            panel.webview.html = getMemoryWebviewContent(memoryData);
        } else {
            vscode.window.showErrorMessage('获取记忆失败');
        }
    } catch (error) {
        vscode.window.showErrorMessage(`查看记忆异常: ${error instanceof Error ? error.message : String(error)}`);
    }
}

// 生成记忆查看页面
function getMemoryWebviewContent(memoryData: any): string {
    return `<!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AIgo记忆</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                color: var(--vscode-foreground);
                background-color: var(--vscode-editor-background);
            }
            .memory-item {
                margin-bottom: 20px;
                padding: 10px;
                border: 1px solid var(--vscode-panel-border);
                border-radius: 5px;
            }
            .memory-name {
                font-weight: bold;
                margin-bottom: 5px;
            }
            .memory-type {
                font-style: italic;
                margin-bottom: 10px;
                color: var(--vscode-descriptionForeground);
            }
            .memory-content {
                white-space: pre-wrap;
                background-color: var(--vscode-editor-inactiveSelectionBackground);
                padding: 10px;
                border-radius: 3px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <h1>AIgo记忆</h1>
        <div id="memory-container">
            ${renderMemoryItems(memoryData)}
        </div>
    </body>
    </html>`;
}

// 渲染记忆项目
function renderMemoryItems(memoryData: any): string {
    if (!Array.isArray(memoryData)) {
        return '<p>没有可用的记忆</p>';
    }

    return memoryData.map((item: any) => `
        <div class="memory-item">
            <div class="memory-name">${item.name || '未命名'}</div>
            <div class="memory-type">类型: ${item.type || '未知'}</div>
            <pre class="memory-content">${escapeHtml(item.content || '')}</pre>
        </div>
    `).join('');
}

// HTML转义
function escapeHtml(unsafe: string): string {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 检查连接状态
function checkConnection(): boolean {
    if (!isConnected) {
        vscode.window.showWarningMessage('未连接到AIgo服务器，请先连接服务器');
        return false;
    }
    return true;
}

// 扩展停用时调用
export function deactivate() {
    console.log('AIgo扩展已停用');
} 