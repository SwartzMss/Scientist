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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\MorphSwapGM_{current_time}.log'

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


#https://rpc-testnet.morphl2.io

class MorphSwapGM:
    def __init__(self, rpc_url="https://eth-sepolia-public.unifra.io", chain_id=11155111):
        self.alias = None
        self.rpc = Rpc(rpc=rpc_url, chainid=chain_id)
        self.gaslimit = 750000
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = None
        self.QueueForApprovalResult = []
        self.QueueForSwapFromEthtoMorph = []
        self.QueueForSwapFromUSDTtoMorph = []
        self.QueueForSwapFromUSDTtoMorphResult = []
        self.headers = {
            'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 116)}.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
        }


    def encodeABI_balances(self):
        encoded_data = encode(
            ["address"],
            [self.account.address]
        )
        encoded_data_hex = encoded_data.hex()
        log_and_print(f"encodeABI_balances = {encoded_data_hex}")
        return encoded_data_hex

    def encodeABI_approve(self,amount):
        amount = Web3.to_wei(amount, 'ether')
        encoded_data = encode(
            ["address", "uint256"],
            [Web3.to_checksum_address("0xcb95f07B1f60868618752CeaBBe4e52a1f564336"), amount]
        )
        encoded_data_hex = encoded_data.hex()
        log_and_print(f"encodeABI_approve = {encoded_data_hex}")
        return encoded_data_hex

    def encodeABI_depositETHTo(self):
        encoded_data = encode(
            ["address", "uint32", "bytes"],
            [self.account.address, 200000, b'']
        )
        encoded_data_hex = encoded_data.hex()
        log_and_print(f"encodeABI_depositETHTo  = {encoded_data_hex}")
        return encoded_data_hex

    def encodeABI_depositERC20To(self,amount):
        amount = Web3.to_wei(amount, 'ether')
        encoded_data = encode(
            ["address", "address", "address","uint256","uint32","bytes"],
            [Web3.to_checksum_address("0x5F4c7D793D898e64eddd1fC82D27EcfB5F6e4596"), Web3.to_checksum_address("0xB4A71512cf4F3A8f675D2aeC76198D6419D219C7"),self.account.address,amount,200000, b'']
        )
        encoded_data_hex = encoded_data.hex()
        log_and_print(f"encodeABI_depositERC20To  = {encoded_data_hex}")
        return encoded_data_hex

    def get_eth_balance(self):
        balance_result = self.rpc.get_balance(self.account.address)
        if balance_result == None:
            return None
        balance_wei = int(balance_result['result'], 16)
        balance_bera = self.web3.from_wei(balance_wei, 'ether')
        return Decimal(balance_bera)


    def get_usdt_balance(self):
        contract_abi = [
            {
                "type": "function",
                "name": "balances",
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
        contract_address = Web3.to_checksum_address("0x5F4c7D793D898e64eddd1fC82D27EcfB5F6e4596")
        contract = self.web3.eth.contract(address = contract_address, abi=contract_abi)
        try:
            balance = contract.functions.balances(self.account.address).call()
            return Web3.from_wei(balance, 'ether')
        except Exception as e:
            log_and_print(f"alias {alias}, balances failed: {e}")
            excel_manager.update_info(self.alias, f" balances failed: {e}")
        return None



    def get_approval_amount(self):
        contract_abi = [
            {
                "type": "function",
                "name": "allowance",
                "inputs": [
                    {"name": "_param1", "type": "address", "internalType": "address"},
                    {"name": "_param2", "type": "address", "internalType": "address"}
                ],
                "outputs": [
                    {"name": "", "type": "uint256", "internalType": "uint256"}
                ],
                "stateMutability": "view"
            },
        ]
        contract_address = Web3.to_checksum_address("0x5f4c7d793d898e64eddd1fc82d27ecfb5f6e4596")
        spender_address = Web3.to_checksum_address("0xcb95f07B1f60868618752CeaBBe4e52a1f564336")
        contract = self.web3.eth.contract(address = contract_address, abi=contract_abi)
        try:
            allowance = contract.functions.allowance(self.account.address, spender_address).call()
            return Web3.from_wei(allowance, 'ether')
        except Exception as e:
            log_and_print(f"alias {alias}, allowance failed: {e}")
            excel_manager.update_info(self.alias, f" allowance failed: {e}")
        return None

    def swap_eth_to_morph(self, alias, private_key):
        amount = round(random.uniform(0.001, 0.005), 3)
        self.account = self.web3.eth.account.from_key(private_key) 
        balance = self.get_eth_balance()
        log_and_print(f"alias {alias},balance= {balance} amount= {amount}")
        if balance == None or balance < Decimal(amount):
            log_and_print(f"alias {alias},swap_eth_to_morph balance= {balance} amount= {amount} too less balance skipped")
            excel_manager.update_info(alias, f"too less balance->{balance} amount = {amount} skipped","swap_eth_to_morph")
            return
        __contract_addr = Web3.to_checksum_address("0xcb95f07b1f60868618752ceabbe4e52a1f564336")
        MethodID="0x9a2ac6d5"
        param = self.encodeABI_depositETHTo()
        data = MethodID + param
        BALANCE_PRECISION = math.pow(10, 18)  # 主币精度，18位
        value = int(amount * BALANCE_PRECISION)  # 计算要发送的amount
        try:
            gasprice = int(self.rpc.get_gas_price()['result'], 16) * 2
            response = self.rpc.transfer(
                self.account, __contract_addr, value, self.gaslimit, gasprice, data=data)
            if 'error' in response:
                raise Exception(f"Error: {response}")
            hasResult = response["result"]
            log_and_print(f"{alias} swap_bera_to_stgusdc.transfer successfully hash = {hasResult}")
            self.QueueForSwapFromEthtoMorph.append((alias, hasResult))

        except Exception as e:
            log_and_print(f"{alias} swap_eth_to_morph.transfer failed: {e}")
            excel_manager.update_info(alias, f" transfer failed: {e}", "swap_eth_to_morph")



    def approve_action(self,alias, private_key):
        amount = round(random.uniform(0.1, 0.5), 1)
        self.account = self.web3.eth.account.from_key(private_key) 
        balance = self.get_usdt_balance()
        approval_mount = self.get_approval_amount()
        log_and_print(f"alias {alias},amount= {amount} balance= {balance} approval_mount= {approval_mount}")
        if balance == None or balance < Decimal(amount):
            log_and_print(f"alias {alias},approve_action too less balance skipped")
            excel_manager.update_info(alias, f"approve_action too less balance->{balance} amount = {amount} skipped", "approve_action")
            return
        if approval_mount >= Decimal(amount):
            log_and_print(f"alias {alias},approve_action skipped due to already done")
            excel_manager.update_info(alias, f"already done approval_mount->{approval_mount} amount = {amount}", "approve_action")
            self.QueueForApprovalResult.append((alias, private_key, None, amount))
            return
        __contract_addr = Web3.to_checksum_address("0x5F4c7D793D898e64eddd1fC82D27EcfB5F6e4596")
        param = self.encodeABI_approve(amount)
        MethodID="0x095ea7b3" 
        try:
            data = MethodID + param
            gasprice = int(self.rpc.get_gas_price()['result'], 16) * 2
            response = self.rpc.transfer(
                self.account, __contract_addr, 0, self.gaslimit, gasprice, data=data)
            if 'error' in response:
                raise Exception(f"Error: {response}")
            hasResult = response["result"]
            log_and_print(f"{alias} approve_action successfully hash = {hasResult}")
            self.QueueForApprovalResult.append((alias, private_key, hasResult, amount))
        except Exception as e:
            log_and_print(f"{alias} approve_action failed: {e}")
            excel_manager.update_info(alias, f" approve_action failed: {e}", "approve_action")


    def batch_swap_usdt_to_morph(self):
        for alias, private_key ,amount in self.QueueForSwapFromUSDTtoMorph:
            time.sleep(3)
            self.swap_usdt_to_morph(alias,private_key,amount)


    def swap_usdt_to_morph(self, alias, private_key, amount):
        self.account = self.web3.eth.account.from_key(private_key) 

        __contract_addr = Web3.to_checksum_address("0xcb95f07B1f60868618752CeaBBe4e52a1f564336")
        MethodID="0x838b2520"
        param = self.encodeABI_depositERC20To(amount)
        data = MethodID + param
        BALANCE_PRECISION = math.pow(10, 18)  # 主币精度，18位
        try:
            gasprice = int(self.rpc.get_gas_price()['result'], 16) * 2
            response = self.rpc.transfer(
                self.account, __contract_addr, 0, self.gaslimit, gasprice, data=data)
            if 'error' in response:
                raise Exception(f"Error: {response}")
            hasResult = response["result"]
            log_and_print(f"{alias} swap_usdt_to_morph transfer successfully hash = {hasResult}")
            self.QueueForSwapFromUSDTtoMorphResult.append((alias, hasResult))

        except Exception as e:
            log_and_print(f"{alias} swap_usdt_to_morph transfer failed: {e}")
            excel_manager.update_info(alias, f" transfer failed: {e}", "swap_usdt_to_morph")

    def check_all_transaction_for_SwapFromEthtoMorph(self):
        for alias, tx_hash in self.QueueForSwapFromEthtoMorph:
            log_and_print(f"{alias} start checking transaction status for SwapFromEthtoMorph")
            code,msg = self.check_transaction_status(tx_hash)
            log_and_print(f"{alias} SwapFromEthtoMorph tx_hash = {tx_hash} code = {code} msg = {msg}")
            excel_manager.update_info(alias, f"tx_hash = {tx_hash} code = {code} msg = {msg}", "swap_eth_to_morph")
        self.QueueForSwapFromEthtoMorph.clear()

    def check_all_transaction_for_SwapFromUSDTtoMorph(self):
        for alias, tx_hash in self.QueueForSwapFromUSDTtoMorphResult:
            log_and_print(f"{alias} start checking transaction status for SwapFromUSDTtoMorph")
            code,msg = self.check_transaction_status(tx_hash)
            log_and_print(f"{alias} SwapFromUSDTtoMorph tx_hash = {tx_hash} code = {code} msg = {msg}")
            excel_manager.update_info(alias, f"tx_hash = {tx_hash} code = {code} msg = {msg}", "swap_usdt_to_morph")
        self.QueueForSwapFromUSDTtoMorphResult.clear()

    def check_all_transaction_for_Approve(self):
        for alias, private_key, tx_hash,amount in self.QueueForApprovalResult:
            log_and_print(f"{alias} start checking transaction status for Approve")
            if tx_hash == None:
                log_and_print(f"{alias} no need check Approve")
                self.QueueForSwapFromUSDTtoMorph.append((alias, private_key,amount))
                continue
            code,msg = self.check_transaction_status(tx_hash)
            log_and_print(f"{alias} Approve tx_hash = {tx_hash} code = {code} msg = {msg}")
            excel_manager.update_info(alias, f"tx_hash = {tx_hash} code = {code} msg = {msg}","approve_action")
            if code != True:
                continue
            self.QueueForSwapFromUSDTtoMorph.append((alias, private_key,amount))
        self.QueueForApprovalResult.clear()

    def check_transaction_status(self, tx_hash, timeout=300, interval=10):
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
    excel_manager = excelWorker("MorphSwapGM", log_and_print)
    app = MorphSwapGM()

    # swap_eth_to_morph
    alais_list = UserInfoApp.find_alias_by_path()
    for alias in alais_list:
        log_and_print(f"statring running by alias {alias}")
        private_key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        app.swap_eth_to_morph(alias, private_key)
    app.check_all_transaction_for_SwapFromEthtoMorph()

    time.sleep(5)

    # swap_eth_to_morph
    alais_list = UserInfoApp.find_alias_by_path()
    for alias in alais_list:
        time.sleep(2)
        log_and_print(f"statring running by alias {alias}")
        private_key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        app.approve_action(alias, private_key)
        
    app.check_all_transaction_for_Approve()
    app.batch_swap_usdt_to_morph()
    app.check_all_transaction_for_SwapFromUSDTtoMorph()
    excel_manager.save_msg_and_stop_service()