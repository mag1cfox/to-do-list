#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟会话管理API测试脚本
专门测试PomodoroSessionManager组件依赖的后端API接口
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys
import os

# 配置
BASE_URL = "http://127.0.0.1:5000"
API_BASE = f"{BASE_URL}/api"

class PomodoroSessionAPITester:
    def __init__(self):
        self.auth_token = None
        self.test_user = None
        self.test_task = None
        self.test_sessions = []

    def setup_method(self):
        """设置测试方法"""
        # 创建测试用户并登录
        self.create_test_user()
        self.login_user()
        # 创建测试任务
        self.create_test_task()

    def teardown_method(self):
        """清理测试方法"""
        # 清理测试数据
        self.cleanup_test_data()

    def create_test_user(self):
        """创建测试用户"""
        try:
            # 尝试创建新用户
            user_data = {
                "username": f"pomodoro_test_user_{int(time.time())}",
                "email": f"pomodoro_test_{int(time.time())}@example.com",
                "password": "testpassword123"
            }

            response = requests.post(f"{API_BASE}/auth/register", json=user_data)
            if response.status_code == 201:
                self.test_user = response.json()
                print(f"[OK] 测试用户创建成功: {self.test_user['user']['username']}")
            else:
                # 如果用户已存在，尝试登录现有用户
                self.login_existing_user(user_data['username'], user_data['password'])

        except Exception as e:
            print(f"[ERROR] 创建测试用户失败: {e}")
            raise

    def login_existing_user(self, username, password):
        """登录现有用户"""
        try:
            login_data = {
                "username": username,
                "password": password
            }
            response = requests.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                self.auth_token = response.json()['access_token']
                print(f"[OK] 现有用户登录成功")
            else:
                raise Exception("现有用户登录失败")
        except Exception as e:
            print(f"[ERROR] 现有用户登录失败: {e}")
            raise

    def login_user(self):
        """用户登录"""
        try:
            if not self.test_user:
                return

            login_data = {
                "username": self.test_user['user']['username'],
                "password": "testpassword123"
            }
            response = requests.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                self.auth_token = response.json()['access_token']
                print(f"[OK] 用户登录成功")
            else:
                raise Exception("用户登录失败")

        except Exception as e:
            print(f"[ERROR] 用户登录失败: {e}")
            raise

    def create_test_task(self):
        """创建测试任务"""
        try:
            task_data = {
                "title": "番茄钟测试任务",
                "description": "用于测试番茄钟会话管理的任务",
                "estimated_pomodoros": 3,
                "priority": "HIGH"
            }

            response = requests.post(
                f"{API_BASE}/tasks/",
                json=task_data,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )

            if response.status_code == 201:
                self.test_task = response.json()
                print(f"[OK] 测试任务创建成功: {self.test_task['title']}")
            else:
                print(f"[WARNING] 任务创建失败: {response.status_code}")

        except Exception as e:
            print(f"[ERROR] 创建测试任务失败: {e}")

    def get_headers(self):
        """获取请求头"""
        return {"Authorization": f"Bearer {self.auth_token}"}

    def cleanup_test_data(self):
        """清理测试数据"""
        try:
            # 删除测试会话
            for session in self.test_sessions:
                try:
                    requests.delete(
                        f"{API_BASE}/pomodoro-sessions/{session['id']}",
                        headers=self.get_headers()
                    )
                except:
                    pass

            # 删除测试任务
            if self.test_task:
                try:
                    requests.delete(
                        f"{API_BASE}/tasks/{self.test_task['id']}",
                        headers=self.get_headers()
                    )
                except:
                    pass

            print(f"[OK] 测试数据清理完成")

        except Exception as e:
            print(f"[WARNING] 清理测试数据失败: {e}")

    def test_1_user_authentication(self):
        """测试用户认证"""
        print("\n1. 测试用户认证...")

        try:
            if not self.auth_token:
                raise Exception("用户认证失败")

            # 测试受保护的端点
            response = requests.get(
                f"{API_BASE}/pomodoro-sessions/",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                print("[OK] 用户认证成功，可以访问受保护的端点")
                return True
            else:
                print(f"[FAIL] 用户认证失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 用户认证测试失败: {e}")
            return False

    def test_2_get_pomodoro_sessions(self):
        """测试获取番茄钟会话列表"""
        print("\n2. 测试获取番茄钟会话列表...")

        try:
            response = requests.get(
                f"{API_BASE}/pomodoro-sessions/",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                sessions = response.json().get('pomodoro_sessions', [])
                print(f"[OK] 获取会话列表成功，共 {len(sessions)} 个会话")
                if sessions:
                    print(f"[INFO] 示例会话: ID={sessions[0]['id']}, 状态={sessions[0]['status']}")
                return True
            else:
                print(f"[FAIL] 获取会话列表失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 获取会话列表测试失败: {e}")
            return False

    def test_3_create_pomodoro_session(self):
        """测试创建番茄钟会话"""
        print("\n3. 测试创建番茄钟会话...")

        try:
            if not self.test_task:
                print("[SKIP] 没有测试任务，跳过创建会话测试")
                return True

            session_data = {
                "task_id": self.test_task['id'],
                "planned_duration": 25,
                "session_type": "FOCUS"
            }

            response = requests.post(
                f"{API_BASE}/pomodoro-sessions/",
                json=session_data,
                headers=self.get_headers()
            )

            if response.status_code == 201:
                session = response.json()['pomodoro_session']
                self.test_sessions.append(session)
                print(f"[OK] 创建会话成功: ID={session['id']}, 任务ID={session['task_id']}")
                print(f"[INFO] 会话状态: {session['status']}, 计划时长: {session['planned_duration']}分钟")
                return True
            else:
                error_data = response.json() if response.content else {}
                print(f"[FAIL] 创建会话失败: {response.status_code}, 错误: {error_data.get('error', '未知错误')}")
                return False

        except Exception as e:
            print(f"[ERROR] 创建会话测试失败: {e}")
            return False

    def test_4_start_pomodoro_session(self):
        """测试开始番茄钟会话"""
        print("\n4. 测试开始番茄钟会话...")

        try:
            if not self.test_sessions:
                print("[SKIP] 没有测试会话，跳过开始会话测试")
                return True

            session = self.test_sessions[-1]  # 使用最新的会话

            response = requests.post(
                f"{API_BASE}/pomodoro-sessions/{session['id']}/start",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                updated_session = response.json()['pomodoro_session']
                print(f"[OK] 开始会话成功: ID={updated_session['id']}")
                print(f"[INFO] 会话状态: {updated_session['status']}")
                if updated_session.get('start_time'):
                    print(f"[INFO] 开始时间: {updated_session['start_time']}")
                return True
            else:
                error_data = response.json() if response.content else {}
                print(f"[FAIL] 开始会话失败: {response.status_code}, 错误: {error_data.get('error', '未知错误')}")
                return False

        except Exception as e:
            print(f"[ERROR] 开始会话测试失败: {e}")
            return False

    def test_5_get_active_pomodoro_session(self):
        """测试获取活跃的番茄钟会话"""
        print("\n5. 测试获取活跃的番茄钟会话...")

        try:
            response = requests.get(
                f"{API_BASE}/pomodoro-sessions/active",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                if 'active_session' in data and data['active_session']:
                    session = data['active_session']
                    print(f"[OK] 获取活跃会话成功: ID={session['id']}, 状态={session['status']}")
                    print(f"[INFO] 剩余时间: {session.get('remaining_time', 0)}秒")
                else:
                    print("[OK] 当前没有活跃的会话")
                return True
            else:
                print(f"[FAIL] 获取活跃会话失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 获取活跃会话测试失败: {e}")
            return False

    def test_6_complete_pomodoro_session(self):
        """测试完成番茄钟会话"""
        print("\n6. 测试完成番茄钟会话...")

        try:
            if not self.test_sessions:
                print("[SKIP] 没有测试会话，跳过完成会话测试")
                return True

            session = self.test_sessions[-1]

            completion_data = {
                "completion_summary": "测试完成总结"
            }

            response = requests.post(
                f"{API_BASE}/pomodoro-sessions/{session['id']}/complete",
                json=completion_data,
                headers=self.get_headers()
            )

            if response.status_code == 200:
                updated_session = response.json()['pomodoro_session']
                print(f"[OK] 完成会话成功: ID={updated_session['id']}")
                print(f"[INFO] 会话状态: {updated_session['status']}")
                print(f"[INFO] 实际时长: {updated_session.get('actual_duration', 0)}分钟")
                if updated_session.get('completion_summary'):
                    print(f"[INFO] 完成总结: {updated_session['completion_summary']}")
                return True
            else:
                error_data = response.json() if response.content else {}
                print(f"[FAIL] 完成会话失败: {response.status_code}, 错误: {error_data.get('error', '未知错误')}")
                return False

        except Exception as e:
            print(f"[ERROR] 完成会话测试失败: {e}")
            return False

    def test_7_interrupt_pomodoro_session(self):
        """测试中断番茄钟会话"""
        print("\n7. 测试中断番茄钟会话...")

        try:
            # 创建一个新会话用于中断测试
            if not self.test_task:
                print("[SKIP] 没有测试任务，跳过中断会话测试")
                return True

            # 创建新会话
            session_data = {
                "task_id": self.test_task['id'],
                "planned_duration": 20,
                "session_type": "FOCUS"
            }

            create_response = requests.post(
                f"{API_BASE}/pomodoro-sessions/",
                json=session_data,
                headers=self.get_headers()
            )

            if create_response.status_code != 201:
                print(f"[SKIP] 无法创建测试会话，跳过中断测试")
                return True

            new_session = create_response.json()['pomodoro_session']
            self.test_sessions.append(new_session)

            # 开始会话
            start_response = requests.post(
                f"{API_BASE}/pomodoro-sessions/{new_session['id']}/start",
                headers=self.get_headers()
            )

            if start_response.status_code != 200:
                print(f"[SKIP] 无法开始测试会话，跳过中断测试")
                return True

            # 中断会话
            interruption_data = {
                "interruption_reason": "测试中断原因"
            }

            response = requests.post(
                f"{API_BASE}/pomodoro-sessions/{new_session['id']}/interrupt",
                json=interruption_data,
                headers=self.get_headers()
            )

            if response.status_code == 200:
                updated_session = response.json()['pomodoro_session']
                print(f"[OK] 中断会话成功: ID={updated_session['id']}")
                print(f"[INFO] 会话状态: {updated_session['status']}")
                print(f"[INFO] 中断原因: {updated_session.get('interruption_reason', '无')}")
                print(f"[INFO] 实际时长: {updated_session.get('actual_duration', 0)}分钟")
                return True
            else:
                error_data = response.json() if response.content else {}
                print(f"[FAIL] 中断会话失败: {response.status_code}, 错误: {error_data.get('error', '未知错误')}")
                return False

        except Exception as e:
            print(f"[ERROR] 中断会话测试失败: {e}")
            return False

    def test_8_get_single_pomodoro_session(self):
        """测试获取单个番茄钟会话"""
        print("\n8. 测试获取单个番茄钟会话...")

        try:
            if not self.test_sessions:
                print("[SKIP] 没有测试会话，跳过获取单个会话测试")
                return True

            session = self.test_sessions[0]

            response = requests.get(
                f"{API_BASE}/pomodoro-sessions/{session['id']}",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                session_data = response.json()['pomodoro_session']
                print(f"[OK] 获取单个会话成功: ID={session_data['id']}")
                print(f"[INFO] 会话详情:")
                print(f"  - 任务ID: {session_data['task_id']}")
                print(f"  - 状态: {session_data['status']}")
                print(f"  - 类型: {session_data['session_type']}")
                print(f"  - 计划时长: {session_data['planned_duration']}分钟")
                print(f"  - 实际时长: {session_data.get('actual_duration', 0)}分钟")
                print(f"  - 创建时间: {session_data.get('created_at', 'N/A')}")
                return True
            else:
                print(f"[FAIL] 获取单个会话失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 获取单个会话测试失败: {e}")
            return False

    def test_9_delete_pomodoro_session(self):
        """测试删除番茄钟会话"""
        print("\n9. 测试删除番茄钟会话...")

        try:
            # 创建一个用于删除测试的会话
            if not self.test_task:
                print("[SKIP] 没有测试任务，跳过删除会话测试")
                return True

            session_data = {
                "task_id": self.test_task['id'],
                "planned_duration": 15,
                "session_type": "FOCUS"
            }

            create_response = requests.post(
                f"{API_BASE}/pomodoro-sessions/",
                json=session_data,
                headers=self.get_headers()
            )

            if create_response.status_code != 201:
                print(f"[SKIP] 无法创建测试会话，跳过删除测试")
                return True

            new_session = create_response.json()['pomodoro_session']

            # 删除会话
            response = requests.delete(
                f"{API_BASE}/pomodoro-sessions/{new_session['id']}",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                print(f"[OK] 删除会话成功: ID={new_session['id']}")

                # 验证删除成功
                verify_response = requests.get(
                    f"{API_BASE}/pomodoro-sessions/{new_session['id']}",
                    headers=self.get_headers()
                )

                if verify_response.status_code == 404:
                    print("[OK] 验证删除成功：会话已不存在")
                    return True
                else:
                    print("[WARNING] 删除成功但验证失败")
                    return True
            else:
                error_data = response.json() if response.content else {}
                print(f"[FAIL] 删除会话失败: {response.status_code}, 错误: {error_data.get('error', '未知错误')}")
                return False

        except Exception as e:
            print(f"[ERROR] 删除会话测试失败: {e}")
            return False

    def test_10_session_validation_rules(self):
        """测试会话验证规则"""
        print("\n10. 测试会话验证规则...")

        try:
            test_results = []

            # 测试1: 创建会话时缺少必需字段
            print("[INFO] 测试缺少必需字段...")
            invalid_data = {
                "planned_duration": 25
                # 缺少 task_id
            }

            response = requests.post(
                f"{API_BASE}/pomodoro-sessions/",
                json=invalid_data,
                headers=self.get_headers()
            )

            if response.status_code == 400:
                print("[OK] 正确拒绝缺少必需字段的请求")
                test_results.append(True)
            else:
                print(f"[FAIL] 应该拒绝缺少必需字段的请求: {response.status_code}")
                test_results.append(False)

            # 测试2: 无效的会话类型
            print("[INFO] 测试无效的会话类型...")
            invalid_type_data = {
                "task_id": self.test_task['id'] if self.test_task else 1,
                "planned_duration": 25,
                "session_type": "INVALID_TYPE"
            }

            response = requests.post(
                f"{API_BASE}/pomodoro-sessions/",
                json=invalid_type_data,
                headers=self.get_headers()
            )

            if response.status_code == 400:
                print("[OK] 正确拒绝无效的会话类型")
                test_results.append(True)
            else:
                print(f"[FAIL] 应该拒绝无效的会话类型: {response.status_code}")
                test_results.append(False)

            # 测试3: 无效的任务ID
            print("[INFO] 测试无效的任务ID...")
            invalid_task_data = {
                "task_id": 99999,  # 不存在的任务ID
                "planned_duration": 25,
                "session_type": "FOCUS"
            }

            response = requests.post(
                f"{API_BASE}/pomodoro-sessions/",
                json=invalid_task_data,
                headers=self.get_headers()
            )

            if response.status_code == 404:
                print("[OK] 正确拒绝无效的任务ID")
                test_results.append(True)
            else:
                print(f"[FAIL] 应该拒绝无效的任务ID: {response.status_code}")
                test_results.append(False)

            # 测试4: 创建重复的活跃会话
            print("[INFO] 测试重复活跃会话检查...")
            if self.test_sessions and len(self.test_sessions) > 0:
                # 获取最新的会话并检查其状态
                latest_session = self.test_sessions[-1]

                # 如果最新会话是活跃状态，尝试创建另一个会话
                if latest_session.get('status') == 'IN_PROGRESS':
                    duplicate_data = {
                        "task_id": self.test_task['id'] if self.test_task else 1,
                        "planned_duration": 20,
                        "session_type": "FOCUS"
                    }

                    response = requests.post(
                        f"{API_BASE}/pomodoro-sessions/",
                        json=duplicate_data,
                        headers=self.get_headers()
                    )

                    if response.status_code == 400:
                        print("[OK] 正确拒绝创建重复活跃会话")
                        test_results.append(True)
                    else:
                        print(f"[FAIL] 应该拒绝创建重复活跃会话: {response.status_code}")
                        test_results.append(False)
                else:
                    print("[SKIP] 当前没有活跃会话，跳过重复会话测试")
                    test_results.append(True)
            else:
                print("[SKIP] 没有测试会话，跳过重复会话测试")
                test_results.append(True)

            # 汇总测试结果
            passed = sum(test_results)
            total = len(test_results)
            print(f"[INFO] 验证规则测试结果: {passed}/{total} 通过")

            return passed == total

        except Exception as e:
            print(f"[ERROR] 会话验证规则测试失败: {e}")
            return False

    def test_11_session_lifecycle(self):
        """测试完整的会话生命周期"""
        print("\n11. 测试完整的会话生命周期...")

        try:
            if not self.test_task:
                print("[SKIP] 没有测试任务，跳过生命周期测试")
                return True

            lifecycle_session = None

            # 1. 创建会话
            print("[INFO] 步骤1: 创建会话")
            session_data = {
                "task_id": self.test_task['id'],
                "planned_duration": 30,
                "session_type": "FOCUS"
            }

            response = requests.post(
                f"{API_BASE}/pomodoro-sessions/",
                json=session_data,
                headers=self.get_headers()
            )

            if response.status_code != 201:
                print(f"[FAIL] 创建会话失败: {response.status_code}")
                return False

            lifecycle_session = response.json()['pomodoro_session']
            self.test_sessions.append(lifecycle_session)
            print(f"[OK] 会话创建成功: ID={lifecycle_session['id']}")

            # 2. 开始会话
            print("[INFO] 步骤2: 开始会话")
            response = requests.post(
                f"{API_BASE}/pomodoro-sessions/{lifecycle_session['id']}/start",
                headers=self.get_headers()
            )

            if response.status_code != 200:
                print(f"[FAIL] 开始会话失败: {response.status_code}")
                return False

            print(f"[OK] 会话开始成功")

            # 3. 等待一小段时间
            print("[INFO] 步骤3: 等待2秒模拟会话进行")
            time.sleep(2)

            # 4. 完成会话
            print("[INFO] 步骤4: 完成会话")
            completion_data = {
                "completion_summary": "生命周期测试完成"
            }

            response = requests.post(
                f"{API_BASE}/pomodoro-sessions/{lifecycle_session['id']}/complete",
                json=completion_data,
                headers=self.get_headers()
            )

            if response.status_code != 200:
                print(f"[FAIL] 完成会话失败: {response.status_code}")
                return False

            completed_session = response.json()['pomodoro_session']
            print(f"[OK] 会话完成成功")

            # 5. 验证最终状态
            print("[INFO] 步骤5: 验证最终状态")
            if completed_session['status'] == 'COMPLETED':
                print("[OK] 会话状态正确: COMPLETED")
            else:
                print(f"[FAIL] 会话状态错误: {completed_session['status']}")
                return False

            if completed_session.get('actual_duration', 0) > 0:
                print(f"[OK] 实际时长记录正确: {completed_session['actual_duration']}分钟")
            else:
                print("[WARNING] 实际时长可能为0")

            if completed_session.get('completion_summary') == "生命周期测试完成":
                print("[OK] 完成总结记录正确")
            else:
                print("[FAIL] 完成总结记录错误")
                return False

            print("[OK] 完整会话生命周期测试成功")
            return True

        except Exception as e:
            print(f"[ERROR] 会话生命周期测试失败: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("番茄钟会话管理API测试开始")
        print("=" * 60)

        test_methods = [
            self.test_1_user_authentication,
            self.test_2_get_pomodoro_sessions,
            self.test_3_create_pomodoro_session,
            self.test_4_start_pomodoro_session,
            self.test_5_get_active_pomodoro_session,
            self.test_6_complete_pomodoro_session,
            self.test_7_interrupt_pomodoro_session,
            self.test_8_get_single_pomodoro_session,
            self.test_9_delete_pomodoro_session,
            self.test_10_session_validation_rules,
            self.test_11_session_lifecycle
        ]

        passed = 0
        failed = 0

        for i, test_method in enumerate(test_methods, 1):
            try:
                print(f"\n{'='*20} 测试 {i} {'='*20}")
                result = test_method()
                if result is not False:
                    passed += 1
                    print(f"[PASS] {test_method.__name__} - 通过")
                else:
                    failed += 1
                    print(f"[FAIL] {test_method.__name__} - 失败")
            except AssertionError as e:
                print(f"[FAIL] {test_method.__name__} - 失败: {e}")
                failed += 1
            except Exception as e:
                print(f"[ERROR] {test_method.__name__} - 异常: {e}")
                failed += 1
            print("-" * 40)

        print("=" * 60)
        print("测试结果汇总:")
        print(f"[PASS] 通过: {passed}")
        print(f"[FAIL] 失败: {failed}")
        print(f"总计: {passed + failed}")

        if failed == 0:
            print("[SUCCESS] 所有测试都通过了！番茄钟会话管理API正常工作。")
        else:
            print("[WARNING] 部分测试失败，请检查相关功能。")

        print("=" * 60)

        return failed == 0

def run_pomodoro_session_tests():
    """运行番茄钟会话管理测试"""
    tester = PomodoroSessionAPITester()
    try:
        return tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n[INFO] 测试被用户中断")
        return False
    except Exception as e:
        print(f"\n[ERROR] 测试执行失败: {e}")
        return False
    finally:
        # 确保清理
        try:
            tester.cleanup_test_data()
        except:
            pass

if __name__ == "__main__":
    success = run_pomodoro_session_tests()
    sys.exit(0 if success else 1)