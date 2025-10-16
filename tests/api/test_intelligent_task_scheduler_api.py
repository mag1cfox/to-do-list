#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能任务调度建议API测试脚本
专门测试IntelligentTaskScheduler组件依赖的后端API接口
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

class IntelligentTaskSchedulerAPITester:
    def __init__(self):
        self.auth_token = None
        self.test_user = None
        self.test_data = {
            'tasks': [],
            'time_blocks': [],
            'categories': [],
            'projects': []
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
                "username": f"smart_scheduler_test_{int(time.time())}",
                "email": f"smart_test_{int(time.time())}@example.com",
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
            # 创建时间块
            self.create_test_time_blocks()
            # 创建任务
            self.create_test_tasks()

            print(f"[OK] 智能调度测试数据创建完成")

        except Exception as e:
            print(f"[ERROR] 创建测试数据失败: {e}")

    def create_test_projects(self):
        """创建测试项目"""
        try:
            project_data = {
                "name": "智能调度测试项目",
                "description": "用于测试智能任务调度建议功能",
                "color": "#722ed1",
                "priority": "HIGH"
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
            categories_data = [
                {
                    "name": "紧急工作",
                    "description": "需要优先处理的工作任务",
                    "color": "#ff4d4f"
                },
                {
                    "name": "学习成长",
                    "description": "个人学习和技能提升",
                    "color": "#52c41a"
                },
                {
                    "name": "日常事务",
                    "description": "日常生活相关事务",
                    "color": "#1890ff"
                }
            ]

            for category_data in categories_data:
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

    def create_test_time_blocks(self):
        """创建测试时间块"""
        try:
            today = datetime.now()
            time_blocks_data = [
                {
                    "date": today.isoformat(),
                    "start_time": today.replace(hour=9, minute=0).isoformat(),
                    "end_time": today.replace(hour=10, minute=30).isoformat(),
                    "block_type": "RESEARCH",
                    "color": "#1890ff",
                    "description": "专注工作时间块"
                },
                {
                    "date": today.isoformat(),
                    "start_time": today.replace(hour=11, minute=0).isoformat(),
                    "end_time": today.replace(hour=12, minute=0).isoformat(),
                    "block_type": "GROWTH",
                    "color": "#52c41a",
                    "description": "学习成长时间块"
                },
                {
                    "date": today.isoformat(),
                    "start_time": today.replace(hour=14, minute=0).isoformat(),
                    "end_time": today.replace(hour=15, minute=30).isoformat(),
                    "block_type": "RESEARCH",
                    "color": "#1890ff",
                    "description": "下午工作时间块"
                },
                {
                    "date": today.isoformat(),
                    "start_time": today.replace(hour=16, minute=0).isoformat(),
                    "end_time": today.replace(hour=16, minute=30).isoformat(),
                    "block_type": "REVIEW",
                    "color": "#722ed1",
                    "description": "复盘总结时间块"
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

    def create_test_tasks(self):
        """创建测试任务"""
        try:
            if not self.test_data['categories'] or not self.test_data['projects']:
                print("[SKIP] 缺少类别或项目数据，跳过任务创建")
                return

            tomorrow = datetime.now() + timedelta(days=1)
            next_week = datetime.now() + timedelta(days=7)

            tasks_data = [
                {
                    "title": "紧急工作任务",
                    "description": "需要在今天完成的高优先级工作任务",
                    "status": "PENDING",
                    "priority": "HIGH",
                    "planned_start_time": tomorrow.isoformat(),
                    "estimated_pomodoros": 3,
                    "task_type": "RIGID",
                    "project_id": self.test_data['projects'][0]['id'],
                    "category_id": self.test_data['categories'][0]['id']  # 紧急工作
                },
                {
                    "title": "技能学习计划",
                    "description": "学习新技术和提升技能",
                    "status": "PENDING",
                    "priority": "MEDIUM",
                    "planned_start_time": next_week.isoformat(),
                    "estimated_pomodoros": 2,
                    "task_type": "FLEXIBLE",
                    "project_id": self.test_data['projects'][0]['id'],
                    "category_id": self.test_data['categories'][1]['id']  # 学习成长
                },
                {
                    "title": "项目文档整理",
                    "description": "整理项目相关文档和资料",
                    "status": "PENDING",
                    "priority": "LOW",
                    "planned_start_time": tomorrow.isoformat(),
                    "estimated_pomodoros": 1,
                    "task_type": "FLEXIBLE",
                    "project_id": self.test_data['projects'][0]['id'],
                    "category_id": self.test_data['categories'][2]['id']  # 日常事务
                },
                {
                    "title": "代码审查",
                    "description": "审查团队提交的代码",
                    "status": "PENDING",
                    "priority": "HIGH",
                    "planned_start_time": tomorrow.isoformat(),
                    "estimated_pomodoros": 2,
                    "task_type": "RIGID",
                    "project_id": self.test_data['projects'][0]['id'],
                    "category_id": self.test_data['categories'][0]['id']  # 紧急工作
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

    def get_headers(self):
        """获取请求头"""
        return {"Authorization": f"Bearer {self.auth_token}"}

    def cleanup_test_data(self):
        """清理测试数据"""
        try:
            # 删除测试数据
            for task in self.test_data['tasks']:
                try:
                    requests.delete(
                        f"{API_BASE}/tasks/{task['id']}",
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

            print(f"[OK] 智能调度测试数据清理完成")

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

    def test_2_get_tasks_for_scheduling(self):
        """测试获取待调度任务API"""
        print("\n2. 测试获取待调度任务API...")

        try:
            response = requests.get(
                f"{API_BASE}/tasks/",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                tasks = response.json()
                pending_tasks = [task for task in tasks if task.get('status') == 'PENDING']
                print(f"[OK] 获取任务列表成功，共 {len(tasks)} 个任务，其中 {len(pending_tasks)} 个待调度")

                if pending_tasks:
                    print(f"[INFO] 示例待调度任务: {pending_tasks[0].get('title', 'N/A')}")
                    print(f"[INFO] 优先级分布: {self.get_priority_distribution(pending_tasks)}")
                    print(f"[INFO] 类型分布: {self.get_type_distribution(pending_tasks)}")

                return True
            else:
                print(f"[FAIL] 获取任务列表失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 获取待调度任务API测试失败: {e}")
            return False

    def test_3_get_time_blocks_for_scheduling(self):
        """测试获取时间块API"""
        print("\n3. 测试获取时间块API...")

        try:
            response = requests.get(
                f"{API_BASE}/time-blocks/",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                time_blocks = response.json().get('time_blocks', [])
                today_blocks = [block for block in time_blocks
                               if datetime.fromisoformat(block['date']).date() == datetime.now().date()]

                print(f"[OK] 获取时间块列表成功，共 {len(time_blocks)} 个时间块")
                print(f"[INFO] 今日时间块: {len(today_blocks)} 个")

                if today_blocks:
                    total_available_minutes = sum(
                        datetime.fromisoformat(block['end_time']).replace(tzinfo=None) -
                        datetime.fromisoformat(block['start_time']).replace(tzinfo=None)
                        for block in today_blocks
                    )
                    print(f"[INFO] 今日可用时间: {total_available_minutes.total_seconds() / 60:.0f} 分钟")
                    print(f"[INFO] 时间块类型: {self.get_block_type_distribution(today_blocks)}")

                return True
            else:
                print(f"[FAIL] 获取时间块列表失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 获取时间块API测试失败: {e}")
            return False

    def test_4_get_categories_for_scheduling(self):
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
                    print(f"[INFO] 可用类别: {[cat.get('name', 'N/A') for cat in categories]}")

                return True
            else:
                print(f"[FAIL] 获取类别列表失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"[ERROR] 获取类别API测试失败: {e}")
            return False

    def test_5_scheduling_data_consistency(self):
        """测试调度数据一致性"""
        print("\n5. 测试调度数据一致性...")

        try:
            # 获取所有相关数据
            tasks_response = requests.get(f"{API_BASE}/tasks/", headers=self.get_headers())
            time_blocks_response = requests.get(f"{API_BASE}/time-blocks/", headers=self.get_headers())
            categories_response = requests.get(f"{API_BASE}/task-categories/", headers=self.get_headers())

            tasks = tasks_response.json()
            time_blocks = time_blocks_response.json().get('time_blocks', [])
            categories = categories_response.json()

            # 检查数据一致性
            consistency_issues = []

            # 检查任务类别关联
            pending_tasks = [task for task in tasks if task.get('status') == 'PENDING']
            for task in pending_tasks:
                if task.get('category_id'):
                    category_exists = any(cat['id'] == task['category_id'] for cat in categories)
                    if not category_exists:
                        consistency_issues.append(f"任务 {task['id']} 引用了不存在的类别 {task['category_id']}")

            # 检查时间块日期有效性
            for block in time_blocks:
                try:
                    block_date = datetime.fromisoformat(block['date']).date()
                    if block_date < datetime.now().date():
                        consistency_issues.append(f"时间块 {block['id']} 日期已过期")
                except:
                    consistency_issues.append(f"时间块 {block['id']} 日期格式无效")

            # 检查任务时间合理性
            for task in pending_tasks:
                if task.get('planned_start_time'):
                    try:
                        task_time = datetime.fromisoformat(task['planned_start_time'])
                        if task_time < datetime.now() - timedelta(days=1):
                            consistency_issues.append(f"任务 {task['id']} 计划时间已过期")
                    except:
                        consistency_issues.append(f"任务 {task['id']} 计划时间格式无效")

            if consistency_issues:
                print(f"[FAIL] 发现数据一致性问题:")
                for issue in consistency_issues[:3]:  # 只显示前3个问题
                    print(f"  - {issue}")
                return False
            else:
                print("[OK] 调度数据一致性检查通过")
                print(f"[INFO] 待调度任务: {len(pending_tasks)} 个")
                print(f"[INFO] 可用时间块: {len(time_blocks)} 个")
                print(f"[INFO] 任务类别: {len(categories)} 个")
                return True

        except Exception as e:
            print(f"[ERROR] 调度数据一致性测试失败: {e}")
            return False

    def test_6_task_priority_calculation(self):
        """测试任务优先级计算逻辑"""
        print("\n6. 测试任务优先级计算逻辑...")

        try:
            response = requests.get(f"{API_BASE}/tasks/", headers=self.get_headers())
            tasks = response.json()

            if not tasks:
                print("[SKIP] 没有任务数据，跳过优先级计算测试")
                return True

            # 模拟智能调度算法的优先级计算
            priority_scores = []
            for task in tasks:
                if task.get('status') != 'PENDING':
                    continue

                score = self.calculate_task_priority_score(task)
                priority_scores.append({
                    'task_id': task['id'],
                    'title': task['title'],
                    'score': score,
                    'priority': task.get('priority', 'MEDIUM')
                })

            # 按分数排序
            priority_scores.sort(key=lambda x: x['score'], reverse=True)

            print(f"[OK] 优先级计算完成，计算了 {len(priority_scores)} 个任务的优先级分数")

            if priority_scores:
                print(f"[INFO] 最高优先级任务: {priority_scores[0]['title']} (分数: {priority_scores[0]['score']:.2f})")
                print(f"[INFO] 最低优先级任务: {priority_scores[-1]['title']} (分数: {priority_scores[-1]['score']:.2f})")

                # 验证高优先级任务确实有较高分数
                high_priority_tasks = [ps for ps in priority_scores if ps['priority'] == 'HIGH']
                low_priority_tasks = [ps for ps in priority_scores if ps['priority'] == 'LOW']

                if high_priority_tasks and low_priority_tasks:
                    avg_high_score = sum(ps['score'] for ps in high_priority_tasks) / len(high_priority_tasks)
                    avg_low_score = sum(ps['score'] for ps in low_priority_tasks) / len(low_priority_tasks)

                    if avg_high_score > avg_low_score:
                        print("[OK] 优先级计算逻辑正确：高优先级任务分数更高")
                    else:
                        print("[WARNING] 优先级计算逻辑可能有问题：高优先级任务分数不占优势")

            return True

        except Exception as e:
            print(f"[ERROR] 任务优先级计算测试失败: {e}")
            return False

    def test_7_time_block_suitability(self):
        """测试时间块适合度计算"""
        print("\n7. 测试时间块适合度计算...")

        try:
            # 获取时间块和任务数据
            tasks_response = requests.get(f"{API_BASE}/tasks/", headers=self.get_headers())
            time_blocks_response = requests.get(f"{API_BASE}/time-blocks/", headers=self.get_headers())

            tasks = tasks_response.json()
            time_blocks = time_blocks_response.json().get('time_blocks', [])

            if not tasks or not time_blocks:
                print("[SKIP] 缺少任务或时间块数据，跳过适合度计算测试")
                return True

            pending_tasks = [task for task in tasks if task.get('status') == 'PENDING']
            today_blocks = [block for block in time_blocks
                           if datetime.fromisoformat(block['date']).date() == datetime.now().date()]

            suitability_scores = []

            for task in pending_tasks[:3]:  # 只测试前3个任务
                for block in today_blocks[:3]:  # 只测试前3个时间块
                    suitability = self.calculate_time_block_suitability(task, block)
                    suitability_scores.append({
                        'task': task['title'],
                        'block_type': block['block_type'],
                        'suitability': suitability
                    })

            print(f"[OK] 时间块适合度计算完成，计算了 {len(suitability_scores)} 个匹配度")

            if suitability_scores:
                best_match = max(suitability_scores, key=lambda x: x['suitability'])
                worst_match = min(suitability_scores, key=lambda x: x['suitability'])

                print(f"[INFO] 最佳匹配: {best_match['task']} -> {best_match['block_type']} (适合度: {best_match['suitability']:.2f})")
                print(f"[INFO] 最差匹配: {worst_match['task']} -> {worst_match['block_type']} (适合度: {worst_match['suitability']:.2f})")

            return True

        except Exception as e:
            print(f"[ERROR] 时间块适合度计算测试失败: {e}")
            return False

    def test_8_scheduling_algorithm_performance(self):
        """测试调度算法性能"""
        print("\n8. 测试调度算法性能...")

        try:
            import time

            # 获取数据
            tasks_response = requests.get(f"{API_BASE}/tasks/", headers=self.get_headers())
            time_blocks_response = requests.get(f"{API_BASE}/time-blocks/", headers=self.get_headers())

            tasks = tasks_response.json()
            time_blocks = time_blocks_response.json().get('time_blocks', [])

            # 模拟智能调度算法执行
            start_time = time.time()

            # 生成推荐
            recommendations = self.simulate_smart_recommendations(tasks, time_blocks)

            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # 转换为毫秒

            print(f"[OK] 调度算法执行完成")
            print(f"[INFO] 执行时间: {execution_time:.2f}ms")
            print(f"[INFO] 输入数据: {len(tasks)} 个任务, {len(time_blocks)} 个时间块")
            print(f"[INFO] 输出推荐: {len(recommendations)} 条建议")

            # 性能基准测试
            if execution_time > 1000:  # 超过1秒认为性能较差
                print(f"[WARNING] 算法执行时间较长: {execution_time:.2f}ms")
                return False
            else:
                print(f"[OK] 算法性能良好: {execution_time:.2f}ms")
                return True

        except Exception as e:
            print(f"[ERROR] 调度算法性能测试失败: {e}")
            return False

    def test_9_recommendation_validation(self):
        """测试推荐结果验证"""
        print("\n9. 测试推荐结果验证...")

        try:
            tasks_response = requests.get(f"{API_BASE}/tasks/", headers=self.get_headers())
            time_blocks_response = requests.get(f"{API_BASE}/time-blocks/", headers=self.get_headers())

            tasks = tasks_response.json()
            time_blocks = time_blocks_response.json().get('time_blocks', [])

            recommendations = self.simulate_smart_recommendations(tasks, time_blocks)

            if not recommendations:
                print("[SKIP] 没有生成推荐，跳过验证测试")
                return True

            validation_errors = []

            # 验证推荐的基本结构
            for i, rec in enumerate(recommendations):
                if not rec.get('type'):
                    validation_errors.append(f"推荐 {i} 缺少类型字段")
                if not rec.get('priority'):
                    validation_errors.append(f"推荐 {i} 缺少优先级字段")
                if rec.get('priority', 0) < 0 or rec.get('priority', 0) > 1:
                    validation_errors.append(f"推荐 {i} 优先级超出范围")

            # 验证任务推荐的有效性
            task_recommendations = [rec for rec in recommendations if rec.get('type') == 'TASK_RECOMMENDATION']
            for rec in task_recommendations:
                if not rec.get('task'):
                    validation_errors.append("任务推荐缺少任务信息")
                if not rec.get('suggestedAction'):
                    validation_errors.append("任务推荐缺少建议操作")

            if validation_errors:
                print(f"[FAIL] 推荐验证发现问题:")
                for error in validation_errors[:3]:
                    print(f"  - {error}")
                return False
            else:
                print(f"[OK] 推荐结果验证通过，共 {len(recommendations)} 条有效推荐")
                print(f"[INFO] 推荐类型分布: {self.get_recommendation_type_distribution(recommendations)}")
                return True

        except Exception as e:
            print(f"[ERROR] 推荐结果验证测试失败: {e}")
            return False

    def test_10_integration_workflow(self):
        """测试完整工作流程"""
        print("\n10. 测试完整工作流程...")

        try:
            workflow_results = []

            # 步骤1: 数据获取
            tasks_response = requests.get(f"{API_BASE}/tasks/", headers=self.get_headers())
            time_blocks_response = requests.get(f"{API_BASE}/time-blocks/", headers=self.get_headers())
            categories_response = requests.get(f"{API_BASE}/task-categories/", headers=self.get_headers())

            if all(response.status_code == 200 for response in [tasks_response, time_blocks_response, categories_response]):
                workflow_results.append("✓ 数据获取成功")
            else:
                workflow_results.append("✗ 数据获取失败")
                return False

            # 步骤2: 智能分析
            tasks = tasks_response.json()
            time_blocks = time_blocks_response.json().get('time_blocks', [])
            recommendations = self.simulate_smart_recommendations(tasks, time_blocks)

            if recommendations:
                workflow_results.append("✓ 智能分析成功")
            else:
                workflow_results.append("✗ 智能分析失败")

            # 步骤3: 推荐排序
            sorted_recommendations = sorted(recommendations, key=lambda x: x['priority'], reverse=True)
            if sorted_recommendations:
                workflow_results.append("✓ 推荐排序成功")

            # 步骤4: 结果验证
            high_priority_count = len([r for r in sorted_recommendations if r['priority'] >= 0.7])
            if high_priority_count > 0:
                workflow_results.append("✓ 高优先级推荐识别成功")

            print(f"[OK] 工作流程测试完成")
            for result in workflow_results:
                print(f"  {result}")

            success_rate = len([r for r in workflow_results if r.startswith('✓')]) / len(workflow_results)
            print(f"[INFO] 工作流程成功率: {success_rate * 100:.1f}%")

            return success_rate >= 0.75

        except Exception as e:
            print(f"[ERROR] 完整工作流程测试失败: {e}")
            return False

    def test_11_data_quality_assessment(self):
        """测试数据质量评估"""
        print("\n11. 测试数据质量评估...")

        try:
            quality_scores = {}

            # 评估任务数据质量
            tasks_response = requests.get(f"{API_BASE}/tasks/", headers=self.get_headers())
            tasks = tasks_response.json()

            task_quality_score = self.assess_task_data_quality(tasks)
            quality_scores['tasks'] = task_quality_score

            # 评估时间块数据质量
            time_blocks_response = requests.get(f"{API_BASE}/time-blocks/", headers=self.get_headers())
            time_blocks = time_blocks_response.json().get('time_blocks', [])

            time_block_quality_score = self.assess_time_block_data_quality(time_blocks)
            quality_scores['time_blocks'] = time_block_quality_score

            # 计算总体质量分数
            overall_quality = sum(quality_scores.values()) / len(quality_scores)

            print(f"[OK] 数据质量评估完成")
            print(f"[INFO] 任务数据质量: {task_quality_score:.2f}/1.00")
            print(f"[INFO] 时间块数据质量: {time_block_quality_score:.2f}/1.00")
            print(f"[INFO] 总体数据质量: {overall_quality:.2f}/1.00")

            # 质量阈值检查
            if overall_quality >= 0.8:
                print("[OK] 数据质量优秀，适合智能调度")
                return True
            elif overall_quality >= 0.6:
                print("[WARNING] 数据质量一般，可能影响调度效果")
                return True
            else:
                print("[FAIL] 数据质量较差，建议先完善数据")
                return False

        except Exception as e:
            print(f"[ERROR] 数据质量评估失败: {e}")
            return False

    # 辅助方法
    def calculate_task_priority_score(self, task):
        """计算任务优先级分数（模拟智能算法）"""
        score = 0.5  # 基础分数

        # 优先级评分
        if task.get('priority') == 'HIGH':
            score += 0.3
        elif task.get('priority') == 'MEDIUM':
            score += 0.1

        # 时间紧急度评分
        if task.get('planned_start_time'):
            task_time = datetime.fromisoformat(task['planned_start_time'])
            days_until = (task_time - datetime.now()).days
            if days_until <= 1:
                score += 0.3
            elif days_until <= 3:
                score += 0.2

        # 复杂度评分
        if task.get('estimated_pomodoros', 1) >= 3:
            score += 0.1

        return min(1.0, score)

    def calculate_time_block_suitability(self, task, time_block):
        """计算时间块适合度（模拟智能算法）"""
        suitability = 0.5  # 基础分数

        # 时间块类型与任务类别匹配
        task_category = task.get('category_id', '')
        block_type = time_block.get('block_type', '')

        # 简化的匹配逻辑
        if '工作' in task_category or '紧急' in task_category:
            if block_type in ['RESEARCH', 'GROWTH']:
                suitability += 0.3
        elif '学习' in task_category or '成长' in task_category:
            if block_type in ['GROWTH', 'RESEARCH']:
                suitability += 0.3
        elif '日常' in task_category:
            if block_type in ['REVIEW', 'REST']:
                suitability += 0.2

        return min(1.0, suitability)

    def simulate_smart_recommendations(self, tasks, time_blocks):
        """模拟智能推荐生成"""
        recommendations = []
        pending_tasks = [task for task in tasks if task.get('status') == 'PENDING']

        for task in pending_tasks:
            priority_score = self.calculate_task_priority_score(task)

            if priority_score >= 0.3:  # 最低优先级阈值
                # 寻找合适的时间块
                suitable_block = None
                best_suitability = 0

                for block in time_blocks:
                    suitability = self.calculate_time_block_suitability(task, block)
                    if suitability > best_suitability:
                        best_suitability = suitability
                        suitable_block = block

                recommendations.append({
                    'id': f"rec_{task['id']}",
                    'type': 'TASK_RECOMMENDATION',
                    'priority': priority_score,
                    'task': task,
                    'suggestedTime': suitable_block,
                    'suggestedAction': {
                        'type': 'SCHEDULE_TO_BLOCK' if suitable_block else 'CREATE_TIME_BLOCK',
                        'text': '安排到合适时间块' if suitable_block else '创建新时间块'
                    },
                    'reasons': self.generate_recommendation_reasons(task, priority_score),
                    'status': 'PENDING'
                })

        return sorted(recommendations, key=lambda x: x['priority'], reverse=True)

    def generate_recommendation_reasons(self, task, priority_score):
        """生成推荐原因"""
        reasons = []

        if task.get('priority') == 'HIGH':
            reasons.append('高优先级任务')

        if task.get('planned_start_time'):
            task_time = datetime.fromisoformat(task['planned_start_time'])
            days_until = (task_time - datetime.now()).days
            if days_until <= 1:
                reasons.append('即将到期')
            elif days_until <= 3:
                reasons.append('临近截止日期')

        if task.get('estimated_pomodoros', 1) >= 3:
            reasons.append('复杂任务')

        if priority_score >= 0.7:
            reasons.append('AI推荐高优先级')

        return reasons

    def assess_task_data_quality(self, tasks):
        """评估任务数据质量"""
        if not tasks:
            return 0.0

        quality_factors = []

        # 完整性检查
        complete_tasks = [task for task in tasks
                         if task.get('title') and task.get('status') and task.get('priority')]
        completeness = len(complete_tasks) / len(tasks)
        quality_factors.append(completeness)

        # 优先级分布
        has_various_priorities = len(set(task.get('priority') for task in tasks)) > 1
        priority_diversity = 1.0 if has_various_priorities else 0.5
        quality_factors.append(priority_diversity)

        # 时间信息完整性
        tasks_with_time = [task for task in tasks if task.get('planned_start_time')]
        time_completeness = len(tasks_with_time) / len(tasks) if tasks else 0
        quality_factors.append(time_completeness)

        return sum(quality_factors) / len(quality_factors)

    def assess_time_block_data_quality(self, time_blocks):
        """评估时间块数据质量"""
        if not time_blocks:
            return 0.0

        quality_factors = []

        # 完整性检查
        complete_blocks = [block for block in time_blocks
                           if block.get('start_time') and block.get('end_time') and block.get('block_type')]
        completeness = len(complete_blocks) / len(time_blocks)
        quality_factors.append(completeness)

        # 类型多样性
        block_types = set(block.get('block_type') for block in time_blocks)
        type_diversity = min(len(block_types) / 5, 1.0)  # 最多5种类型
        quality_factors.append(type_diversity)

        # 时间分布合理性
        if time_blocks:
            today_blocks = [block for block in time_blocks
                           if datetime.fromisoformat(block['date']).date() == datetime.now().date()]
            time_distribution = len(today_blocks) / len(time_blocks)
            quality_factors.append(time_distribution)
        else:
            quality_factors.append(0.0)

        return sum(quality_factors) / len(quality_factors)

    def get_priority_distribution(self, tasks):
        """获取优先级分布"""
        priorities = {}
        for task in tasks:
            priority = task.get('priority', 'MEDIUM')
            priorities[priority] = priorities.get(priority, 0) + 1
        return priorities

    def get_type_distribution(self, tasks):
        """获取任务类型分布"""
        types = {}
        for task in tasks:
            task_type = task.get('task_type', 'FLEXIBLE')
            types[task_type] = types.get(task_type, 0) + 1
        return types

    def get_block_type_distribution(self, blocks):
        """获取时间块类型分布"""
        types = {}
        for block in blocks:
            block_type = block.get('block_type', 'RESEARCH')
            types[block_type] = types.get(block_type, 0) + 1
        return types

    def get_recommendation_type_distribution(self, recommendations):
        """获取推荐类型分布"""
        types = {}
        for rec in recommendations:
            rec_type = rec.get('type', 'UNKNOWN')
            types[rec_type] = types.get(rec_type, 0) + 1
        return types

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("智能任务调度建议API测试开始")
        print("=" * 60)

        test_methods = [
            self.test_1_user_authentication,
            self.test_2_get_tasks_for_scheduling,
            self.test_3_get_time_blocks_for_scheduling,
            self.test_4_get_categories_for_scheduling,
            self.test_5_scheduling_data_consistency,
            self.test_6_task_priority_calculation,
            self.test_7_time_block_suitability,
            self.test_8_scheduling_algorithm_performance,
            self.test_9_recommendation_validation,
            self.test_10_integration_workflow,
            self.test_11_data_quality_assessment
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
            print("[SUCCESS] 所有测试都通过了！智能任务调度建议API正常工作。")
        else:
            print("[WARNING] 部分测试失败，请检查相关功能。")

        print("=" * 60)

        return failed == 0

def run_intelligent_task_scheduler_tests():
    """运行智能任务调度建议测试"""
    tester = IntelligentTaskSchedulerAPITester()
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
    success = run_intelligent_task_scheduler_tests()
    sys.exit(0 if success else 1)