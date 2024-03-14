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
from tools.socket5SwitchProxy import socket5SwitchProxy

# 获取当前时间并格式化为字符串
current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\ReikiSign_{current_time}.log'


def log_message(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class ReikiSign:
    def __init__(self):
        self.alias = None
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
            url, headers=self.headers,json=data, timeout=10)
        log_and_print(f"{self.alias} getNonce response.status_code:{response.status_code}")
        data = response.json()
        log_and_print(f"{self.alias} getNonce response:{data}")
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
            url, headers=self.headers,json=data, timeout=10)
        log_and_print(f"{self.alias} postChallenge response.status_code:{response.status_code}")
        data = response.json()
        log_and_print(f"{self.alias} postChallenge response:{data}")
        return data

    def getInfo(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://reiki.web3go.xyz/ai/console/api/info"
        response = session.get(
            url, headers=self.headers, timeout=10)
        log_and_print(f"{self.alias} getInfo response.status_code:{response.status_code}")
        data = response.json()
        log_and_print(f"{self.alias} getInfo response:{data}")
        return data

    def getProfile(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://reiki.web3go.xyz/ai/console/api/account/profile"
        response = session.get(
            url, headers=self.headers, timeout=10)
        log_and_print(f"{self.alias} getProfile response.status_code:{response.status_code}")
        data = response.json()
        log_and_print(f"{self.alias} getProfile response:{data}")
        return data

    def getSuggested_question(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://reiki.web3go.xyz/ai/api/home/suggested_question"
        response = session.get(
            url, headers=self.headers, timeout=10)
        log_and_print(f"{self.alias} getSuggested_question response.status_code:{response.status_code}")
        data = response.json()
        log_and_print(f"{self.alias} getSuggested_question response:{data}")
        return data

    def getSuggested_bot(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://reiki.web3go.xyz/ai/api/home/suggested_bot"
        response = session.get(
            url, headers=self.headers, timeout=10)
        log_and_print(f"{self.alias} getSuggested_bot response.status_code:{response.status_code}")
        data = response.json()
        log_and_print(f"{self.alias} getSuggested_bot response:{data}")
        return data

    def checkin(self):
        current_date = datetime.utcnow().date().isoformat()
        url = f"https://reiki.web3go.xyz/api/checkin?day={current_date}"
        response = session.put(
            url, headers=self.headers, timeout=10)
        log_and_print(f"{self.alias} checkin response.status_code:{response.status_code}")
        data = response.json()
        log_and_print(f"{self.alias} checkin response:{data}")
        return data

    def checkResult(self):
        url = f"https://reiki.web3go.xyz/api/GoldLeaf/me"
        response = session.get(
            url, headers=self.headers, timeout=10)
        log_and_print(f"{self.alias} checkResult response.status_code:{response.status_code}")
        data = response.json()
        log_and_print(f"{self.alias} checkResult response:{data}")
        return data

    def run(self,alias, account):
        self.alias = alias
        self.account = account
        try:
            response = self.getNonce()
            self.nonce = response['nonce']
            log_and_print(f"{alias} getNonce successfully ")
        except Exception as e:
            log_and_print(f"{alias} getNonce failed: {e}")
            excel_manager.update_info(alias, f"getNonce failed: {e}")
            return False

        try:
            self.signature = self.signMessage()
            log_and_print(f"{alias} signMessage successfully ")
        except Exception as e:
            log_and_print(f"{alias} signMessage failed: {e}")
            excel_manager.update_info(alias, f"signMessage failed: {e}")
            return False    

        try:
            response = self.postChallenge()
            token = response['extra']['token']
            self.headers['authorization'] = 'Bearer ' + token
            log_and_print(f"{alias} postChallenge successfully ")
        except Exception as e:
            log_and_print(f"{alias} postChallenge failed: {e}")
            excel_manager.update_info(alias, f"postChallenge failed: {e}")
            return False  
 
        try:
            response = self.getInfo()
            response = self.getProfile()
            response = self.getSuggested_question()
            response = self.getSuggested_bot()
            log_and_print(f"{alias} first random msg successfully ")
        except Exception as e:
            log_and_print(f"{alias} first random msg failed: {e}")

        try:
            response = self.checkResult()
            if 'today' in response and isinstance(response['today'], int):
                today= response["today"]
                total = response["total"]
                log_and_print(f"{alias} checkResult already successfully total {total} today {today}")
                excel_manager.update_info(alias, f"checkResult already successfully total {total} today {today}")
                return True
        except Exception as e:
            log_and_print(f"{alias} first checkResult failed: {e}")
            excel_manager.update_info(alias, f"first checkResult failed: {e}")
            return False  

        try:
            response = self.checkin()
            if response != True:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} checkin successfully ")
        except Exception as e:
            log_and_print(f"{alias} checkin failed: {e}")
            excel_manager.update_info(alias, f"checkin failed: {e}")
            return False      

        try:
            time.sleep(2)
            response = self.getInfo()
            response = self.getProfile()
            log_and_print(f"{alias} second random msg successfully ")
        except Exception as e:
            log_and_print(f"{alias} second random msg failed: {e}")

        try:
            response = self.checkResult()
            today= response["today"]
            total = response["total"]
            log_and_print(f"{alias} second checkResult successfully total {total} today {today}")
            excel_manager.update_info(alias, f"checkResult successfully total {total} today {today}")
        except Exception as e:
            log_and_print(f"{alias} second checkResult failed: {e}")
            excel_manager.update_info(alias, f"second checkResult failed: {e}")
            return False       

if __name__ == '__main__':
    session = requests.Session()
    app = ReikiSign()
    proxyApp = socket5SwitchProxy(logger = log_and_print)
    retry_list = []
    failed_list = []
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("ReikiSign", log_and_print)
    alais_list = UserInfoApp.find_alias_by_path()
    for alias in alais_list:
        log_and_print(f"statring running by alias {alias}")
        key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        account = web3.Account.from_key(key)    
        proxyName = UserInfoApp.find_socket5proxy_by_alias_in_file(alias)
        if not proxyName:
            log_and_print(f"cannot find proxy username = {alias}")
            excel_manager.update_info(alias, f"cannot find proxy ")
            continue
        result, proxyinfo = proxyApp.change_proxy_until_success(proxyName)
        if result == False:
            log_and_print(f"change_proxy_until_success failed {alias}")
            excel_manager.update_info(alias, f"change_proxy_until_success failed")
            continue
        session.proxies = proxyinfo
        if(app.run(alias, account) == False):
            retry_list.append((alias, account))

    if len(retry_list) != 0:
        log_and_print(f"start retry failed case")
        time.sleep(5) 

    for alias, account in retry_list:
        log_and_print(f"statring rerunning by alias {alias}")
        proxyName = UserInfoApp.find_socket5proxy_by_alias_in_file(alias)
        if not proxyName:
            log_and_print(f"cannot find proxy username = {alias}")
            excel_manager.update_info(alias, f"cannot find proxy ")
            continue
        result, proxyinfo = proxyApp.change_proxy_until_success(proxyName)
        if result == False:
            log_and_print(f"change_proxy_until_success failed {alias}")
            excel_manager.update_info(alias, f"change_proxy_until_success failed")
            continue
        session.proxies = proxyinfo
        if(app.run(alias, account) == False):
            failed_list.append((alias, account))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for alias, account in failed_list:
        log_and_print(f"final failed username = {alias}")
    excel_manager.save_msg_and_stop_service()
