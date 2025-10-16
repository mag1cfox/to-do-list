#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据可视化报表API测试脚本
专门测试DataVisualizationReport组件依赖的后端API接口
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

class DataVisualizationAPITester:
    def __init__(self):
        self.auth_token = None
        self.test_user = None
        self.test_data = {
            'tasks': [],
            'projects': [],
            'categories': [],
            'pomodoro_sessions': [],
            'time_blocks': []
        }

    def setup_method(self):
        """设置测试方法"""
        # 创建测试用户并登录
        self.create_test_user()
        self.login_user()
        # 创建测试数据
        self.create_test_data()

    def teardown_method(self):
        """清理测试方法"""
        # 清理测试数据
        self.cleanup_test_data()

    def create_test_user(self):
        """创建测试用户"""
        try:
            # 尝试创建新用户
            user_data = {
                "username": f"viz_test_user_{int(time.time())}",
                "email": f"viz_test_{int(time.time())}@example.com",
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

    def create_test_data(self):
        """创建测试数据"""
        try:
            # 创建项目
            self.create_test_projects()
            # 创建任务类别
            self.create_test_categories()
            # 创建任务
            self.create_test_tasks()
            # 创建番茄钟会话
            self.create_test_pomodoro_sessions()
            # 创建时间块
            self.create_test_time_blocks()

            print(f"[OK] 测试数据创建完成")

        except Exception as e:
            print(f"[ERROR] 创建测试数据失败: {e}")

    def create_test_projects(self):
        """创建测试项目"""
        try:
            project_data = {
                "name": "数据可视化测试项目",
                "description": "用于测试数据可视化报表的项目",
                "color": "#1890ff"
            }

            response = requests.post(
                f"{API_BASE}/projects/",
                json=project_data,
                headers=self.get_headers()
            )

            if response.status_code == 201:
                project = response.json()
                self.test_data['projects'].append(project)
                print(f"[OK] 测试项目创建成功: {project['name']}")
            else:
                print(f"[WARNING] 项目创建失败: {response.status_code}")

        except Exception as e:
            print(f"[ERROR] 创建测试项目失败: {e}")

    def create_test_categories(self):
        """创建测试任务类别"""
        try:
            category_data = {
                "name": "数据分析",
                "description": "数据分析相关任务",
                "color": "#52c41a"
            }

            response = requests.post(
                f"{API_BASE}/task-categories/",
                json=category_data,
                headers=self.get_headers()
            )

            if response.status_code == 201:
                category = response.json()
                self.test_data['categories'].append(category)
                print(f"[OK] 测试类别创建成功: {category['name']}")
            else:
                print(f"[WARNING] 类别创建失败: {response.status_code}")

        except Exception as e:
            print(f"[ERROR] 创建测试类别失败: {e}")

    def create_test_tasks(self):
        """创建测试任务"""
        try:
            tasks_data = [
                {
                    "title": "数据分析任务1",
                    "description": "第一个数据分析测试任务",
                    "status": "COMPLETED",
                    "priority": "HIGH",
                    "estimated_pomodoros": 3,
                    "project_id": self.test_data['projects'][0]['id'] if self.test_data['projects'] else None,
                    "category_id": self.test_data['categories'][0]['id'] if self.test_data['categories'] else None
                },
                {
                    "title": "报表生成任务",
                    "description": "生成数据可视化报表",
                    "status": "IN_PROGRESS",
                    "priority": "MEDIUM",
                    "estimated_pomodoros": 2,
                    "project_id": self.test_data['projects'][0]['id'] if self.test_data['projects'] else None,
                    "category_id": self.test_data['categories'][0]['id'] if self.test_data['categories'] else None
                },
                {
                    "title": "API测试任务",
                    "description": "测试API接口功能",
                    "status": "PENDING",
                    "priority": "LOW",
                    "estimated_pomodoros": 1,
                    "project_id": self.test_data['projects'][0]['id'] if self.test_data['projects'] else None
                }
            ]

            for task_data in tasks_data:
                response = requests.post(
                    f"{API_BASE}/tasks/",
                    json=task_data,
                    headers=self.get_headers()
                )

                if response.status_code == 201:
                    task = response.json()
                    self.test_data['tasks'].append(task)
                    print(f"[OK] 测试任务创建成功: {task['title']}")
                else:
                    print(f"[WARNING] 任务创建失败: {response.status_code}")

        except Exception as e:
            print(f"[ERROR] 创建测试任务失败: {e}")

    def create_test_pomodoro_sessions(self):
        """创建测试番茄钟会话"""
        try:
            if not self.test_data['tasks']:
                print("[SKIP] 没有测试任务，跳过创建番茄钟会话")
                return

            for task in self.test_data['tasks'][:2]:  # 只为前两个任务创建会话
                session_data = {
                    "task_id": task['id'],
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
                    self.test_data['pomodoro_sessions'].append(session)
                    print(f"[OK] 测试番茄钟会话创建成功: 任务ID={task['id']}")

                    # 尝试开始并完成一些会话
                    if task['status'] == 'COMPLETED':
                        self.complete_pomodoro_session(session['id'])
                else:
                    print(f"[WARNING] 番茄钟会话创建失败: {response.status_code}")

        except Exception as e:
            print(f"[ERROR] 创建测试番茄钟会话失败: {e}")

    def complete_pomodoro_session(self, session_id):
        """完成番茄钟会话"""
        try:
            # 开始会话
            start_response = requests.post(
                f"{API_BASE}/pomodoro-sessions/{session_id}/start",
                headers=self.get_headers()
            )

            if start_response.status_code == 200:
                # 完成会话
                completion_data = {
                    "completion_summary": "测试会话完成"
                }
                complete_response = requests.post(
                    f"{API_BASE}/pomodoro-sessions/{session_id}/complete",
                    json=completion_data,
                    headers=self.get_headers()
                )

                if complete_response.status_code == 200:
                    print(f"[OK] 番茄钟会话完成成功: {session_id}")
        except Exception as e:
            print(f"[ERROR] 完成番茄钟会话失败: {e}")

    def create_test_time_blocks(self):
        """创建测试时间块"""
        try:
            time_blocks_data = [
                {
                    "date": datetime.now().isoformat(),
                    "start_time": datetime.now().replace(hour=9, minute=0).isoformat(),
                    "end_time": datetime.now().replace(hour=10, minute=0).isoformat(),
                    "block_type": "RESEARCH",
                    "color": "#1890ff",
                    "description": "数据分析时间块"
                },
                {
                    "date": datetime.now().isoformat(),
                    "start_time": datetime.now().replace(hour=14, minute=0).isoformat(),
                    "end_time": datetime.now().replace(hour=15, minute=0).isoformat(),
                    "block_type": "GROWTH",
                    "color": "#52c41a",
                    "description": "学习成长时间块"
                }
            ]

            for block_data in time_blocks_data:
                response = requests.post(
                    f"{API_BASE}/time-blocks/",
                    json=block_data,
                    headers=self.get_headers()
                )

                if response.status_code == 201:
                    time_block = response.json()
                    self.test_data['time_blocks'].append(time_block)
                    print(f"[OK] 测试时间块创建成功: {block_data['block_type']}")
                else:
                    print(f"[WARNING] 时间块创建失败: {response.status_code}")

        except Exception as e:
            print(f"[ERROR] 创建测试时间块失败: {e}")

    def get_headers(self):
        """获取请求头"""
        return {"Authorization": f"Bearer {self.auth_token}"}

    def cleanup_test_data(self):
        """清理测试数据"""
        try:
            # 删除测试数据
            for session in self.test_data['pomodoro_sessions']:
                try:
                    requests.delete(
                        f"{API_BASE}/pomodoro-sessions/{session['id']}",
                        headers=self.get_headers()
                    )
                except:
                    pass

            for task in self.test_data['tasks']:
                try:
                    requests.delete(
                        f"{API_BASE}/tasks/{task['id']}",
                        headers=self.get_headers()
                    )
                except:
                    pass

            for category in self.test_data['categories']:
                try:
                    requests.delete(
                        f"{API_BASE}/task-categories/{category['id']}",
                        headers=self.get_headers()
                    )
                except:
                    pass

            for project in self.test_data['projects']:
                try:
                    requests.delete(
                        f"{API_BASE}/projects/{project['id']}",
                        headers=self.get_headers()
                    )
                except:
                    pass

            for time_block in self.test_data['time_blocks']:
                try:
                    requests.delete(
                        f"{API_BASE}/time-blocks/{time_block['id']}",
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
                f"{API_BASE}/tasks/",
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

    def test_2_get_tasks_api(self):
        """测试获取任务API"""
        print("\n2. 测试获取任务API...")

        try:
            response = requests.get(
                f"{API_BASE}/tasks/",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                tasks = response.json()
                print(f"[OK] 获取任务列表成功，共 {len(tasks.get('tasks', []))} 个任务")
                if tasks.get('tasks'):
                    print(f"[INFO] 示例任务: {tasks['tasks'][0].get('title', 'N/A')}")
                return True
            else:
                print(f"[FAIL] 获取任务列表失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 获取任务API测试失败: {e}")
            return False

    def test_3_get_projects_api(self):
        """测试获取项目API"""
        print("\n3. 测试获取项目API...")

        try:
            response = requests.get(
                f"{API_BASE}/projects/",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                projects = response.json()
                print(f"[OK] 获取项目列表成功，共 {len(projects)} 个项目")
                if projects:
                    print(f"[INFO] 示例项目: {projects[0].get('name', 'N/A')}")
                return True
            else:
                print(f"[FAIL] 获取项目列表失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 获取项目API测试失败: {e}")
            return False

    def test_4_get_categories_api(self):
        """测试获取任务类别API"""
        print("\n4. 测试获取任务类别API...")

        try:
            response = requests.get(
                f"{API_BASE}/task-categories/",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                categories = response.json()
                print(f"[OK] 获取类别列表成功，共 {len(categories)} 个类别")
                if categories:
                    print(f"[INFO] 示例类别: {categories[0].get('name', 'N/A')}")
                return True
            else:
                print(f"[FAIL] 获取类别列表失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 获取类别API测试失败: {e}")
            return False

    def test_5_get_pomodoro_sessions_api(self):
        """测试获取番茄钟会话API"""
        print("\n5. 测试获取番茄钟会话API...")

        try:
            response = requests.get(
                f"{API_BASE}/pomodoro-sessions/",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                sessions = response.json()
                session_list = sessions.get('pomodoro_sessions', [])
                print(f"[OK] 获取番茄钟会话列表成功，共 {len(session_list)} 个会话")
                if session_list:
                    print(f"[INFO] 示例会话: 状态={session_list[0].get('status', 'N/A')}")
                return True
            else:
                print(f"[FAIL] 获取番茄钟会话列表失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 获取番茄钟会话API测试失败: {e}")
            return False

    def test_6_get_time_blocks_api(self):
        """测试获取时间块API"""
        print("\n6. 测试获取时间块API...")

        try:
            response = requests.get(
                f"{API_BASE}/time-blocks/",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                time_blocks = response.json()
                block_list = time_blocks.get('time_blocks', [])
                print(f"[OK] 获取时间块列表成功，共 {len(block_list)} 个时间块")
                if block_list:
                    print(f"[INFO] 示例时间块: 类型={block_list[0].get('block_type', 'N/A')}")
                return True
            else:
                print(f"[FAIL] 获取时间块列表失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 获取时间块API测试失败: {e}")
            return False

    def test_7_data_completeness(self):
        """测试数据完整性"""
        print("\n7. 测试数据完整性...")

        try:
            # 获取所有数据
            tasks_response = requests.get(f"{API_BASE}/tasks/", headers=self.get_headers())
            sessions_response = requests.get(f"{API_BASE}/pomodoro-sessions/", headers=self.get_headers())
            projects_response = requests.get(f"{API_BASE}/projects/", headers=self.get_headers())
            categories_response = requests.get(f"{API_BASE}/task-categories/", headers=self.get_headers())
            time_blocks_response = requests.get(f"{API_BASE}/time-blocks/", headers=self.get_headers())

            # 检查数据完整性
            tasks = tasks_response.json().get('tasks', [])
            sessions = sessions_response.json().get('pomodoro_sessions', [])
            projects = projects_response.json() or []
            categories = categories_response.json() or []
            time_blocks = time_blocks_response.json().get('time_blocks', [])

            # 验证关联关系
            data_integrity_issues = []

            # 检查任务的项目关联
            for task in tasks:
                if task.get('project_id'):
                    project_exists = any(p['id'] == task['project_id'] for p in projects)
                    if not project_exists:
                        data_integrity_issues.append(f"任务 {task['id']} 引用了不存在的项目 {task['project_id']}")

                if task.get('category_id'):
                    category_exists = any(c['id'] == task['category_id'] for c in categories)
                    if not category_exists:
                        data_integrity_issues.append(f"任务 {task['id']} 引用了不存在的类别 {task['category_id']}")

            # 检查番茄钟会话的任务关联
            for session in sessions:
                if session.get('task_id'):
                    task_exists = any(t['id'] == session['task_id'] for t in tasks)
                    if not task_exists:
                        data_integrity_issues.append(f"会话 {session['id']} 引用了不存在的任务 {session['task_id']}")

            if data_integrity_issues:
                print(f"[FAIL] 发现数据完整性问题:")
                for issue in data_integrity_issues[:5]:  # 只显示前5个问题
                    print(f"  - {issue}")
                return False
            else:
                print("[OK] 数据完整性检查通过")
                print(f"[INFO] 数据统计: 任务={len(tasks)}, 会话={len(sessions)}, 项目={len(projects)}, 类别={len(categories)}, 时间块={len(time_blocks)}")
                return True

        except Exception as e:
            print(f"[ERROR] 数据完整性测试失败: {e}")
            return False

    def test_8_filtering_and_pagination(self):
        """测试过滤和分页功能"""
        print("\n8. 测试过滤和分页功能...")

        try:
            # 测试任务状态过滤
            response = requests.get(
                f"{API_BASE}/tasks/?status=COMPLETED",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                completed_tasks = response.json().get('tasks', [])
                print(f"[OK] 状态过滤成功，已完成任务 {len(completed_tasks)} 个")

                # 验证过滤结果
                all_completed = all(task.get('status') == 'COMPLETED' for task in completed_tasks)
                if not all_completed and completed_tasks:
                    print(f"[WARNING] 过滤结果中包含非已完成任务")
            else:
                print(f"[FAIL] 状态过滤失败: {response.status_code}")
                return False

            # 测试任务分页
            response = requests.get(
                f"{API_BASE}/tasks/?page=1&limit=2",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                paginated_tasks = response.json().get('tasks', [])
                print(f"[OK] 分页功能正常，返回 {len(paginated_tasks)} 个任务")
            else:
                print(f"[FAIL] 分页功能失败: {response.status_code}")
                return False

            return True

        except Exception as e:
            print(f"[ERROR] 过滤和分页测试失败: {e}")
            return False

    def test_9_data_consistency(self):
        """测试数据一致性"""
        print("\n9. 测试数据一致性...")

        try:
            # 获取任务数据
            tasks_response = requests.get(f"{API_BASE}/tasks/", headers=self.get_headers())
            tasks = tasks_response.json().get('tasks', [])

            # 获取番茄钟会话数据
            sessions_response = requests.get(f"{API_BASE}/pomodoro-sessions/", headers=self.get_headers())
            sessions = sessions_response.json().get('pomodoro_sessions', [])

            # 统计任务状态
            task_status_count = {}
            for task in tasks:
                status = task.get('status', 'UNKNOWN')
                task_status_count[status] = task_status_count.get(status, 0) + 1

            # 统计番茄钟会话状态
            session_status_count = {}
            for session in sessions:
                status = session.get('status', 'UNKNOWN')
                session_status_count[status] = session_status_count.get(status, 0) + 1

            print(f"[INFO] 任务状态统计: {task_status_count}")
            print(f"[INFO] 会话状态统计: {session_status_count}")

            # 检查数据一致性
            if tasks and not task_status_count:
                print("[WARNING] 有任务数据但状态统计为空")
                return False

            if sessions and not session_status_count:
                print("[WARNING] 有会话数据但状态统计为空")
                return False

            print("[OK] 数据一致性检查通过")
            return True

        except Exception as e:
            print(f"[ERROR] 数据一致性测试失败: {e}")
            return False

    def test_10_api_performance(self):
        """测试API性能"""
        print("\n10. 测试API性能...")

        try:
            # 测试多个API的响应时间
            api_endpoints = [
                "/tasks/",
                "/projects/",
                "/task-categories/",
                "/pomodoro-sessions/",
                "/time-blocks/"
            ]

            performance_results = {}

            for endpoint in api_endpoints:
                start_time = time.time()
                response = requests.get(f"{API_BASE}{endpoint}", headers=self.get_headers())
                end_time = time.time()

                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                performance_results[endpoint] = {
                    'status_code': response.status_code,
                    'response_time_ms': round(response_time, 2)
                }

                print(f"[INFO] {endpoint}: {response.status_code}, {response_time:.2f}ms")

            # 检查性能是否可接受（小于2秒）
            slow_endpoints = [ep for ep, data in performance_results.items() if data['response_time_ms'] > 2000]

            if slow_endpoints:
                print(f"[WARNING] 以下端点响应较慢: {slow_endpoints}")
                return False
            else:
                print("[OK] API性能测试通过，所有端点响应时间正常")
                return True

        except Exception as e:
            print(f"[ERROR] API性能测试失败: {e}")
            return False

    def test_11_comprehensive_data_aggregation(self):
        """测试综合数据聚合"""
        print("\n11. 测试综合数据聚合...")

        try:
            # 获取所有相关数据
            tasks_response = requests.get(f"{API_BASE}/tasks/", headers=self.get_headers())
            sessions_response = requests.get(f"{API_BASE}/pomodoro-sessions/", headers=self.get_headers())
            projects_response = requests.get(f"{API_BASE}/projects/", headers=self.get_headers())

            tasks = tasks_response.json().get('tasks', [])
            sessions = sessions_response.json().get('pomodoro_sessions', [])
            projects = projects_response.json() or []

            # 计算关键统计指标
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.get('status') == 'COMPLETED'])
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            total_sessions = len(sessions)
            completed_sessions = len([s for s in sessions if s.get('status') == 'COMPLETED'])
            session_completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0

            # 计算总专注时间
            total_focus_time = sum(s.get('actual_duration', s.get('planned_duration', 0)) for s in sessions)

            # 计算项目分布
            project_distribution = {}
            for task in tasks:
                project_id = task.get('project_id')
                project_name = "个人任务"
                if project_id:
                    project = next((p for p in projects if p['id'] == project_id), None)
                    if project:
                        project_name = project.get('name', '未知项目')

                project_distribution[project_name] = project_distribution.get(project_name, 0) + 1

            print(f"[INFO] 综合统计结果:")
            print(f"  - 总任务数: {total_tasks}")
            print(f"  - 任务完成率: {completion_rate:.1f}%")
            print(f"  - 番茄钟会话数: {total_sessions}")
            print(f"  - 会话完成率: {session_completion_rate:.1f}%")
            print(f"  - 总专注时间: {total_focus_time}分钟")
            print(f"  - 项目分布: {project_distribution}")

            # 验证数据合理性
            if total_tasks > 0 and completion_rate > 100:
                print("[FAIL] 任务完成率超过100%，数据异常")
                return False

            if total_sessions > 0 and session_completion_rate > 100:
                print("[FAIL] 会话完成率超过100%，数据异常")
                return False

            if total_focus_time < 0:
                print("[FAIL] 专注时间为负数，数据异常")
                return False

            print("[OK] 综合数据聚合测试通过")
            return True

        except Exception as e:
            print(f"[ERROR] 综合数据聚合测试失败: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("数据可视化报表API测试开始")
        print("=" * 60)

        test_methods = [
            self.test_1_user_authentication,
            self.test_2_get_tasks_api,
            self.test_3_get_projects_api,
            self.test_4_get_categories_api,
            self.test_5_get_pomodoro_sessions_api,
            self.test_6_get_time_blocks_api,
            self.test_7_data_completeness,
            self.test_8_filtering_and_pagination,
            self.test_9_data_consistency,
            self.test_10_api_performance,
            self.test_11_comprehensive_data_aggregation
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
            print("[SUCCESS] 所有测试都通过了！数据可视化报表API正常工作。")
        else:
            print("[WARNING] 部分测试失败，请检查相关功能。")

        print("=" * 60)

        return failed == 0

def run_data_visualization_tests():
    """运行数据可视化报表测试"""
    tester = DataVisualizationAPITester()
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
    success = run_data_visualization_tests()
    sys.exit(0 if success else 1)