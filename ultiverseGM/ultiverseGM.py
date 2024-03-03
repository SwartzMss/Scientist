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
from web3 import Web3
from eth_abi import encode

# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)
from tools.rpc import Rpc
# 现在可以从tools目录导入UserInfo
from tools.UserInfo import UserInfo

# 现在可以从tools目录导入excelWorker
from tools.excelWorker import excelWorker
from tools.switchProxy import ClashAPIManager
# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\ultiverseGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class ultiverseGM:
    def __init__(self,rpc_url='https://1rpc.io/opbnb', chain_id=204):
        self.alias = None
        self.account = None
        self.signMsg = None
        self.rpc = Rpc(rpc=rpc_url, chainid=chain_id)
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
        soul_in_account = int(json_strr["data"]['soulInAccount'])// 1000000
        soul_in_wallets = int(json_strr["data"]['soulInWallets'])// 1000000
        log_and_print(f"{alias} soul_in_account : {soul_in_account} soul_in_wallets {soul_in_wallets}")
        total_soul = soul_in_account + soul_in_wallets
        final_result = max(soul_in_account, soul_in_wallets)
        return final_result,total_soul

    def post_info(self):
        url = f"https://toolkit.ultiverse.io/api/user/info"
        response = session.post(url, headers=self.headers, timeout=60)
        data = response.json()
        return data

    def getAgentinfo(self):
        url = f"https://pml.ultiverse.io/api/register/agent-info"
        response = session.get(url, headers=self.headers, timeout=60)
        data = response.json()
        return data

    def getProfile(self):
        url = f"https://pml.ultiverse.io/api/profile"
        response = session.get(url, headers=self.headers, timeout=60)
        data = response.json()
        return data

    def getResultsStartDate(self):
        current_date = datetime.datetime.now()
        # 格式化日期为 "YYYY-MM-DD" 格式的字符串
        current_date_string = current_date.strftime("%Y-%m-%d")
        first_day_of_last_month = (current_date.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
        # 格式化日期为 "YYYY-MM-DD" 格式的字符串
        first_day_of_last_month_string = first_day_of_last_month.strftime("%Y-%m-%d")
        url = f"https://pml.ultiverse.io/api/explore/results?startDate={first_day_of_last_month_string}&endDate={current_date_string}"
        response = session.get(url, headers=self.headers, timeout=60)
        data = response.json()
        return data

    def getList(self):
        url = f"https://pml.ultiverse.io/api/explore/list"
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
        url = f"https://pml.ultiverse.io/api/explore/sign"
        data={
            "worldIds": signinData["worldIds"],
            "chainId":204
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
        dataInfo = MethodID+param
        res = self.rpc.transfer(
            self.account, contract_addr, 0, 103808, data=dataInfo)
        return res


    def send_raw_transaction(self, hex):
        data = {"jsonrpc":"2.0","method":"eth_sendRawTransaction","params":[hex],"id":1}
        try:
            res = requests.post(self.rpc, json=data, headers=headers,  proxies=self.proxies)
            return res.json()
        except Exception as e:
            time.sleep(2)
            return None

    def count_explored_entries(self,data):
        # Assuming 'data' is a dictionary with a 'data' key containing a list of entries
        return sum(1 for entry in data['data'] if entry.get('explored', False))

    def count_unexplored_entries(self,data):
        # Assuming 'data' is a dictionary with a 'data' key containing a list of entries
        return sum(1 for entry in data['data'] if not entry.get('explored', True))

    def getCheck(self,voyageId):
        url = f"https://pml.ultiverse.io/api/explore/check?id={voyageId}&chainId=204"
        response = session.get(url, headers=self.headers, timeout=60)
        data = response.json()
        return data

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
            response = self.post_info()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            log_and_print(f"{alias} post_info successfully")
        except Exception as e:
            log_and_print(f"{alias} post_info failed: {e}")
            excel_manager.update_info(alias, f" post_info failed: {e}")
            return False 

        try:
            response = self.getAgentinfo()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            log_and_print(f"{alias} getAgentinfo successfully")
        except Exception as e:
            log_and_print(f"{alias} getAgentinfo failed: {e}")
            excel_manager.update_info(alias, f" getAgentinfo failed: {e}")
            return False 

        try:
            self.headers.pop('Cookie', None)
            response = self.getProfile()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            points = int(response["data"]['points'])
            soulPointsForExplored, soulPoints = self.calculate_total_soul_from_json(response)
            log_and_print(f"{alias} first getProfile successfully")
        except Exception as e:
            log_and_print(f"{alias} first getProfile failed: {e}")
            excel_manager.update_info(alias, f" first getProfile failed: {e}")
            return False 


        try:
            response = self.getResultsStartDate()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            log_and_print(f"{alias} getResultsStartDate successfully")
        except Exception as e:
            log_and_print(f"{alias} getResultsStartDate failed: {e}")
            excel_manager.update_info(alias, f" getResultsStartDate failed: {e}")
            return False 


        try:
            response = self.getList()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            time.sleep(2)
            signdata = self.filter_tasks_within_soul_limit(response,soulPointsForExplored)
            # 解析 JSON 字符串回 Python 对象
            signJason = json.loads(signdata)
            exploredNum = self.count_explored_entries(response)
            unexploredNum = self.count_unexplored_entries(response)
            # 检查 worldIds 是否为空
            if not signJason['worldIds']:  # 这将检查列表是否为空
                log_and_print(f"{alias} soulPoints = {soulPoints}  points = {points} exploredNum = {exploredNum} unexploredNum = {unexploredNum}")
                excel_manager.update_info(alias, f"No more task has been explored! soulPoints = {soulPoints} points = {points} exploredNum = {exploredNum} unexploredNum = {unexploredNum}")
                return True
            log_and_print(f"{alias} first getList successfully ")
        except Exception as e:
            log_and_print(f"{alias} first getList failed: {e}")
            excel_manager.update_info(alias, f" first getList failed: {e}")
            return False 

        try:
            response = self.sign(signJason)
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            log_and_print(f"{alias} sign successfully ")
        except Exception as e:
            log_and_print(f"{alias} sign failed: {e}")
            excel_manager.update_info(alias, f" sign failed: {e}")
            return False 
            
        try:
            exploreCallData = self.encode_ultiverse_data(response)
            voyageId = response["data"]["voyageId"]
            response = self.explore_action(exploreCallData)
            if 'error' in response:
                raise Exception(f"Error: {response}")
            response = self.getList()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            log_and_print(f"{alias} explore_action successfully")
        except Exception as e:
            log_and_print(f"{alias} explore_action failed: {e}")
            excel_manager.update_info(alias, f" explore_action failed: {e}")
            return False 

        try:
            response = self.getProfile()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            pointsFinal = int(response["data"]['points'])
            soulPointsForExplored, soulPoints = self.calculate_total_soul_from_json(response)
            log_and_print(f"{alias} second getProfile successfully soulPoints")
        except Exception as e:
            log_and_print(f"{alias} second getProfile failed: {e}")
            excel_manager.update_info(alias, f"second getProfile failed: {e}")
            return False 

        try:
            response = self.getCheck(voyageId)
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            log_and_print(f"{alias} getCheck successfully")
        except Exception as e:
            log_and_print(f"{alias} getCheck failed: {e}")
            excel_manager.update_info(alias, f" getCheck failed: {e}")
            return False 

        try:
            response = self.getList()
            if response["success"] != True:
                raise Exception(f" Error: {response}")
            exploredNum = self.count_explored_entries(response)
            unexploredNum = self.count_unexplored_entries(response)
            log_and_print(f"{alias} soulPoints = {soulPoints}  points = {points} exploredNum = {exploredNum} unexploredNum = {unexploredNum}")
            if isRetry == False and soulPointsForExplored >= 50 and unexploredNum > 0 :
                log_and_print(f"{alias} need retry for switch another wallet")
                return False
            excel_manager.update_info(alias, f"some tasks have been explored! soulPoints = {soulPoints} points = {points} exploredNum = {exploredNum} unexploredNum = {unexploredNum}")
            return True
        except Exception as e:
            log_and_print(f"{alias} final getList failed: {e}")
            excel_manager.update_info(alias, f" final getList failed: {e}")
            return False 


if __name__ == '__main__':
    session = requests.Session()
    isRetry = False
    app = ultiverseGM()
    proxyApp = ClashAPIManager(logger = log_and_print)
    failed_list = []
    retry_list = [] 
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("ultiverseGM", log_and_print)

    credentials_list = UserInfoApp.find_user_credentials_for_eth("ultiverseGM")
    for credentials in credentials_list:
        alias = credentials["alias"]
        key = credentials["key"]
        proxyName = UserInfoApp.find_proxy_by_alias_in_file(alias)
        if not proxyName:
            log_and_print(f"cannot find proxy username = {alias}")
            continue
        if proxyApp.change_proxy_until_success(proxyName) == False:
            continue
        time.sleep(5)   
        account = web3.Account.from_key(key)    
        if(app.run(alias, account) == False):
            retry_list.append((alias, account))

    if len(retry_list) != 0:
        log_and_print("start retry faile case")
        isRetry = True
        time.sleep(10)

    for alias, account in retry_list:
        proxyName = UserInfoApp.find_proxy_by_alias_in_file(alias)
        if not proxyName:
            log_and_print(f"cannot find proxy username = {alias}")
            continue
        if proxyApp.change_proxy_until_success(proxyName) == False:
            continue
        time.sleep(5)   
        if(app.run(alias, account) == False):
            failed_list.append((alias, account))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for alias, account in failed_list:
        log_and_print(f"final failed username = {alias}")
    excel_manager.save_msg_and_stop_service()
    proxyApp.change_proxy("🇭🇰 HK | 香港 01")
