#!/usr/bin/env python3
"""
项目骨架简单验证脚本
"""

import os
import sys

def check_project():
    """检查项目骨架"""
    print("Project Structure Check")
    print("=" * 50)

    # 检查关键文件
    critical_files = [
        "backend/pyproject.toml",
        "backend/app.py",
        "frontend/package.json",
        "frontend/src/main.jsx",
        "README.md",
        "product_requirements.md",
        "model.md",
        "relations.md",
        "Rule.md"
    ]

    all_good = True

    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"OK: {file_path}")
        else:
            print(f"MISSING: {file_path}")
            all_good = False

    print("=" * 50)

    if all_good:
        print("SUCCESS: All files present!")
        print("\nNext steps:")
        print("1. Backend: cd backend && uv run python app.py")
        print("2. Frontend: cd frontend && pnpm dev")
        print("3. Access: http://localhost:5173")
        return 0
    else:
        print("FAILED: Some files are missing.")
        return 1

if __name__ == "__main__":
    sys.exit(check_project())