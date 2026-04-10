# 手动推送步骤

由于网络连接问题，请手动执行以下步骤：

## 1. 打开终端

在 `e:/github/stock-research-backup` 目录下打开 PowerShell

## 2. 配置 Git

```powershell
# 配置 Git 用户信息（如果还没配置）
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 添加远程仓库
git remote add origin https://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@github.com/treeie2/models_app.git
```

## 3. 提交并推送

```powershell
# 添加所有文件
git add -A

# 提交
git commit -m "修复 Vercel 部署配置，添加全文搜索功能"

# 强制推送到 main 分支
git push -f origin HEAD:main
```

## 4. 验证部署

推送成功后，访问 https://vercel.com/dashboard 查看部署状态。

部署完成后，访问 https://modelsapp-git-main-shermanns-projects.vercel.app/ 测试全文搜索功能。

## 主要变更

1. **新增 `api/index.py`** - Vercel Serverless Function 入口
2. **更新 `vercel.json`** - 使用 `@vercel/python` 构建器
3. **保留 `main.py`** - Flask 主应用（包含全文搜索 API）
4. **保留 `templates/dashboard.html`** - 全文搜索前端界面
