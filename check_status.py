#!/usr/bin/env python3
"""
项目状态检查脚本
检查前后端项目骨架的完整性
"""

import os
import sys
from pathlib import Path

def check_backend_structure():
    """检查后端项目结构"""
    print("\n检查后端项目结构...")

    backend_files = [
        "backend/pyproject.toml",
        "backend/.env.example",
        "backend/app.py",
        "backend/config/__init__.py",
        "backend/app/__init__.py",
        "backend/models/__init__.py",
        "backend/models/user.py",
        "backend/models/task.py",
        "backend/models/task_category.py",
        "backend/models/time_block.py",
        "backend/models/project.py",
        "backend/models/tag.py",
        "backend/models/task_tags.py",
        "backend/routes/__init__.py",
        "backend/routes/auth_routes.py",
        "backend/routes/user_routes.py",
        "backend/routes/task_routes.py",
        "backend/utils/__init__.py",
        "backend/utils/response_utils.py"
    ]

    missing_files = []
    for file_path in backend_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print("后端文件缺失:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("后端项目结构完整")
        return True

def check_frontend_structure():
    """检查前端项目结构"""
    print("\n检查前端项目结构...")

    frontend_files = [
        "frontend/package.json",
        "frontend/vite.config.js",
        "frontend/index.html",
        "frontend/src/main.jsx",
        "frontend/src/index.css",
        "frontend/src/App.jsx",
        "frontend/src/App.css",
        "frontend/src/components/Header.jsx",
        "frontend/src/stores/authStore.js",
        "frontend/src/services/api.js",
        "frontend/src/pages/Home.jsx",
        "frontend/src/pages/Login.jsx",
        "frontend/src/pages/Tasks.jsx"
    ]

    missing_files = []
    for file_path in frontend_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print("前端文件缺失:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("前端项目结构完整")
        return True

def check_documentation():
    """检查文档完整性"""
    print("\n检查项目文档...")

    docs = [
        "README.md",
        "product_requirements.md",
        "model.md",
        "relations.md",
        "Rule.md"
    ]

    missing_docs = []
    for doc in docs:
        if not os.path.exists(doc):
            missing_docs.append(doc)

    if missing_docs:
        print("文档缺失:")
        for doc in missing_docs:
            print(f"   - {doc}")
        return False
    else:
        print("项目文档完整")
        return True

def check_directory_structure():
    """检查目录结构"""
    print("\n检查目录结构...")

    directories = [
        "backend",
        "backend/app",
        "backend/models",
        "backend/routes",
        "backend/services",
        "backend/utils",
        "backend/config",
        "frontend",
        "frontend/src",
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/services",
        "frontend/src/hooks",
        "frontend/src/utils",
        "frontend/public"
    ]

    missing_dirs = []
    for dir_path in directories:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)

    if missing_dirs:
        print("目录缺失:")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        return False
    else:
        print("目录结构完整")
        return True

def main():
    """主检查函数"""
    print("时间管理系统 - 项目骨架状态检查")
    print("=" * 50)

    checks = [
        check_directory_structure(),
        check_backend_structure(),
        check_frontend_structure(),
        check_documentation()
    ]

    print("\n" + "=" * 50)

    if all(checks):
        print("所有检查通过！项目骨架搭建完成。")
        print("\n下一步操作:")
        print("1. 后端: cd backend && uv run python app.py")
        print("2. 前端: cd frontend && pnpm dev")
        print("3. 访问: http://localhost:5173")
        return 0
    else:
        print("检查未通过，请修复上述问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())