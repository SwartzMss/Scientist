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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\ReikiSign_{current_time}.log'


def log_message(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a') as log_file:
        print(message)
        log_file.write(message + '\n')




class ReikiSign:
    def __init__(self):
        self.userName = None
        self.account = None
        self.nonce = None
        self.signature = None
        self.iso_date_string = None
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
        url = "https://reiki.web3go.xyz/api/account/web3/web3_nonce"
        data={
            "address": self.account.address
        }
        log_and_print(f"address:{self.account.address}")
        response = session.post(
            url, headers=self.headers,json=data, timeout=60)
        data = response.json()
        #log_and_print(f"response:{data}")
        return data

    def signMessage(self):
        # 获取当前时间并转换为ISO 8601格式的字符串
        self.iso_date_string = datetime.utcnow().isoformat() + "Z"
        msg = f"reiki.web3go.xyz wants you to sign in with your Ethereum account:\n{self.account.address}\n\n{self.nonce}\n\nURI: https://reiki.web3go.xyz\nVersion: 1\nChain ID: 56\nNonce: {self.nonce}\nIssued At: {self.iso_date_string}"
        res = self.account.sign_message(encode_defunct(text=msg))
        return res.signature.hex()


    def postChallenge(self):
        url = "https://reiki.web3go.xyz/api/account/web3/web3_challenge"
        msg = f"reiki.web3go.xyz wants you to sign in with your Ethereum account:\n{self.account.address}\n\n{self.nonce}\n\nURI: https://reiki.web3go.xyz\nVersion: 1\nChain ID: 56\nNonce: {self.nonce}\nIssued At: {self.iso_date_string}"
        data={
            "address": self.account.address,
            "nonce": self.nonce,
            "challenge": json.dumps({"msg": msg}),
            "signature": self.signature
        }
        response = session.post(
            url, headers=self.headers,json=data, timeout=60)
        data = response.json()
        log_and_print(f"response:{data}")
        return data


    def checkin(self):
        current_date = datetime.utcnow().date().isoformat()
        url = f"https://reiki.web3go.xyz/api/checkin?day={current_date}"
        response = session.put(
            url, headers=self.headers, timeout=60)
        data = response.json()
        log_and_print(f"response:{data}")
        return data

    def checkResult(self):
        url = f"https://reiki.web3go.xyz/api/GoldLeaf/me"
        response = session.get(
            url, headers=self.headers, timeout=60)
        data = response.json()
        log_and_print(f"response:{data}")
        return data

    def run(self,userName, account):
        self.userName = userName
        self.account = account
        try:
            response = self.getNonce()
            self.nonce = response['nonce']
            log_and_print(f"{userName} getNonce successfully ")
        except Exception as e:
            log_and_print(f"{userName} getNonce failed: {e}")
            return False

        try:
            self.signature = self.signMessage()
            log_and_print(f"{userName} signMessage successfully ")
        except Exception as e:
            log_and_print(f"{userName} signMessage failed: {e}")
            return False    

        try:
            response = self.postChallenge()
            token = response['extra']['token']
            self.headers['authorization'] = 'Bearer ' + token
            log_and_print(f"{userName} postChallenge successfully ")
        except Exception as e:
            log_and_print(f"{userName} postChallenge failed: {e}")
            return False  
 
        try:
            response = self.checkin()
            if response != True:
                raise Exception(f"Error: {response}")
            log_and_print(f"{userName} checkin successfully ")
            excel_manager.update_info(username, "checkin successfully")
        except Exception as e:
            log_and_print(f"{userName} checkin failed: {e}")
            return False      
        '''
        try:
            response = self.checkResult()
            if response["today"] != 0:
                log_and_print(f"{userName} checkResult successfully ")
                return True
            raise Exception("Error: fake checkin")    
        except Exception as e:
            log_and_print(f"{userName} checkResult failed: {e}")
            return False       
        '''     

if __name__ == '__main__':
    proxy_list = ['http://127.0.0.1:7890']
    proxies = {'http': random.choice(proxy_list),
               'https': random.choice(proxy_list)}
    session = requests.Session()
    session.proxies = proxies
    app = ReikiSign()

    failed_list = []
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("ReikiSign", log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_reiki("eth", "ReikiSign")
    for credentials in credentials_list:
        username = credentials["username"]
        access_token = credentials["access_token"]

        account = web3.Account.from_key(access_token)    
        if(app.run(username, account) == False):
            failed_list.append((username, account))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for username, failed_list in failed_list:
        log_and_print(f"final failed username = {username}")
        excel_manager.update_info(username, "sign failed")
    excel_manager.save_msg_and_stop_service()