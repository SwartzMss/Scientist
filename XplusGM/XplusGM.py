from appium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import subprocess
import time
import sys
import os
import datetime
# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# 现在可以从tools目录导入UserInfo
from tools.UserInfo import UserInfo

# 现在可以从tools目录导入excelWorker
from tools.excelWorker import excelWorker

# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\XplusGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a') as log_file:
        print(message)
        log_file.write(message + '\n')



class XplusGM:
    def __init__(self, app_package, app_activity):
        self.device_name = None
        self.username = None
        self.index = 100
        self.app_package = app_package
        self.app_activity = app_activity
        self.driver = None

    def start_ldplayer(self):
        self.close_ldplayer()
        time.sleep(2)
        """启动指定索引号的雷电模拟器实例"""
        command = f'"E:\\leidian\\LDPlayer9\\dnplayer.exe" index={self.index}'
        subprocess.Popen(command, shell=True)

    def close_ldplayer(self):
        """关闭指定索引号的雷电模拟器实例"""
        command = f'"E:\\leidian\\LDPlayer9\\dnconsole.exe" quit --index {self.index}'
        subprocess.Popen(command, shell=True)
        log_and_print(f"Closing LDPlayer username={self.username}...")

    def is_emulator_ready(self, emulator_name):
        """检查模拟器是否准备就绪"""
        result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE, text=True)
        return emulator_name in result.stdout

    def wait_for_emulator(self, timeout=120):
        """等待模拟器启动并就绪"""
        start_time = time.time()
        while not self.is_emulator_ready(self.device_name):
            if (time.time() - start_time) > timeout:
                raise TimeoutError("Timeout waiting for emulator to be ready.")
            log_and_print("Waiting for emulator to be ready...")
            time.sleep(5)
        log_and_print("Emulator is ready.")

    def connect_to_appium(self):
        """连接到Appium服务并启动应用"""
        desired_caps = {
            'platformName': 'Android',
            'platformVersion': '9',
            'noReset': True,
            'deviceName': self.device_name,
            'appPackage': self.app_package,
            'appActivity': self.app_activity,
            'automationName': 'UiAutomator2',
            'newCommandTimeout': 6000,
        }
        self.driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_caps)
        log_and_print("Connected to Appium.")

    def find_and_click_element(self, xpath, timeout=5):
        """查找元素并点击"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            element.click()
            return True
        except WebDriverException  as e:
            return False

    def quit(self):
        """退出驱动和关闭模拟器"""
        if self.driver:
            self.driver.quit()
            log_and_print("Appium session ended.")

    def run(self, username, index, device_name):
        self.device_name = device_name
        self.username = username
        self.index = index
        error_occurred = False

        try:
            try:
                self.start_ldplayer()
                log_and_print(f"{username} start_ldplayer successfully")
            except Exception as e:
                log_and_print(f"{username} start_ldplayer failed: {e}")
                error_occurred = True

            if not error_occurred:
                try:
                    self.wait_for_emulator()
                    log_and_print(f"{username} wait_for_emulator successfully")
                except Exception as e:
                    log_and_print(f"{username} wait_for_emulator failed: {e}")
                    error_occurred = True

            if not error_occurred:
                try:
                    self.connect_to_appium()
                    log_and_print(f"{username} connect_to_appium successfully")
                except Exception as e:
                    log_and_print(f"{username} connect_to_appium failed: {e}")
                    error_occurred = True

            if self.find_and_click_element('//android.widget.Button[@text="領取"]') == True:
                self.find_and_click_element('//android.widget.Image[@text="17EZJMxGT442BvgHrTnaL9xn22vlf1U8xA6wjaEq2oFqOWbOsBwZg7QYwCw8bCIAzQ6SGSQACABQAKABAABQPARXepnFZhDV3JOXwVyCVVktUGNUivVbH2HFxIWEt2bwZqlAAAAAElFTkSuQmCC"]')
                if self.find_and_click_element('//android.widget.Button[@text="開啟挖礦"]') == True:
                    log_and_print(f"recheck successfully: {self.username}")
                    excel_manager.update_info(self.username, "recheck successfully")
            else:
                log_and_print(f"not need sign rightb now: {self.username}")
                excel_manager.update_info(self.username, "not need sign rightb now")
        finally:
            # Regardless of what happened above, try to clean up.
            self.cleanup_resources(username, error_occurred)

    def cleanup_resources(self, username, error_occurred):
        time.sleep(3)  # 等待一些操作完成
        self.quit()
        time.sleep(1)
        self.close_ldplayer()
        time.sleep(1)

# 使用示例
if __name__ == "__main__":

    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("XplusGM", log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_app("AZC", "XplusGM")
    app = XplusGM( "com.xplus.wallet", ".MainActivity")
    failed_list = []
    for credentials in credentials_list:
        username = credentials["username"]
        index = credentials["index"]
        devid = credentials["devid"]
        if(app.run(username, index,devid) == False):
            failed_list.append((username))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for username in failed_list:
        log_and_print(f"final failed username = {username}")
    excel_manager.save_msg_and_stop_service()  
