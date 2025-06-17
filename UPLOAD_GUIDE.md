# 代码上传指南

本指南将帮助您将代码上传到远程仓库。

## 准备工作

1. 确保您已经有一个远程仓库（如GitHub、GitLab或Gitee）
2. 确保您已经安装了Git并配置了SSH密钥或用户名密码

## 上传步骤

### 1. 添加远程仓库

```bash
# 替换 <remote-url> 为您的远程仓库URL
git remote add origin <remote-url>
```

例如：
```bash
git remote add origin https://github.com/yourusername/AIgo.git
```

或者使用SSH：
```bash
git remote add origin git@github.com:yourusername/AIgo.git
```

### 2. 推送代码到远程仓库

```bash
# 推送主分支
git push -u origin main
```

如果您使用的是默认的master分支：
```bash
git push -u origin master
```

### 3. 验证上传

访问您的远程仓库网站，确认代码已经成功上传。

## 常见问题

### 认证失败

如果遇到认证失败的问题：

1. 检查您的用户名和密码是否正确
2. 确认您的SSH密钥是否已添加到远程仓库
3. 尝试使用凭证管理器存储您的凭证

### 冲突解决

如果远程仓库已经有内容，可能会发生冲突：

```bash
# 先拉取远程仓库的内容
git pull origin main --rebase

# 解决冲突后继续
git push -u origin main
```

## 后续步骤

成功上传代码后，您可以：

1. 创建README.md文件，说明项目的用途和使用方法
2. 添加LICENSE文件，明确项目的许可证
3. 设置项目的贡献指南
4. 邀请其他人参与项目 