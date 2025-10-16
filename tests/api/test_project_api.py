#!/usr/bin/env python3
"""
项目管理API测试脚本
"""

import requests
import json
import sys

# API基础URL
BASE_URL = "http://localhost:5000/api"

def test_project_api():
    """测试项目管理API"""
    print("开始测试项目管理API...")

    # 1. 创建测试用户
    print("\n1. 创建测试用户...")
    register_data = {
        "username": "project_test_user",
        "email": "projecttest@example.com",
        "password": "test123456"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 201:
            print("[OK] 用户创建成功")
        else:
            print(f"[ERROR] 用户创建失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"[ERROR] 用户创建异常: {e}")
        return False

    # 2. 用户登录获取token
    print("\n2. 用户登录...")
    login_data = {
        "username": "project_test_user",
        "password": "test123456"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False

    # 设置认证头
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 3. 测试创建项目
    print("\n3. 测试创建项目...")
    project_data = {
        "name": "测试项目1",
        "color": "#1890ff",
        "description": "这是一个测试项目"
    }

    try:
        response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers)
        if response.status_code == 201:
            project1 = response.json().get('project')
            print(f"✅ 项目1创建成功: {project1['name']}")
        else:
            print(f"❌ 项目1创建失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 项目1创建异常: {e}")
        return False

    # 创建第二个项目
    project_data2 = {
        "name": "测试项目2",
        "color": "#52c41a",
        "description": "这是另一个测试项目"
    }

    try:
        response = requests.post(f"{BASE_URL}/projects", json=project_data2, headers=headers)
        if response.status_code == 201:
            project2 = response.json().get('project')
            print(f"✅ 项目2创建成功: {project2['name']}")
        else:
            print(f"❌ 项目2创建失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 项目2创建异常: {e}")
        return False

    # 4. 测试获取项目列表
    print("\n4. 测试获取项目列表...")
    try:
        response = requests.get(f"{BASE_URL}/projects", headers=headers)
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ 获取项目列表成功，共 {len(projects)} 个项目")
            for project in projects:
                print(f"  - {project['name']} ({project['color']}) - {project.get('task_count', 0)} 个任务")
        else:
            print(f"❌ 获取项目列表失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 获取项目列表异常: {e}")
        return False

    # 5. 测试获取单个项目
    print("\n5. 测试获取单个项目...")
    try:
        response = requests.get(f"{BASE_URL}/projects/{project1['id']}", headers=headers)
        if response.status_code == 200:
            project_detail = response.json()
            print(f"✅ 获取项目详情成功: {project_detail['name']}")
            print(f"  描述: {project_detail.get('description', '无')}")
            print(f"  任务数量: {project_detail.get('task_count', 0)}")
            print(f"  完成进度: {project_detail.get('completion_progress', 0)*100:.1f}%")
        else:
            print(f"❌ 获取项目详情失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 获取项目详情异常: {e}")
        return False

    # 6. 测试更新项目
    print("\n6. 测试更新项目...")
    update_data = {
        "name": "更新后的测试项目1",
        "color": "#f5222d",
        "description": "这是更新后的项目描述"
    }

    try:
        response = requests.put(f"{BASE_URL}/projects/{project1['id']}", json=update_data, headers=headers)
        if response.status_code == 200:
            updated_project = response.json().get('project')
            print(f"✅ 项目更新成功: {updated_project['name']}")
        else:
            print(f"❌ 项目更新失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 项目更新异常: {e}")
        return False

    # 7. 测试删除项目
    print("\n7. 测试删除项目...")
    try:
        response = requests.delete(f"{BASE_URL}/projects/{project2['id']}", headers=headers)
        if response.status_code == 200:
            print(f"✅ 项目删除成功: {project2['name']}")
        else:
            print(f"❌ 项目删除失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 项目删除异常: {e}")
        return False

    # 8. 再次获取项目列表验证删除
    print("\n8. 验证删除结果...")
    try:
        response = requests.get(f"{BASE_URL}/projects", headers=headers)
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ 删除后项目列表，共 {len(projects)} 个项目")
            if len(projects) == 1:
                print("✅ 删除验证成功")
            else:
                print("❌ 删除验证失败，项目数量不正确")
                return False
        else:
            print(f"❌ 获取删除后项目列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 验证删除异常: {e}")
        return False

    print("\n🎉 所有项目管理API测试通过！")
    return True

if __name__ == "__main__":
    try:
        success = test_project_api()
        if success:
            print("\n✅ 项目管理页面API功能正常，前端页面可以使用！")
            sys.exit(0)
        else:
            print("\n❌ API测试失败，需要修复后端问题")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生未预期的错误: {e}")
        sys.exit(1)