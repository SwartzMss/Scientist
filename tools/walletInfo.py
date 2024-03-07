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
from web3.exceptions import TimeExhausted
# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)
from tools.UserInfo import UserInfo
from tools.excelWorker import excelWorker
# 现在可以从tools目录导入Rpc
from tools.rpc import Rpc

def log_and_print(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - {text}")

blockchains = {
    "BNB": {
        "url": "https://bsc-dataseed.binance.org",
        "chain_id": 56
    },
    "openBNB": {
        "url": "https://opbnb-mainnet-rpc.bnbchain.org",
        "chain_id": 204
    },
    "matic": {
        "url": "https://rpc-mainnet.maticvigil.com",
        "chain_id": 137
    }
}

class wallinfo:
    def __init__(self, rpc_url, chain_id):
        self.rpc = Rpc(rpc=rpc_url, chainid=chain_id)
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.chain_id = chain_id

    def get_balance(self, to_address):
        balance_result = self.rpc.get_balance(to_address)
        if balance_result == None:
            return None
        balance_wei = int(balance_result['result'], 16)
        balance_value = self.web3.from_wei(balance_wei, 'ether')
        return Decimal(balance_value)

if __name__ == "__main__":
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("wallet", log_and_print)
    alais_list = UserInfoApp.find_alias_by_path()
    alias_info = {alias: {} for alias in alais_list}
    
    # 收集地址信息
    for alias in alias_list:
        key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        address = web3.Account.from_key(key).address
        # 将地址信息存储在内存中
        alias_info[alias]['address'] = address
    
    for name, details in blockchains.items():
        log_and_print(f"Name: {name}, URL: {details['url']}, Chain ID: {details['chain_id']}")
        app = wallinfo(details['url'], details['chain_id'])
        for alias in alais_list:
            key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
            address = web3.Account.from_key(key).address    
            balance = app.get_balance(address)
            log_and_print(f"{alias} address {address} {name}_balance {balance}")
            excel_manager.update_info(alias, str(balance), f"{name}_balance")
            
    excel_manager.save_msg_and_stop_service()

