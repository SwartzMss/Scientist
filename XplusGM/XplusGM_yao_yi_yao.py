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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\XplusGM_yaoyiyao_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')



class XplusGM:
    def __init__(self, app_package, app_activity):
        self.device_name = None
        self.alias = None
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


    def yaoyiyao_ldplayer(self, counts=50):
        time.sleep(3)
        log_and_print("yaoyiyao_ldplayer start..")
        command = f'"E:\\leidian\\LDPlayer9\\dnconsole.exe" action --name "{self.alias}" --key call.shake --value null'
        processes = []
        for i in range(counts):
            log_and_print(f"yaoyiyao_ldplayer count {i}..")
            try:
                process = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
                processes.append(process)
            except Exception as e:
                log_and_print(f"Error starting process: {e}")

        # 等待所有进程完成
        for process in processes:
            process.wait()
        for process in processes:
            _, stderr = process.communicate()
            if stderr:
                log_and_print(f"Process error: {stderr.decode()}")

        log_and_print("yaoyiyao_ldplayer down..")

    def close_ldplayer(self):
        """关闭指定索引号的雷电模拟器实例"""
        command = f'"E:\\leidian\\LDPlayer9\\dnconsole.exe" quit --index {self.index}'
        subprocess.Popen(command, shell=True)
        log_and_print(f"Closing LDPlayer username={self.alias}...")

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

    def connect_to_appium(self, retry_limit=3, retry_delay=5):
        """连接到Appium服务并启动应用，带重试逻辑"""
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
        
        attempts = 0
        while attempts < retry_limit:
            try:
                self.driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_caps)
                log_and_print("Connected to Appium.")
                return  # 成功连接后退出函数
            except WebDriverException as e:
                log_and_print(f"Attempt {attempts + 1} failed to connect to Appium: {e}")
                attempts += 1
                time.sleep(retry_delay)
        
        raise Exception("Failed to connect to Appium after multiple attempts.")


    def find_and_click_element(self, xpath, timeout=5):
        """查找元素并点击"""
        try:
            time.sleep(3)
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            element.click()
            return True
        except WebDriverException  as e:
            log_and_print(f"find_and_click_element failed {e}")
            return False

    def find_element(self, xpath, timeout=5):
        """查找元素并点击"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except WebDriverException  as e:
            return False

    def quit(self):
        """退出驱动和关闭模拟器"""
        if self.driver:
            self.driver.quit()
            log_and_print("Appium session ended.")
        self.driver = None

    def run(self, alias, index, device_name):
        self.device_name = device_name
        self.alias = alias
        self.index = index
        error_occurred = False

        try:
            try:
                self.start_ldplayer()
                log_and_print(f"{alias} firstly start_ldplayer successfully")
            except Exception as e:
                log_and_print(f"{alias} firstly start_ldplayer failed: {e}")
                sys.exit()

            try:
                self.wait_for_emulator()
                log_and_print(f"{alias} firstly wait_for_emulator successfully")
            except Exception as e:
                log_and_print(f"{alias} firstly wait_for_emulator failed: {e}")
                sys.exit()

            countNum = 0
            while(1):
                log_and_print(f"{alias} countNum = {countNum}")
                countNum = countNum +1
                if countNum >= 120:
                    break
                try:
                    self.connect_to_appium()
                    log_and_print(f"{alias} connect_to_appium successfully")
                    error_occurred = False
                except Exception as e:
                    log_and_print(f"{alias} connect_to_appium failed: {e}")
                    error_occurred = True

                time.sleep(8) # 这边耗时会等待最开始的加载
                # if not error_occurred:
                #     if self.find_and_click_element('//android.view.View[@text="自動挖礦"]') == True:
                #         log_and_print(f"switch page to start successfully: {self.alias}")
                #     else:
                #         log_and_print(f"switch page  to start failed: {self.alias}")
                #         error_occurred = True

                if not error_occurred:
                    if self.find_and_click_element('//android.view.View[@text="遊戲"]') == True:	
                        log_and_print(f"小程式 clicked succeed: {self.alias}")
                    else:
                        log_and_print(f"小程式 clicked failed: {self.alias}")
                        error_occurred = True
                if not error_occurred:
                    if self.find_and_click_element('//android.view.View[@resource-id="app"]/android.view.View[1]/android.view.View[2]/android.view.View/android.view.View[8]') == True:	
                        log_and_print(f"game clicked succeed: {self.alias}")
                    else:
                        log_and_print(f"game clicked failed: {self.alias}")
                        error_occurred = True  
        

                if not error_occurred:
                    if self.find_and_click_element('//android.view.View[@text="立刻搖一搖"]') == True:	
                        log_and_print(f"立刻搖一搖 clicked succeed: {self.alias}")
                    else:
                        log_and_print(f"立刻搖一搖 clicked failed: {self.alias}")
                        error_occurred = True  
                time.sleep(5)    
                if not error_occurred:
                    self.yaoyiyao_ldplayer()
                self.quit()
                log_and_print(f" self.quit done: {self.alias}")
                time.sleep(3)
        finally:
            if error_occurred:
                self.close_ldplayer()
                return False
            self.cleanup_resources()
            return True

    def cleanup_resources(self):
        time.sleep(3)  # 等待一些操作完成
        self.quit()
        time.sleep(1)
        self.close_ldplayer()
        time.sleep(1)

# 使用示例
if __name__ == "__main__":
    app = XplusGM( "com.xplus.wallet", ".MainActivity")
    for i in range(4):
        log_and_print(f"################: {i}次启动")
        #app.run("swartz", 30,"emulator-5614")
        #app.run("JP07", 27,"emulator-5608")
        #app.run("JP08", 28,"emulator-5610")
        app.run("JP09", 29,"emulator-5612")
        #app.run("JP06", 26,"emulator-5606")
        #smd 01 02 sbm sme
        #app.run("MSS", 2,"emulator-5558")
        #app.run("SME1102", 1,"emulator-5556")
        #app.run("SMD01", 6,"emulator-5566")
        #app.run("SMD02", 7,"emulator-5568")
        #app.run("SBM", 4,"emulator-5562")
        time.sleep(3)
