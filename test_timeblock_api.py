#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api"

def test_timeblock_api():
    print("开始测试时间块API...")

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

    # 2. 创建时间块
    print("2. 创建时间块...")
    today = datetime.now().date()

    sample_timeblocks = [
        {
            "date": today.isoformat(),
            "start_time": datetime.combine(today, datetime.min.time().replace(hour=9, minute=0)).isoformat(),
            "end_time": datetime.combine(today, datetime.min.time().replace(hour=10, minute=30)).isoformat(),
            "block_type": "RESEARCH",
            "color": "#1890ff",
            "description": "科研时间块"
        },
        {
            "date": today.isoformat(),
            "start_time": datetime.combine(today, datetime.min.time().replace(hour=11, minute=0)).isoformat(),
            "end_time": datetime.combine(today, datetime.min.time().replace(hour=12, minute=0)).isoformat(),
            "block_type": "GROWTH",
            "color": "#52c41a",
            "description": "学习成长时间"
        },
        {
            "date": today.isoformat(),
            "start_time": datetime.combine(today, datetime.min.time().replace(hour=14, minute=0)).isoformat(),
            "end_time": datetime.combine(today, datetime.min.time().replace(hour=15, minute=30)).isoformat(),
            "block_type": "REVIEW",
            "color": "#fa8c16",
            "description": "复盘时间"
        },
        {
            "date": today.isoformat(),
            "start_time": datetime.combine(today, datetime.min.time().replace(hour=16, minute=0)).isoformat(),
            "end_time": datetime.combine(today, datetime.min.time().replace(hour=17, minute=0)).isoformat(),
            "block_type": "REST",
            "color": "#f5222d",
            "description": "休息时间"
        }
    ]

    created_timeblocks = []
    for timeblock_data in sample_timeblocks:
        try:
            response = requests.post(f"{BASE_URL}/time-blocks", json=timeblock_data, headers=headers)
            if response.status_code == 201:
                timeblock = response.json().get('time_block')
                created_timeblocks.append(timeblock)
                print(f"[OK] 创建时间块: {timeblock['block_type']} - {timeblock['duration']}分钟")
            else:
                print(f"[ERROR] 时间块创建失败: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    # 3. 获取时间块列表
    print("3. 获取时间块列表...")
    try:
        response = requests.get(f"{BASE_URL}/time-blocks", headers=headers)
        if response.status_code == 200:
            timeblocks = response.json()
            print(f"[OK] 获取到 {len(timeblocks)} 个时间块")
            for tb in timeblocks:
                print(f"   - {tb['block_type']}: {tb['start_time']} ~ {tb['end_time']} ({tb['duration']}分钟)")
        else:
            print(f"[ERROR] 获取时间块列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 4. 按日期获取时间块
    print("4. 按日期获取时间块...")
    try:
        response = requests.get(f"{BASE_URL}/time-blocks?date={today.isoformat()}", headers=headers)
        if response.status_code == 200:
            timeblocks_today = response.json()
            print(f"[OK] 今日时间块: {len(timeblocks_today)} 个")
        else:
            print(f"[ERROR] 按日期获取时间块失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 5. 获取单个时间块
    print("5. 获取单个时间块...")
    if created_timeblocks:
        try:
            response = requests.get(f"{BASE_URL}/time-blocks/{created_timeblocks[0]['id']}", headers=headers)
            if response.status_code == 200:
                timeblock_detail = response.json()
                print(f"[OK] 获取时间块详情: {timeblock_detail['block_type']}")
            else:
                print(f"[ERROR] 获取时间块详情失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    # 6. 更新时间块
    print("6. 更新时间块...")
    if created_timeblocks:
        update_data = {
            "color": "#722ed1",
            "description": "更新后的时间块描述"
        }
        try:
            response = requests.put(f"{BASE_URL}/time-blocks/{created_timeblocks[0]['id']}", json=update_data, headers=headers)
            if response.status_code == 200:
                updated_timeblock = response.json().get('time_block')
                print(f"[OK] 时间块更新成功")
            else:
                print(f"[ERROR] 时间块更新失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    # 7. 测试时间重叠检测
    print("7. 测试时间重叠检测...")
    overlapping_data = {
        "date": today.isoformat(),
        "start_time": datetime.combine(today, datetime.min.time().replace(hour=9, minute=30)).isoformat(),
        "end_time": datetime.combine(today, datetime.min.time().replace(hour=10, minute=0)).isoformat(),
        "block_type": "ENTERTAINMENT",
        "color": "#13c2c2"
    }

    try:
        response = requests.post(f"{BASE_URL}/time-blocks", json=overlapping_data, headers=headers)
        if response.status_code == 400:
            print("[OK] 时间重叠检测正常工作")
        else:
            print(f"[ERROR] 时间重叠检测失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

    # 8. 删除时间块
    print("8. 删除时间块...")
    for timeblock in created_timeblocks[:2]:  # 删除前两个时间块
        try:
            response = requests.delete(f"{BASE_URL}/time-blocks/{timeblock['id']}", headers=headers)
            if response.status_code == 200:
                print(f"[OK] 时间块删除成功")
            else:
                print(f"[ERROR] 时间块删除失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    print("所有时间块API测试通过!")
    return True

if __name__ == "__main__":
    try:
        if test_timeblock_api():
            print("时间块API功能正常，日历视图可以使用!")
            sys.exit(0)
        else:
            print("时间块API测试失败")
            sys.exit(1)
    except Exception as e:
        print(f"测试异常: {e}")
        sys.exit(1)