#!/usr/bin/env python3
"""
项目骨架验证脚本
"""

import os
import sys

def verify_project():
    """验证项目骨架"""
    print("Project Structure Verification")
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
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_good = False

    print("\n" + "=" * 50)

    if all_good:
        print("SUCCESS: Project skeleton is complete!")
        print("\nNext steps:")
        print("1. Backend: cd backend && uv run python app.py")
        print("2. Frontend: cd frontend && pnpm dev")
        print("3. Access: http://localhost:5173")
        return 0
    else:
        print("FAILED: Some files are missing.")
        return 1

if __name__ == "__main__":
    sys.exit(verify_project())