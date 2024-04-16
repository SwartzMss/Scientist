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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\MintChainSwapGM_{current_time}.log'

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class MintChainSwapGM:
    def __init__(self):
        self.alias = None
        self.rpcForSepolia = Rpc(rpc_url="https://eth-sepolia-public.unifra.io", chain_id=11155111, logger = log_and_print)
        self.web3ForSepolia = Web3(Web3.HTTPProvider("https://eth-sepolia-public.unifra.io"))
        self.rpcForMintChain = Rpc(rpc_url="sepolia-testnet-rpc.mintchain.io ", chain_id=1687, logger = log_and_print)
        self.web3ForMintChain = Web3(Web3.HTTPProvider("sepolia-testnet-rpc.mintchain.io"))
        self.gaslimit = 750000
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
        
    def get_eth_balance(self):
        balance_result = self.rpcForSepolia.get_balance(self.account.address)
        if balance_result == None:
            return None
        balance_wei = int(balance_result['result'], 16)
        balance_bera = self.web3.from_wei(balance_wei, 'ether')
        return Decimal(balance_bera)

    def get_Mint_eth_balance(self):
        balance_result = self.rpcForMintChain.get_balance(self.account.address)
        if balance_result == None:
            return None
        balance_wei = int(balance_result['result'], 16)
        balance_bera = self.web3.from_wei(balance_wei, 'ether')
        return Decimal(balance_bera)

    def swap_eth_to_mint(self, alias, private_key):
        amount = round(random.uniform(0.001, 0.005), 3)
        self.account = self.web3.eth.account.from_key(private_key) 
        balance = self.get_eth_balance()
        log_and_print(f"alias {alias},balance= {balance} amount= {amount}")
        if balance == None or balance < Decimal(amount):
            log_and_print(f"alias {alias},swap_eth_to_mint balance= {balance} amount= {amount} too less balance skipped")
            excel_manager.update_info(alias, f"too less balance->{balance} amount = {amount} skipped","swap_eth_to_mint")
            return
        __contract_addr = Web3.to_checksum_address("0xcb95f07b1f60868618752ceabbe4e52a1f564336")
        MethodID="0x9a2ac6d5"
        param = self.encodeABI_depositETHTo()
        data = MethodID + param
        BALANCE_PRECISION = math.pow(10, 18)  # 主币精度，18位
        value = int(amount * BALANCE_PRECISION)  # 计算要发送的amount
        try:
            response = self.rpc.get_gas_price()
            if 'error' in response:
                raise Exception(f"get_gas_price Error: {response}")
            gasprice = int(response['result'], 16) * 2
            log_and_print(f"{alias} swap_eth_to_morph gasprice = {gasprice}")
            response = self.rpc.transfer(
                self.account, __contract_addr, value, self.gaslimit, gasprice, data=data)
            log_and_print(f"{alias} swap_eth_to_morph response = {response}")
            if 'error' in response:
                raise Exception(f" transfer Error: {response}")
            hasResult = response["result"]
            log_and_print(f"{alias} swap_bera_to_stgusdc.transfer successfully hash = {hasResult}")
            self.QueueForSwapFromEthtoMorph.append((alias, hasResult))

        except Exception as e:
            log_and_print(f"{alias} swap_eth_to_morph failed: {e}")
            excel_manager.update_info(alias, f" {e}", "swap_eth_to_morph")

    def swap_mint_to_eth(self, alias, private_key):
        amount = round(random.uniform(0.001, 0.005), 3)
        self.account = self.web3.eth.account.from_key(private_key) 
        balance = self.get_eth_balance()
        log_and_print(f"alias {alias},balance= {balance} amount= {amount}")
        if balance == None or balance < Decimal(amount):
            log_and_print(f"alias {alias},swap_eth_to_mint balance= {balance} amount= {amount} too less balance skipped")
            excel_manager.update_info(alias, f"too less balance->{balance} amount = {amount} skipped","swap_eth_to_mint")
            return
        __contract_addr = Web3.to_checksum_address("0xcb95f07b1f60868618752ceabbe4e52a1f564336")
        MethodID="0x9a2ac6d5"
        param = self.encodeABI_depositETHTo()
        data = MethodID + param
        BALANCE_PRECISION = math.pow(10, 18)  # 主币精度，18位
        value = int(amount * BALANCE_PRECISION)  # 计算要发送的amount
        try:
            response = self.rpc.get_gas_price()
            if 'error' in response:
                raise Exception(f"get_gas_price Error: {response}")
            gasprice = int(response['result'], 16) * 2
            log_and_print(f"{alias} swap_eth_to_morph gasprice = {gasprice}")
            response = self.rpc.transfer(
                self.account, __contract_addr, value, self.gaslimit, gasprice, data=data)
            log_and_print(f"{alias} swap_eth_to_morph response = {response}")
            if 'error' in response:
                raise Exception(f" transfer Error: {response}")
            hasResult = response["result"]
            log_and_print(f"{alias} swap_bera_to_stgusdc.transfer successfully hash = {hasResult}")
            self.QueueForSwapFromEthtoMorph.append((alias, hasResult))

        except Exception as e:
            log_and_print(f"{alias} swap_eth_to_morph failed: {e}")
            excel_manager.update_info(alias, f" {e}", "swap_eth_to_morph")


    def check_transaction_status(self, tx_hash, timeout=300, interval=10,type = 0):
        """type = 0 代表sepolia  1代表mintchain"""
        """检查交易的状态，返回是否确认和交易状态。使用计数器实现超时。"""
        max_attempts = timeout // interval  # 计算最大尝试次数
        attempts = 0  # 初始化尝试次数计数器

        while attempts < max_attempts:  # 循环直到达到最大尝试次数
            try:
                if type == 0:
                    receipt = self.web3ForSepolia.eth.get_transaction_receipt(tx_hash)                
                else:
                    receipt = self.web3ForMintChain.eth.get_transaction_receipt(tx_hash)                
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
    excel_manager = excelWorker("MintChainSwapGM", log_and_print)
    app = MintChainSwapGM()

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
        time.sleep(3)
        log_and_print(f"statring running by alias {alias}")
        private_key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        app.approve_action(alias, private_key)
        
    app.check_all_transaction_for_Approve()
    app.batch_swap_usdt_to_morph()
    app.check_all_transaction_for_SwapFromUSDTtoMorph()
    excel_manager.save_msg_and_stop_service()
