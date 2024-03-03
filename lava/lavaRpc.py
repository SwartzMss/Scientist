import requests
from web3 import Web3
from eth_account.messages import encode_defunct
import time
import math
import sys
from decimal import Decimal
import web3
import requests
import random
import datetime
import json
import os
import random
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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\lavaRpc_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')

rpc_file_path = os.path.join(script_dir, 'RPC.txt')
address_file_path = os.path.join(script_dir, 'address.txt')

class lavaRpc:
    def __init__(self):
        self.web3 = None
        self.alias = None

    def parse_rpc_file(self):
        with open(rpc_file_path, 'r',encoding='utf-8') as file:
            lines = file.readlines()
            result = []
            for line in lines:
                parts = line.strip().split(' ', 1)  # Split on the first space only
                if len(parts) == 2:
                    result.append({'alias': parts[0], 'url': parts[1]})
        random.shuffle(result)  # Shuffle the list to break the original order
        return result

    def parse_address_file(self, max_num = 300):
        with open(address_file_path, 'r') as file:
            # 读取所有行并去除换行符
            addresses = [line.strip() for line in file.readlines()]
        # 打乱地址列表
        random.shuffle(addresses)
        return addresses[:min(max_num, len(addresses))]


    def get_balance(self, address):
        """获取指定地址的ETH余额。"""
        try:
            # 将地址转换为校验和地址格式
            checksum_address = self.web3.to_checksum_address(address)
            # 使用Web3获取校验和地址的余额（以Wei为单位）
            balance_wei = self.web3.eth.get_balance(checksum_address)
            # 将余额从Wei转换为Ether，注意正确的方法调用
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            return Decimal(balance_eth)
        except ValueError as e:
            log_and_print(f"{self.alias} 无效的地址或值错误: {e}")
        except Exception as e:
            log_and_print(f"{self.alias} 获取余额时发生未知错误: {e}")
        return None

    def run(self, alias, rpc_url):
        sleepValue = 0.5
        self.alias = alias
        log_and_print(f"{self.alias} starting")
        succeedNum = 0
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        addressList = self.parse_address_file()
        for address in addressList:
            time.sleep(sleepValue)
            if None != self.get_balance(address):
                succeedNum = succeedNum + 1
            else:
                sleepValue = sleepValue + 0.5
        log_and_print(f"{alias} succeedNum = {succeedNum}")
        excel_manager.update_info(alias, f" succeedNum: {succeedNum}")

if __name__ == "__main__":
    app = lavaRpc()
    proxyApp = ClashAPIManager(logger = log_and_print)
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("lavaRpc", log_and_print)
    rpcinfo_list = app.parse_rpc_file()
    for rpcinfo in rpcinfo_list:
        alias = rpcinfo["alias"]
        url = rpcinfo["url"]
        proxyName = UserInfoApp.find_proxy_by_alias_in_file(alias)
        if not proxyName:
            log_and_print(f"cannot find proxy username = {alias}")
            continue
        if proxyApp.change_proxy_until_success(proxyName) == False:
            continue
        app.run(alias, url)
    excel_manager.save_msg_and_stop_service()
    proxyApp.change_proxy("🇭🇰 HK | 香港 01")