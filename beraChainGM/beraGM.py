import time
import os
from eth_account.messages import encode_defunct
import web3
import random
import sys
import datetime
import requests

# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# 现在可以从tools目录导入UserInfo
from tools.UserInfo import UserInfo
from tools.YesCaptchaClient import YesCaptchaClient
# 现在可以从tools目录导入excelWorker
from tools.excelWorker import excelWorker
from tools.switchProxy import ClashAPIManager
# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\bearGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')

class bearGM:
    def __init__(self):
        self.headers = {
            'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 116)}.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/plain;charset=UTF-8',
            'referer': 'https://artio.faucet.berachain.com/',
            'origin': 'https://artio.faucet.berachain.com', 
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.session = None

    def create_new_session(self):
        self.session = requests.Session()

    def claimAddressCode(self, address):
        form_data = {'address': address}
        url = f"https://artio-80085-faucet-api-cf.berachain.com/api/claim"
        response = self.session.post(url,json=form_data, headers=self.headers, timeout=60)
        data = response.json()
        log_and_print(f"response:{response}")
        return data

    def run(self, alias, key):
        self.create_new_session()
        website_url = 'https://artio.faucet.berachain.com'
        website_key = '0x4AAAAAAARdAuciFArKhVwt'
        task_type = 'TurnstileTaskProxyless'

        address = web3.Account.from_key(key).address 
        captcha_client = YesCaptchaClient(logger = log_and_print)
        try:
            recaptcha_token = captcha_client.get_recaptcha_token(website_url, website_key, task_type)
            self.headers['authorization'] = 'Bearer ' + recaptcha_token

        except Exception as e:
            log_and_print(f"get_recaptcha_token Error: {e}")
            excel_manager.update_info(alias,  f"Error {e}")
            return False

        response = self.claimAddressCode(address)
        log_and_print(f"{alias}: {response}")
        excel_manager.update_info(alias,  f"{response}")
        return True


if __name__ == "__main__":
    app = bearGM()
    proxyApp = ClashAPIManager(logger = log_and_print)
    failed_list = []
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("bearGM", log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_eth("bearGM")

    for credentials in credentials_list:
        alias = credentials["alias"]
        key = credentials["key"]
        proxyName = UserInfoApp.find_proxy_by_alias_in_file(alias)
        if proxyName== None:
            log_and_print(f"cannot find proxy username = {alias}")
            continue
        proxyApp.change_proxy(proxyName)
        time.sleep(5)   
        if(app.run(alias, key) == False):
            failed_list.append(alias)

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for alias in failed_list:
        log_and_print(f"final failed username = {alias}")
    excel_manager.save_msg_and_stop_service()
    proxyApp.change_proxy("🇭🇰 HK | 香港 01")