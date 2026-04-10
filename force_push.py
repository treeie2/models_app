#!/usr/bin/env python3
"""
强制推送当前代码到 GitHub
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd, description):
    """运行命令"""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ❌ {description} 失败: {result.stderr}")
        return False
    print(f"   ✅ {description} 完成")
    return True


def main():
    """主函数"""
    print("🚀 强制推送代码到 GitHub...\n")
    
    # 配置
    github_token = "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"
    github_repo = "treeie2/models_app"
    
    # 使用 git 命令推送
    source_dir = Path("e:/github/stock-research-backup")
    
    # 初始化 git（如果没有）
    if not (source_dir / ".git").exists():
        print("📂 初始化 Git 仓库...")
        if not run_command(["git", "init"], source_dir, "Git init"):
            return False
    
    # 添加远程仓库
    remote_url = f"https://{github_token}@github.com/{github_repo}.git"
    
    # 检查 remote 是否存在
    result = subprocess.run(["git", "remote", "get-url", "origin"], 
                          cwd=source_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print("📂 添加远程仓库...")
        if not run_command(["git", "remote", "add", "origin", remote_url], source_dir, "添加 remote"):
            return False
    else:
        # 更新 remote URL
        if not run_command(["git", "remote", "set-url", "origin", remote_url], source_dir, "更新 remote URL"):
            return False
    
    # 添加所有文件
    print("\n🔄 添加文件...")
    if not run_command(["git", "add", "-A"], source_dir, "Git add"):
        return False
    
    # 提交
    print("\n🔄 提交更改...")
    result = subprocess.run(["git", "commit", "-m", "添加全文搜索功能并清理项目"], 
                          cwd=source_dir, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Git commit 完成")
    else:
        print(f"   ⚠️ Commit: {result.stderr}")
    
    # 强制推送到 main 分支
    print("\n🔄 推送到 GitHub...")
    result = subprocess.run(["git", "push", "-f", "origin", "HEAD:main"], 
                          cwd=source_dir, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Git push 完成")
        print("\n✅ 全部完成!")
        print("   代码已推送到 GitHub")
        print("   Vercel 会自动重新部署")
        return True
    else:
        print(f"   ❌ Git push 失败: {result.stderr}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
