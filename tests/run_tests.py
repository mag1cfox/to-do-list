#!/usr/bin/env python3
"""
运行所有测试的脚本
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd, capture_output=True, text=True
    )
    return result.returncode == 0, result.stdout, result.stderr


def main():
    """主函数"""
    test_root = Path(__file__).parent

    print("🧪 开始运行TimeManager测试套件")
    print("=" * 50)

    # 测试目录列表
    test_dirs = [
        ("backend", "后端单元测试"),
        ("api", "API测试"),
        ("integration", "集成测试"),
    ]

    all_passed = True

    for test_dir, description in test_dirs:
        dir_path = test_root / test_dir
        if not dir_path.exists():
            print(f"⚠️  {description} 目录不存在: {dir_path}")
            continue

        print(f"\n📋 运行 {description}...")
        success, stdout, stderr = run_command(
            f"python -m pytest -v --tb=short", cwd=dir_path
        )

        if success:
            print(f"✅ {description} 通过")
        else:
            print(f"❌ {description} 失败")
            if stderr:
                print(f"错误信息:\n{stderr}")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("💥 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())