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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\BerachainBatchMint_{current_time}.log'

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')

class BerachainBatchMint:
    def __init__(self, rpc_url='https://artio.rpc.berachain.com', chain_id=80085):
        self.alias = None
        self.rpc = Rpc(rpc=rpc_url, chainid=chain_id)
        self.gaslimit = 350000
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = None
        self.QueueForApprovalResult = []
        self.QueueForMint = []
        self.QueueForMintResult = []
        self.gasprice = int(self.rpc.get_gas_price()['result'], 16) * 5
        self.headers = {
            'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 116)}.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',

        }

    def get_approval_amount(self):
        contract_abi = [
            {
                "type": "function",
                "name": "allowance",
                "inputs": [
                    {"name": "", "type": "address", "internalType": "address"},
                    {"name": "", "type": "address", "internalType": "address"}
                ],
                "outputs": [
                    {"name": "", "type": "uint256", "internalType": "uint256"}
                ],
                "stateMutability": "view"
            },
        ]
        contract_address = Web3.to_checksum_address("0x6581e59A1C8dA66eD0D313a0d4029DcE2F746Cc5")
        spender_address = Web3.to_checksum_address("0x09ec711b81cd27a6466ec40960f2f8d85bb129d9")
        contract = self.web3.eth.contract(address = contract_address, abi=contract_abi)
        try:
            allowance = contract.functions.allowance(self.account.address, spender_address).call()
            return allowance
        except Exception as e:
            excel_manager.update_info(self.alias, f" allowance failed: {e}")
        return None

    def get_stgusdc_balance(self):
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
        contract_address = Web3.to_checksum_address("0x6581e59A1C8dA66eD0D313a0d4029DcE2F746Cc5")
        contract = self.web3.eth.contract(address = contract_address, abi=contract_abi)
        try:
            balance = contract.functions.balanceOf(self.account.address).call()
            return balance
        except Exception as e:
            excel_manager.update_info(self.alias, f" balanceOf failed: {e}")
        return None

    def encode_mint_data(self, amount):
        spender = "0x09ec711b81cD27A6466EC40960F2f8D85BB129D9"
        amountValue = Web3.to_wei(amount, 'ether')
        values = [
            self.account.address,
            "0x6581e59A1C8dA66eD0D313a0d4029DcE2F746Cc5",
            amountValue, 
        ]
        types = ['address', 'address','uint256']
        
        encoded_data = encode(types, values)
        return encoded_data.hex()

    def mint_stgusdc_to_honey(self, amount):
        __contract_addr = "0x09ec711b81cD27A6466EC40960F2f8D85BB129D9"
        param = self.encode_mint_data(amount)
        MethodID="0xc6c3bbe6" 
        for alias, key in self.QueueForMint:
            time.sleep(5)
            try:
                self.alias = alias
                self.account = self.web3.eth.account.from_key(key)
                data = MethodID + param
                response = self.rpc.transfer(
                    self.account, __contract_addr, 0, self.gaslimit, self.gasprice, data=data)
                if 'error' in response:
                    raise Exception(f"Error: {response}")
                hasResult = response["result"]
                log_and_print(f"{alias} mint_stgusdc_to_honey successfully hash = {hasResult}")
                self.QueueForMintResult.append((alias, hasResult))
            except Exception as e:
                log_and_print(f"{alias} mint_stgusdc_to_honey failed: {e}")
                excel_manager.update_info(alias, f" mint_stgusdc_to_honey failed: {e}")
        self.QueueForMint.clear()


    def encode_approve_data(self, amount):
        spender = "0x09ec711b81cD27A6466EC40960F2f8D85BB129D9"
        amountValue = Web3.to_wei(amount, 'ether')
        values = [
            spender,
            amountValue, 
        ]
        types = ['address', 'uint256']
        
        encoded_data = encode(types, values)
        return encoded_data.hex()

    def approve_action(self, alias, key, amount):
        self.alias = alias
        self.account = self.web3.eth.account.from_key(key) 
        approval_mount = self.get_approval_amount()
        stgusdc_balance = self.get_stgusdc_balance()
        if stgusdc_balance == None or approval_mount == None:
            return
        log_and_print(f"{alias} stgusdc_balance = {Web3.from_wei(stgusdc_balance, 'ether')}")
        log_and_print(f"{alias} approval_mount = {Web3.from_wei(approval_mount, 'ether')}")
        if stgusdc_balance <= Web3.to_wei(amount, 'ether'):
            log_and_print(f"{alias} stgusdc_balance = {Web3.from_wei(stgusdc_balance, 'ether')} less than amount {amount}")
            excel_manager.update_info(alias, f" stgusdc_balance = {Web3.from_wei(stgusdc_balance, 'ether')} less than amount {amount}")
            return
        if approval_mount >= Web3.to_wei(amount, 'ether'):
            self.QueueForApprovalResult.append((alias, key, None))
            return
        __contract_addr = "0x6581e59A1C8dA66eD0D313a0d4029DcE2F746Cc5"
        param = self.encode_approve_data(amount)
        MethodID="0x095ea7b3" 
        try:
            time.sleep(3)
            data = MethodID + param
            response = self.rpc.transfer(
                self.account, __contract_addr, 0, self.gaslimit, self.gasprice, data=data)
            if 'error' in response:
                raise Exception(f"Error: {response}")
            hasResult = response["result"]
            log_and_print(f"{alias} approve_action successfully hash = {hasResult}")
            self.QueueForApprovalResult.append((alias, key, hasResult))
        except Exception as e:
            log_and_print(f"{alias} approve_action failed: {e}")
            excel_manager.update_info(alias, f" approve_action failed: {e}")

    def get_balance(self):
        balance_result = self.rpc.get_balance(self.account.address)
        if balance_result == None:
            return None
        balance_wei = int(balance_result['result'], 16)
        balance_bera = self.web3.from_wei(balance_wei, 'ether')
        return Decimal(balance_bera)

    def check_all_transaction_for_mint(self):
        for alias, tx_hash in self.QueueForMintResult:
            log_and_print(f"{alias} start checking transaction status for mint")
            code,msg = self.check_transaction_status(tx_hash)
            excel_manager.update_info(alias, f"tx_hash = {tx_hash} code = {code} msg = {msg}")
        self.QueueForMintResult.clear()

    def check_all_transaction_for_Approve(self):
        for alias, key, tx_hash in self.QueueForApprovalResult:
            log_and_print(f"{alias} start checking transaction status for Approve")
            if tx_hash == None:
                log_and_print(f"{alias} no need check Approve")
                self.QueueForMint.append((alias, key))
                continue
            code,msg = self.check_transaction_status(tx_hash)
            log_and_print(f"{alias} tx_hash = {tx_hash} code = {code} msg = {msg}")
            if code != True:
                excel_manager.update_info(alias, f" Approve went wrong: tx_hash = {tx_hash} code = {code} msg = {msg}")
            self.QueueForMint.append((alias, key))
        self.QueueForApprovalResult.clear()

    def check_transaction_status(self, tx_hash, timeout=300, interval=30):
        """检查交易的状态，返回是否确认和交易状态。使用计数器实现超时。"""
        max_attempts = timeout // interval  # 计算最大尝试次数
        attempts = 0  # 初始化尝试次数计数器

        while attempts < max_attempts:  # 循环直到达到最大尝试次数
            try:
                receipt = self.web3.eth.get_transaction_receipt(tx_hash)                
                if receipt is not None:
                    if receipt.status == 1:
                        return True, "success"  # 交易已确认且成功
                    else:
                        return False, "failure"  # 交易已确认但失败
            except Exception as e:
                log_and_print(f"Error checking transaction status: {e}")
            
            time.sleep(interval)  # 等待一段时间再次检查
            attempts += 1  # 更新尝试次数

        # 超时后返回False，表示交易状态未知或未确认，状态为挂起
        return False, "pending"

if __name__ == "__main__":
    UserInfoApp = UserInfo(log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_eth("bearChainGM")
    excel_manager = excelWorker("BerachainBatchMint", log_and_print)
    bera_mint = BerachainBatchMint()
    amount = 10
    for credentials in credentials_list:
        alias = credentials["alias"]
        key = credentials["key"]  
        bera_mint.approve_action(alias, key, amount)
        time.sleep(5)

    bera_mint.check_all_transaction_for_Approve()
    bera_mint.mint_stgusdc_to_honey(amount)
    bera_mint.check_all_transaction_for_mint()
    excel_manager.save_msg_and_stop_service()
