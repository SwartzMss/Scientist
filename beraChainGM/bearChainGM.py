from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
from eth_account.messages import encode_defunct
import web3
import sys
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
from tools.switchProxy import ClashAPIManager
# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\bearChainGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')

class bearChainGM:
    def __init__(self):
        #self.user_data_dir_path = user_data_dir_path
        self.driver = None

    def initialize_driver(self):
        """初始化 WebDriver。"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        #chrome_options.add_argument(f"--user-data-dir={self.user_data_dir_path}")
        return webdriver.Chrome(options=chrome_options)

    def login(self, url="https://artio.faucet.berachain.com/"):
        """登录指定的网址。"""
        self.driver = self.initialize_driver()
        time.sleep(5)
        self.driver.get(url)
        time.sleep(3)




    def run(self, userName, address):
        try:
            # 尝试登录
            try:
                self.login()    
                log_and_print(f"{userName} login succeed.")
            except WebDriverException as e:
                log_and_print(f"{userName} login failed : {e}")
                return False

            # 各步骤尝试操作，增加日志记录
            try:
                button = self.driver.find_element(By.XPATH, "//*[@id='terms']")
                button.click()
                log_and_print(f"{userName} Terms button clicked.")
                time.sleep(3)
            except NoSuchElementException:
                log_and_print(f"{userName} Terms button not found.")
                return False

            try:
                button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'I AGREE')]")
                button.click()
                log_and_print(f"{userName} I AGREE' button clicked.")
                time.sleep(3)
            except NoSuchElementException:
                log_and_print(f"{userName} I AGREE' button not found.")
                return False

            try:
                input_element = self.driver.find_element(By.XPATH, "//div[@class='relative w-full']/input")
                input_element.send_keys(address)
                log_and_print(f"{userName} Address input successful.")
                time.sleep(3)
            except NoSuchElementException:
                log_and_print(f"{userName} Address input field not found.")
                return False

            try:
                button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Click here to prove you are not a bot')]")
                button.click()
                log_and_print(f"{userName} 'Prove not a bot' button clicked.")
                time.sleep(3)
            except NoSuchElementException:
                log_and_print(f"{userName} 'Prove not a bot' button not found.")
                return False

            try:
                button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Drip Tokens')]")
                button.click()
                log_and_print(f"{userName} 'Drip Tokens' button clicked.")
                time.sleep(5)
            except NoSuchElementException:
                log_and_print(f"{userName} 'Drip Tokens' button not found.")
                return False

            try:
                grey_listed_elements = self.driver.find_elements(By.XPATH, "//h5[contains(text(), 'Grey-listed for 8 hours')]")
                submitted_elements = self.driver.find_elements(By.XPATH, "//h5[contains(text(), 'Request Submitted')]")
                if grey_listed_elements:
                    log_and_print(f"{userName} Operation failed: Grey-listed for 8 hours.")
                    excel_manager.update_info(username, "Operation failed: Grey-listed for 8 hours")
                elif submitted_elements:
                    log_and_print(f"{userName} Operation successful: Request Submitted.")
                    excel_manager.update_info(username, "Operation successful: Request Submitted.")
                else:
                    log_and_print(f"{userName} Status unknown.")
                    excel_manager.update_info(username, "Operation failed: Status unknown.")

            except WebDriverException:
                log_and_print(f"{userName}Error checking operation status.")
                return False

        finally:
            self.driver.quit()
            time.sleep(3)

    def logout(self):
        """退出并关闭浏览器。"""
        self.driver.quit()

if __name__ == "__main__":
    app = bearChainGM()
    proxyApp = ClashAPIManager(logger = log_and_print)
    failed_list = []
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("bearChainGM", log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_interact("eth", "bearChainGM")

    for credentials in credentials_list:
        username = credentials["username"]
        access_token = credentials["access_token"]
        proxyName = UserInfoApp.find_proxy_by_alias_in_file(username)
        if proxyName== None:
            log_and_print(f"cannot find proxy username = {username}")
            continue
        proxyApp.change_proxy(proxyName)
        time.sleep(5)
        address = web3.Account.from_key(access_token).address    
        if(app.run(username, address) == False):
            failed_list.append((username))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for username, failed_list in failed_list:
        log_and_print(f"final failed username = {username}")
        excel_manager.update_info(username, "sign failed")
    excel_manager.save_msg_and_stop_service()