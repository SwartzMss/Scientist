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
        self.headers.pop('Ul-Auth-Token', None)
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

    def calculate_total_soul_from_json(self, json_strr):

        soul_in_account = int(json_strr["data"]['soulInAccount'])
        soul_in_wallets = int(json_strr["data"]['soulInWallets'])
        
        total_soul = soul_in_account + soul_in_wallets
        final_result = total_soul // 1000000
        return final_result

    def getProfile(self):
        url = f"https://pilot.ultiverse.io/api/profile"
        response = session.get(url, headers=self.headers, timeout=60)
        data = response.json()
        return data

    def getList(self):
        url = f"https://pilot.ultiverse.io/api/explore/list"
        response = session.get(url, headers=self.headers, timeout=60)
        data = response.json()
        return data

    def filter_tasks_within_soul_limit(self,json_data, num):
        available_tasks = [task for task in json_data['data'] if not task['explored']]
        available_tasks.sort(key=lambda x: x['soul'])
        
        selected_tasks = []
        current_soul_sum = 0
        
        for task in available_tasks:
            if current_soul_sum + task['soul'] <= num:
                selected_tasks.append(task)
                current_soul_sum += task['soul']
            if current_soul_sum >= num:
                break
        
        world_ids = [task['worldId'] for task in selected_tasks if 'worldId' in task]
        return json.dumps({"worldIds": world_ids})
    
    def sign(self, signinData):
        url = f"https://pilot.ultiverse.io/api/explore/sign"
        data={
            "worldIds": signinDataDict["worldIds"]
        }
        response = session.post(url, headers=self.headers,json=data, timeout=60)
        data = response.json()
        return data

    def encode_ultiverse_data(self, json_data):
        deadline = json_data['data']['deadline']
        voyageId = json_data['data']['voyageId']
        destinations = json_data['data']['destinations']
        data_hex = json_data['data']['data']
        signatureinfo_hex = json_data['data']['signature']
        # 转换十六进制字符串为字节串
        data_bytes = Web3.to_bytes(hexstr=data_hex)
        signatureinfo_bytes = Web3.to_bytes(hexstr=signatureinfo_hex)
    
        # 定义参数值和它们的类型
        values = [
            deadline,  # deadline, uint256
            voyageId,  # voyageId, uint256
            destinations,  # destinations, uint16[]
            data_bytes,  # data, bytes32
            signatureinfo_bytes  # signatureinfo, bytes
        ]
        types = ['uint256', 'uint256', 'uint16[]', 'bytes32', 'bytes']
        
        # 使用eth_abi进行编码
        encoded_data = encode(types, values)
        
        # 返回编码后的十六进制字符串
        return encoded_data.hex()

    def explore_action(self,param):
        contract_addr = Web3.to_checksum_address("0x16d4c4b440cb779a39b0d8b89b1590a4faa0215d")
        MethodID="0x75278b5c"
        data = MethodID+param
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
            excel_manager.update_info(alias, f" get_nonce failed: {e}")
            return False

        try:
            self.signature = self.sign_message()
            log_and_print(f"{alias} sign_message successfully ")
        except Exception as e:
            log_and_print(f"{alias} sign_message failed: {e}")
            excel_manager.update_info(alias, f" sign_message failed: {e}")
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
            excel_manager.update_info(alias, f" signin failed: {e}")
            return False     

        try:
            response = self.getProfile()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            soulPoints = self.calculate_total_soul_from_json(response)
            log_and_print(f"{alias} getProfile successfully soulPoints = {soulPoints} ")
        except Exception as e:
            log_and_print(f"{alias} getProfile failed: {e}")
            excel_manager.update_info(alias, f" getProfile failed: {e}")
            return False 

        try:
            response = self.getList()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            signdata = self.filter_tasks_within_soul_limit(response,soulPoints)
            # 解析 JSON 字符串回 Python 对象
            data = json.loads(signdata)
            
            # 检查 worldIds 是否为空
            if not data['worldIds']:  # 这将检查列表是否为空
                log_and_print(f"{alias} No tasks found within the soul limit or maybe tasks all been explored")
                excel_manager.update_info(alias, f" No tasks found within the soul limit or maybe tasks all been explored")
                return True
            log_and_print(f"{alias} getList successfully ")
        except Exception as e:
            log_and_print(f"{alias} getList failed: {e}")
            excel_manager.update_info(alias, f" getList failed: {e}")
            return False 

        try:
            response = self.sign(signdata)
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            log_and_print(f"{alias} sign successfully ")
            excel_manager.update_info(alias, f" sign successfully: {e}")
        except Exception as e:
            log_and_print(f"{alias} sign failed: {e}")
            excel_manager.update_info(alias, f" sign failed: {e}")
            return False 
            
        try:
            exploreCallData = self.encode_ultiverse_data(response)
            response = self.explore_action(exploreCallData)
            if 'error' in response:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} explore_action successfully ")
            excel_manager.update_info(alias, f" explore_action successfully")
        except Exception as e:
            log_and_print(f"{alias} explore_action failed: {e}")
            excel_manager.update_info(alias, f" explore_action failed: {e}")
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
