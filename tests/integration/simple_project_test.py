#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_project_management():
    print("开始测试项目管理API...")

    # 注册用户
    print("1. 注册测试用户...")
    user_data = {
        "username": "projecttest",
        "email": "projecttest@example.com",
        "password": "test123456"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 201:
            print("[OK] 用户创建成功")
        else:
            print(f"[ERROR] 用户创建失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 登录
    print("2. 用户登录...")
    login_data = {
        "username": "projecttest",
        "password": "test123456"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("[OK] 登录成功")
        else:
            print(f"[ERROR] 登录失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 创建项目
    print("3. 创建项目...")
    project_data = {
        "name": "测试项目1",
        "color": "#1890ff",
        "description": "这是一个测试项目"
    }

    try:
        response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=headers)
        if response.status_code == 201:
            project = response.json().get('project')
            print(f"[OK] 项目创建成功: {project['name']}")
            project_id = project['id']
        else:
            print(f"[ERROR] 项目创建失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 获取项目列表
    print("4. 获取项目列表...")
    try:
        response = requests.get(f"{BASE_URL}/projects", headers=headers)
        if response.status_code == 200:
            projects = response.json()
            print(f"[OK] 获取项目列表成功，共 {len(projects)} 个项目")
        else:
            print(f"[ERROR] 获取项目列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 获取单个项目
    print("5. 获取单个项目...")
    try:
        response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=headers)
        if response.status_code == 200:
            project_detail = response.json()
            print(f"[OK] 获取项目详情成功: {project_detail['name']}")
        else:
            print(f"[ERROR] 获取项目详情失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 更新项目
    print("6. 更新项目...")
    update_data = {
        "name": "更新后的测试项目",
        "color": "#52c41a",
        "description": "更新后的描述"
    }

    try:
        response = requests.put(f"{BASE_URL}/projects/{project_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            print("[OK] 项目更新成功")
        else:
            print(f"[ERROR] 项目更新失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 删除项目
    print("7. 删除项目...")
    try:
        response = requests.delete(f"{BASE_URL}/projects/{project_id}", headers=headers)
        if response.status_code == 200:
            print("[OK] 项目删除成功")
        else:
            print(f"[ERROR] 项目删除失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    print("所有测试通过!")
    return True

if __name__ == "__main__":
    try:
        if test_project_management():
            print("项目管理API功能正常")
            sys.exit(0)
        else:
            print("项目管理API测试失败")
            sys.exit(1)
    except Exception as e:
        print(f"测试异常: {e}")
        sys.exit(1)