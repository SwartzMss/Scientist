
#https://www.intract.io

from eth_account.messages import encode_defunct
import time
import math
import sys
import web3
import requests
import random
import datetime
import json
import os
from dotenv import load_dotenv
load_dotenv()

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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\IntractSign_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class IntractSign:
    def __init__(self):
        self.alias = None
        self.account = None
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
            'Referer': 'https://www.intract.io/?referralCode=raF4SD&referralSource=REFERRAL_PAGE&referralLink=https%3A%2F%2Fwww.intract.io%2Freferral',
        }

    # 获取 nonce
    def get_nonce(self):
        url = f"https://api.intract.io/api/qv1/auth/generate-nonce"
        data={
            "walletAddress": self.account.address
        }
        response = session.post(
            url,json=data, timeout=10)
        data = response.json()
        return data

    def _sign_message(self,nonce):
        #log_and_print('wallet:' + str(self.account.address))
        msg = f"Nonce: {nonce}"
        res = self.account.sign_message(encode_defunct(text=msg))
        return res.signature.hex()


    def gm(self):
        url = f"https://api.intract.io/api/qv1/auth/gm-streak"
        response = session.post(url, headers=self.headers, timeout=10)
        data = response.json()
        #log_and_print(f"data {data} ")
        return data

    def wallet(self,hex):
        url = f"https://api.intract.io/api/qv1/auth/wallet"
        data={
            "signature": hex,
            "userAddress": self.account.address,
            "isTaskLogin": False,
            "width": "590px",
            "reAuth": False,
            "connector": "metamask",
            "namespaceTag": "EVM",
            "referralCode": None,
            "referralLink": None,
            "referralSource": None
        }
        response = session.post(
            url,json=data, timeout=10)
        set_cookie_string = response.headers.get('set-cookie')
        start = set_cookie_string.find("auth-token=")
        if start != -1:
            start += len("auth-token=")
            end = set_cookie_string.find(";", start)
            auth_token = set_cookie_string[start:end] if end != -1 else set_cookie_string[start:]
        else:
            auth_token = None
        data = response.json()
        return data,auth_token

    def referral(self):
        url = f"https://api.intract.io/api/qv1/campaign/referral-session"
        data={
            "referralCode": "raF4SD",
            "referralLink": "https://www.intract.io/referral",
            "referralSource": "REFERRAL_PAGE"
        }
        response = session.post(
            url, headers=self.headers,json=data, timeout=10)
        data = response.json()
        return data

    def run(self,alias, account):
        self.alias = alias
        self.account = account
        try:
            nonce = self.get_nonce()['data']['nonce']
            hex = self._sign_message(nonce)
            data,auth_token = self.wallet(hex)
            self.headers['authorization'] = 'Bearer ' + auth_token
            log_and_print(f"{alias} login successfully ")
        except Exception as e:
            log_and_print(f"{alias} login failed: {e}")
            excel_manager.update_info(alias, f" login failed: {e}")
            return False

        try:
            referral = self.referral()
            #这不校验结果
        except Exception as e:
            pass

        try:
            gm = self.gm()
            if "already done for today" in gm.get('message', ""):
                log_and_print(f"{alias} gm already done successfully")
                excel_manager.update_info(alias, "already sign successfully")
                return True
            streakCount=gm['streakCount']
            log_and_print(f"{alias} gm successfully")
            excel_manager.update_info(alias, "sign successfully")
            return True
        except Exception as e:
            log_and_print(f"{alias} gm failed: {e}")
            excel_manager.update_info(alias, f" gm failed: {e}")
            return False

            


if __name__ == '__main__':
    session = requests.Session()
    app = IntractSign()
    retry_list = []
    failed_list = []
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("IntractSign", log_and_print)
    alais_list = UserInfoApp.find_alias_by_path()
    for alias in alais_list:
        key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        account = web3.Account.from_key(key)    
        if(app.run(alias, account) == False):
            retry_list.append((alias, account))

    if len(retry_list) != 0:
        log_and_print(f"start retry failed case")
        time.sleep(5)   

    for alias, account in retry_list:
        if(app.run(alias, account) == False):
            failed_list.append((alias, account))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for alias, account in failed_list:
        log_and_print(f"final failed username = {alias}")
    excel_manager.save_msg_and_stop_service()
