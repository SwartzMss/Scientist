import sys
from eth_account.messages import encode_defunct
import time
import math
import sys
import web3
import requests
import random
from datetime import datetime
import json
import os

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
current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\darenGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a') as log_file:
        print(message)
        log_file.write(message + '\n')


class darenGM:
    def __init__(self):
        self.alias = None
        self.account = None
        self.nonce = None
        self.signature = None
        self.headers = {
            'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 116)}.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

    def getNonce(self):
        url = f"https://api.daren.market/v2/auth/web3/message?address={self.account.address}"
        log_and_print(f"address:{self.account.address}")
        response = session.get(
            url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"response:{data}")
        return data

    def extract_nonce(self, json_data):
        # 将消息字符串分割成多行
        message_lines = json_data["message"].split('\n')
        # 在包含"Nonce:"的行中查找Nonce值
        nonce_line = [line for line in message_lines if "Nonce:" in line][0]
        # 分割找到的行以提取Nonce值
        nonce_value = nonce_line.split(': ')[1]
        return nonce_value

    def signMessage(self):
        # 获取当前时间并转换为ISO 8601格式的字符串
        msg = (
                "Welcome to Daren!\n\n"
                "Click to sign in and accept the Daren Terms of Service: https://daren.market/tos\n\n"
                "This request will not trigger a blockchain transaction or cost any gas fees.\n\n"
                f"Wallet address: {self.account.address}\n"
                f"Nonce: {self.nonce}\n"
            )
        res = self.account.sign_message(encode_defunct(text=msg))
        return res.signature.hex()


    def postUsers(self):
        url = "https://api.daren.market/v2/auth/web3/users"
        message = (
            "Welcome to Daren!\n\n"
            "Click to sign in and accept the Daren Terms of Service: https://daren.market/tos\n\n"
            "This request will not trigger a blockchain transaction or cost any gas fees.\n\n"
            f"Wallet address: {self.account.address}\n"
            f"Nonce: {self.nonce}\n"
        )
        data={
            "address": self.account.address,
            "message": message,
            "signature": self.signature,
            "type": "NORMAL"
        }
        response = session.post(
            url, headers=self.headers,json=data, timeout=10)
        data = response.json()
        log_and_print(f"response:{data}")
        return data


    def checkin(self):
        url = f"https://api.daren.market/v2/tasks/+/DAILY_CHECK_IN/claim"
        response = session.post(
            url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"response:{data}")
        return data

    def checkResult(self):
        url = f"https://api.daren.market/v2/points/"
        response = session.get(
            url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"response:{data}")
        return data

    def run(self,alias, account):
        self.alias = alias
        self.account = account
        try:
            response = self.getNonce()
            self.nonce = self.extract_nonce(response)
            log_and_print(f"{alias} getNonce successfully ")
        except Exception as e:
            log_and_print(f"{alias} getNonce failed: {e}")
            return False

        try:
            self.signature = self.signMessage()
            log_and_print(f"{alias} signMessage successfully ")
        except Exception as e:
            log_and_print(f"{alias} signMessage failed: {e}")
            return False    

        try:
            response = self.postUsers()
            token = response['user']['token']
            self.headers['authorization'] =  token
            log_and_print(f"{alias} postUsers successfully ")
        except Exception as e:
            log_and_print(f"{alias} postUsers failed: {e}")
            return False  
 
        try:
            response = self.checkin()
            if response["success"] != True and 'Task has been claimed' not in response["message"]:
                raise Exception(f"checkin Error: {response}")
            response = self.checkResult()
            if response["success"] != True:
                raise Exception(f"checkResult Error: {response}")
            points = response["points"]
            log_and_print(f"{alias} checkin successfully points = {points}")
            excel_manager.update_info(alias, f"checkin successfully points = {points}")
        except Exception as e:
            log_and_print(f"{alias} checkin failed: {e}")
            return False      


if __name__ == '__main__':
    proxy_list = ['http://127.0.0.1:7890']
    proxies = {'http': random.choice(proxy_list),
               'https': random.choice(proxy_list)}
    session = requests.Session()
    session.proxies = proxies
    app = darenGM()

    failed_list = []
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("darenGM", log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_eth("darenGM")
    for credentials in credentials_list:
        alias = credentials["alias"]
        key = credentials["key"]

        account = web3.Account.from_key(key)    
        if(app.run(alias, account) == False):
            failed_list.append((alias, account))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for alias, account in failed_list:
        log_and_print(f"final failed username = {alias}")
    excel_manager.save_msg_and_stop_service()