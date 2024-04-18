import requests
from web3 import Web3, exceptions
from eth_account.messages import encode_defunct
import time
import math
import sys
from decimal import Decimal
import web3
import random
import datetime
import json
from eth_abi import encode
from enum import Enum
from typing import List, Tuple, NamedTuple, Union
from dataclasses import dataclass
from requests.exceptions import SSLError
import os
# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)
from tools.UserInfo import UserInfo
from tools.excelWorker import excelWorker
# 现在可以从tools目录导入Rpc
from tools.rpc import Rpc
# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\GenomefiBalance_{current_time}.log'

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class GenomefiBalance:
    def __init__(self, rpc_url="https://rpc-mainnet.maticvigil.com", chain_id=137):
        self.alias = None
        self.rpc = Rpc(rpc=rpc_url, chainid=chain_id, logger = log_and_print)
        self.gaslimit = 750000
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = None
        self.headers = {
            'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 116)}.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
        }


    def get_balance(self,alias,private_key):
        self.alias = alias
        self.account = self.web3.eth.account.from_key(private_key) 
        contract_abi = [
            {
                "type": "function",
                "name": "balanceOf",
                "inputs": [
                    {
                        "name": "user",
                        "type": "address",
                        "internalType": "address"
                    }
                ],
                "outputs": [
                    {
                        "name": "",
                        "type": "uint256",
                        "internalType": "uint256"
                    }
                ],
                "stateMutability": "view"
            },
        ]
        contract_address = Web3.to_checksum_address("0xCa730042595a1809793fbe2e9883c184c7Eb27Db")
        contract = self.web3.eth.contract(address = contract_address, abi=contract_abi)
        try:
            balance = contract.functions.balanceOf(self.account.address).call()
            balance = Web3.from_wei(balance, 'ether')
            log_and_print(f"alias {alias},  balances : {balance}")
            excel_manager.update_info(self.alias, f" balance = {balance}")
        except Exception as e:
            log_and_print(f"alias {alias}, get balances failed: {e}")
            excel_manager.update_info(self.alias, f" get balances failed: {e}")


if __name__ == "__main__":
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("GenomefiBalance", log_and_print)
    app = GenomefiBalance()

    alais_list = UserInfoApp.find_alias_by_path()
    for alias in alais_list:
        log_and_print(f"statring running by alias {alias}")
        private_key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        app.get_balance(alias, private_key)
    excel_manager.save_msg_and_stop_service()
