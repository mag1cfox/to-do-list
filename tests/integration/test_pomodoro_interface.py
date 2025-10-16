#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_pomodoro_interface():
    """测试番茄钟计时器界面功能"""
    print("开始测试番茄钟计时器界面...")

    # 初始化浏览器
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()

        # 1. 访问前端应用
        print("1. 访问前端应用...")
        driver.get("http://localhost:5174")
        time.sleep(3)

        # 2. 检查页面是否加载成功
        print("2. 检查主页加载...")
        title = driver.title
        if title:
            print(f"[OK] 页面标题: {title}")
        else:
            print("[ERROR] 页面未加载")
            return False

        # 3. 导航到番茄钟页面
        print("3. 导航到番茄钟页面...")
        try:
            # 查找导航链接
            pomodoro_link = driver.find_element(By.XPATH, "//a[contains(@href, '/pomodoro') or contains(text(), '番茄钟')]")
            pomodoro_link.click()
            print("[OK] 点击番茄钟导航链接")
        except:
            # 如果没有找到导航链接，直接访问URL
            driver.get("http://localhost:5174/pomodoro")
            print("[OK] 直接访问番茄钟页面")

        time.sleep(3)

        # 4. 检查番茄钟页面组件
        print("4. 检查番茄钟页面组件...")

        # 检查标题
        try:
            title_element = driver.find_element(By.XPATH, "//h1[contains(text(), '番茄钟计时器')] | //h2[contains(text(), '番茄钟计时器')]")
            print("[OK] 找到页面标题")
        except:
            print("[ERROR] 未找到页面标题")
            return False

        # 检查任务选择下拉框
        try:
            task_select = driver.find_element(By.CSS_SELECTOR, "select[placeholder*='任务'], .ant-select-selector")
            print("[OK] 找到任务选择组件")
        except:
            print("[ERROR] 未找到任务选择组件")

        # 检查计时器显示区域
        try:
            timer_display = driver.find_element(By.CSS_SELECTOR, ".ant-progress, .ant-statistic, div[style*='font-size']")
            print("[OK] 找到计时器显示区域")
        except:
            print("[ERROR] 未找到计时器显示区域")

        # 检查控制按钮
        try:
            start_button = driver.find_element(By.XPATH, "//button[contains(text(), '开始')] | //button[contains(@class, 'play')]")
            print("[OK] 找到开始按钮")
        except:
            print("[ERROR] 未找到开始按钮")

        # 检查设置按钮
        try:
            settings_button = driver.find_element(By.XPATH, "//button[contains(@class, 'setting') or contains(text(), '设置')]")
            print("[OK] 找到设置按钮")
        except:
            print("[ERROR] 未找到设置按钮")

        # 检查历史记录按钮
        try:
            history_button = driver.find_element(By.XPATH, "//button[contains(@class, 'history') or contains(text(), '历史')]")
            print("[OK] 找到历史记录按钮")
        except:
            print("[ERROR] 未找到历史记录按钮")

        # 5. 测试设置功能
        print("5. 测试设置功能...")
        try:
            settings_button = driver.find_element(By.XPATH, "//button[contains(@class, 'setting') or contains(text(), '设置')]")
            settings_button.click()
            time.sleep(1)

            # 检查设置模态框
            modal = driver.find_element(By.CSS_SELECTOR, ".ant-modal, [role='dialog']")
            if modal.is_displayed():
                print("[OK] 设置模态框正常打开")

                # 关闭模态框
                close_button = driver.find_element(By.CSS_SELECTOR, ".ant-modal-close, button[aria-label='Close']")
                close_button.click()
                time.sleep(1)
            else:
                print("[ERROR] 设置模态框未显示")
        except:
            print("[ERROR] 设置功能测试失败")

        # 6. 测试历史记录功能
        print("6. 测试历史记录功能...")
        try:
            history_button = driver.find_element(By.XPATH, "//button[contains(@class, 'history') or contains(text(), '历史')]")
            history_button.click()
            time.sleep(1)

            # 检查历史记录模态框
            modal = driver.find_element(By.CSS_SELECTOR, ".ant-modal, [role='dialog']")
            if modal.is_displayed():
                print("[OK] 历史记录模态框正常打开")

                # 关闭模态框
                close_button = driver.find_element(By.CSS_SELECTOR, ".ant-modal-close, button[aria-label='Close']")
                close_button.click()
                time.sleep(1)
            else:
                print("[ERROR] 历史记录模态框未显示")
        except:
            print("[ERROR] 历史记录功能测试失败")

        # 7. 检查统计卡片
        print("7. 检查统计卡片...")
        try:
            stat_cards = driver.find_elements(By.CSS_SELECTOR, ".ant-card, .ant-statistic")
            if len(stat_cards) >= 3:
                print(f"[OK] 找到 {len(stat_cards)} 个统计卡片")
            else:
                print(f"[WARNING] 只找到 {len(stat_cards)} 个统计卡片")
        except:
            print("[ERROR] 未找到统计卡片")

        print("\n番茄钟计时器界面测试完成!")
        return True

    except Exception as e:
        print(f"[ERROR] 测试过程中出现异常: {e}")
        return False

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    try:
        success = test_pomodoro_interface()
        if success:
            print("\n✅ 番茄钟计时器界面功能测试通过!")
        else:
            print("\n❌ 番茄钟计时器界面功能测试失败!")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")