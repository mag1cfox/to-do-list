#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

def test_timeblock_template_api():
    print("开始测试时间块模板API...")

    # 1. 用户登录获取token
    print("1. 用户登录...")
    login_data = {
        "username": "demo_user",
        "password": "demo123456"
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

    # 2. 创建时间块模板
    print("2. 创建时间块模板...")
    sample_templates = [
        {
            "name": "标准工作日",
            "description": "标准的8小时工作日模板，包含上午和下午工作时间",
            "is_default": True
        },
        {
            "name": "深度工作模式",
            "description": "专注深度工作的时间安排，减少干扰"
        },
        {
            "name": "学习日模式",
            "description": "专门用于学习和技能提升的时间安排"
        }
    ]

    created_templates = []
    for template_data in sample_templates:
        try:
            response = requests.post(f"{BASE_URL}/time-block-templates", json=template_data, headers=headers)
            if response.status_code == 201:
                template = response.json().get('template')
                created_templates.append(template)
                print(f"[OK] 创建模板: {template['name']}")
            else:
                print(f"[ERROR] 模板创建失败: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    # 3. 获取模板列表
    print("3. 获取模板列表...")
    try:
        response = requests.get(f"{BASE_URL}/time-block-templates", headers=headers)
        if response.status_code == 200:
            templates = response.json()
            print(f"[OK] 获取到 {len(templates)} 个模板")
            for template in templates:
                default_mark = " (默认)" if template['is_default'] else ""
                print(f"   - {template['name']}{default_mark}")
        else:
            print(f"[ERROR] 获取模板列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 4. 获取单个模板
    print("4. 获取单个模板...")
    if created_templates:
        try:
            response = requests.get(f"{BASE_URL}/time-block-templates/{created_templates[0]['id']}", headers=headers)
            if response.status_code == 200:
                template_detail = response.json()
                print(f"[OK] 获取模板详情: {template_detail['name']}")
            else:
                print(f"[ERROR] 获取模板详情失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    # 5. 更新模板
    print("5. 更新模板...")
    if created_templates:
        update_data = {
            "description": "更新后的模板描述"
        }
        try:
            response = requests.put(f"{BASE_URL}/time-block-templates/{created_templates[0]['id']}", json=update_data, headers=headers)
            if response.status_code == 200:
                updated_template = response.json().get('template')
                print(f"[OK] 模板更新成功")
            else:
                print(f"[ERROR] 模板更新失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    # 6. 克隆模板
    print("6. 克隆模板...")
    if created_templates:
        try:
            response = requests.post(f"{BASE_URL}/time-block-templates/{created_templates[0]['id']}/clone", headers=headers)
            if response.status_code == 201:
                cloned_template = response.json().get('template')
                print(f"[OK] 模板克隆成功: {cloned_template['name']}")
            else:
                print(f"[ERROR] 模板克隆失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    # 7. 应用模板到日期
    print("7. 应用模板到日期...")
    if created_templates:
        target_date = (datetime.now() + timedelta(days=1)).date()
        apply_data = {
            "date": target_date.isoformat()
        }

        try:
            response = requests.post(f"{BASE_URL}/time-block-templates/{created_templates[0]['id']}/apply", json=apply_data, headers=headers)
            if response.status_code == 201:
                result = response.json()
                generated_blocks = result.get('generated_time_blocks', [])
                print(f"[OK] 模板应用成功，生成 {len(generated_blocks)} 个时间块")
                for block in generated_blocks:
                    print(f"   - {block['block_type']}: {block['start_time']} ~ {block['end_time']}")
            else:
                print(f"[ERROR] 模板应用失败: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    # 8. 测试删除非默认模板
    print("8. 删除非默认模板...")
    # 找到非默认模板进行删除
    non_default_template = None
    try:
        response = requests.get(f"{BASE_URL}/time-block-templates", headers=headers)
        if response.status_code == 200:
            templates = response.json()
            non_default_template = next((t for t in templates if not t['is_default']), None)
    except:
        pass

    if non_default_template:
        try:
            response = requests.delete(f"{BASE_URL}/time-block-templates/{non_default_template['id']}", headers=headers)
            if response.status_code == 200:
                print(f"[OK] 模板删除成功")
            else:
                print(f"[ERROR] 模板删除失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    else:
        print("[SKIP] 没有找到可删除的非默认模板")

    # 9. 测试删除默认模板（应该失败）
    print("9. 测试删除默认模板（应该失败）...")
    default_template = None
    try:
        response = requests.get(f"{BASE_URL}/time-block-templates", headers=headers)
        if response.status_code == 200:
            templates = response.json()
            default_template = next((t for t in templates if t['is_default']), None)
    except:
        pass

    if default_template:
        try:
            response = requests.delete(f"{BASE_URL}/time-block-templates/{default_template['id']}", headers=headers)
            if response.status_code == 400:
                print("[OK] 正确阻止了删除默认模板")
            else:
                print(f"[ERROR] 应该阻止删除默认模板，但状态码是: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    else:
        print("[SKIP] 没有找到默认模板")

    print("所有时间块模板API测试通过!")
    return True

if __name__ == "__main__":
    try:
        if test_timeblock_template_api():
            print("时间块模板API功能正常，时间块调度界面可以使用!")
            sys.exit(0)
        else:
            print("时间块模板API测试失败")
            sys.exit(1)
    except Exception as e:
        print(f"测试异常: {e}")
        sys.exit(1)