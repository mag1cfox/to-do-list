#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

def test_scheduler_functionality():
    print("开始测试时间块调度功能...")

    # 1. 用户登录
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

    # 2. 获取模板列表
    print("2. 获取模板列表...")
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

    # 3. 应用模板到日期
    print("3. 应用模板到日期...")
    if templates:
        # 选择第一个模板
        template = templates[0]
        target_date = (datetime.now() + timedelta(days=3)).date()
        apply_data = {
            "date": target_date.isoformat()
        }

        try:
            response = requests.post(f"{BASE_URL}/time-block-templates/{template['id']}/apply", json=apply_data, headers=headers)
            if response.status_code == 201:
                result = response.json()
                generated_blocks = result.get('generated_time_blocks', [])
                print(f"[OK] 模板应用成功，生成 {len(generated_blocks)} 个时间块")
                for block in generated_blocks:
                    start_time = datetime.fromisoformat(block['start_time'].replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(block['end_time'].replace('Z', '+00:00'))
                    print(f"   - {block['block_type']}: {start_time.strftime('%H:%M')} ~ {end_time.strftime('%H:%M')} ({block['duration']}分钟)")
            else:
                print(f"[ERROR] 模板应用失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    # 4. 验证生成的时间块
    print("4. 验证生成的时间块...")
    try:
        response = requests.get(f"{BASE_URL}/time-blocks?date={target_date.isoformat()}", headers=headers)
        if response.status_code == 200:
            time_blocks = response.json()
            print(f"[OK] 验证成功，找到 {len(time_blocks)} 个时间块")
            for block in time_blocks:
                if block.get('template_id'):
                    print(f"   - 来自模板: {block['block_type']} ({block['duration']}分钟)")
        else:
            print(f"[ERROR] 验证时间块失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 5. 获取模板详情
    print("5. 获取模板详情...")
    if templates:
        try:
            response = requests.get(f"{BASE_URL}/time-block-templates/{templates[0]['id']}", headers=headers)
            if response.status_code == 200:
                template_detail = response.json()
                print(f"[OK] 获取模板详情: {template_detail['name']}")
            else:
                print(f"[ERROR] 获取模板详情失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    # 6. 克隆模板
    print("6. 克隆模板...")
    if templates:
        try:
            response = requests.post(f"{BASE_URL}/time-block-templates/{templates[0]['id']}/clone", headers=headers)
            if response.status_code == 201:
                cloned_template = response.json().get('template')
                print(f"[OK] 模板克隆成功: {cloned_template['name']}")
            else:
                print(f"[ERROR] 模板克隆失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    print("所有时间块调度功能测试通过!")
    return True

if __name__ == "__main__":
    try:
        if test_scheduler_functionality():
            print("时间块调度功能正常，调度界面可以使用!")
        else:
            print("时间块调度功能测试失败")
    except Exception as e:
        print(f"测试异常: {e}")