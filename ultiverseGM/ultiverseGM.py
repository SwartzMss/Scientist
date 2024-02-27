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
import re


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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\ultiverseGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a') as log_file:
        print(message)
        log_file.write(message + '\n')


class ultiverseGM:
    def __init__(self):
        self.alias = None
        self.account = None
        self.signMsg = None
        self.headers = {
            'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 116)}.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://pilot.ultiverse.io',
            'Ul-Auth-Api-Key':'YWktYWdlbnRAZFd4MGFYWmxjbk5s'
        }

    # 获取 nonce
    def get_nonce(self):
        self.headers.pop('Cookie', None)
        self.headers.pop('Ul-Auth-Address', None)
        url = f"https://toolkit.ultiverse.io/api/user/signature"
        data={
            "address": self.account.address,
            "feature":"assets-wallet-login",
            "chainId":204
        }
        response = session.post(
            url, json=data,  headers=self.headers, timeout=60)
        data = response.json()
        return data

    def sign_message(self):
        res = self.account.sign_message(encode_defunct(text=self.signMsg))
        return res.signature.hex()


    def signin(self):
        url = f"https://toolkit.ultiverse.io/api/wallets/signin"
        data={
            "address":self.account.address,
            "signature":self.signature,
            "chainId":204
        }
        response = session.post(url, headers=self.headers,json=data, timeout=60)
        data = response.json()
        return data

    def sign(self):
        url = f"https://pilot.ultiverse.io/api/explore/sign"
        data={
            "worldIds":["BAC"]
        }
        response = session.post(url, headers=self.headers,json=data, timeout=60)
        data = response.json()
        return data

    def explore_action(self,contract_addr, signature, voyageId, deadline):
        contract_addr = contract_addr
        MethodID="0x75278b5c"
        param_1="0000000000000000000000000000000000000000000000000000000065de06f8"
        param_2="000000000000000000000000000000000000000000000000000000000004124d"
        param_3="00000000000000000000000000000000000000000000000000000000000000a0"
        param_4="aa7e241318600646be02c4ae6c3b80f2ce78d107af72dc1abbf6338db2694263"
        param_5="00000000000000000000000000000000000000000000000000000000000000e0"
        param_6="0000000000000000000000000000000000000000000000000000000000000001"
        param_7="0000000000000000000000000000000000000000000000000000000000000002"
        param_8="0000000000000000000000000000000000000000000000000000000000000041"
        param_9="64342684f186055a527b43afd75b89a78c8f13b133b1e553b9b35fc383c86fe3"
        param_10="6d2bdf5edb02e80298574f17674178b3e5cf12a41322731705c999f30b10f862"
        param_11="1b00000000000000000000000000000000000000000000000000000000000000"


        data = MethodID+param_1+param_2+param_3+param_4+param_5+param_6+param_7+param_8+param_9+param_10+param_11+param_12
        res = self.rpc.transfer(
            self.account, contract_addr, 0, 21000, data=data)
        return res


    def run(self,alias, account):
        self.alias = alias
        self.account = account
        try:
            response = self.get_nonce()
            if response["success"] != True:
                raise Exception(f"get_nonce Error: {response}")
            self.signMsg = response["data"]["message"]
            log_and_print(f"{alias} get_nonce succeed")
        except Exception as e:
            log_and_print(f"{alias} get_nonce failed: {e}")
            return False

        try:
            self.signature = self.sign_message()
            log_and_print(f"{alias} sign_message successfully ")
        except Exception as e:
            log_and_print(f"{alias} sign_message failed: {e}")
            return False

        try:
            response = self.signin()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            log_and_print(f"{alias} signin successfully ")
            access_token = response["data"]["access_token"]
            self.headers['Ul-Auth-Token'] =  access_token
            self.headers['Cookie'] =  "Ultiverse_Authorization="+access_token
            self.headers['Ul-Auth-Address'] =  self.account.address
        except Exception as e:
            log_and_print(f"{alias} signin failed: {e}")
            return False     

        try:
            response = self.sign()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            log_and_print(f"{alias} sign successfully ")
        except Exception as e:
            log_and_print(f"{alias} sign failed: {e}")
            return False 

if __name__ == '__main__':
    session = requests.Session()
    app = ultiverseGM()

    failed_list = []
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("ultiverseGM", log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_eth("ultiverseGM")
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
