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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\OptopiaSwap_{current_time}.log'

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


62049

class OptopiaSwap:
    def __init__(self):
        self.alias = None
        self.rpcForSepolia = Rpc(rpc="https://eth-sepolia-public.unifra.io", chainid=11155111, logger = log_and_print)
        self.gaslimitForSepolia = 1500000
        self.web3ForSepolia = Web3(Web3.HTTPProvider("https://eth-sepolia-public.unifra.io"))
        self.rpcForOptopia = Rpc(rpc="https://rpc-testnet.optopia.ai", chainid=62049, logger = log_and_print)
        self.gaslimitForOptopia = 300000
        self.web3ForOptopia = Web3(Web3.HTTPProvider("https://rpc-testnet.optopia.ai"))
        self.account = None
        self.QueueForSwapFromEthtoOptopia = []
        self.QueueForSwapFromOptopiatoEth = []
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
        balance_bera = self.web3ForSepolia.from_wei(balance_wei, 'ether')
        return Decimal(balance_bera)

    def get_Optopia_balance(self):
        balance_result = self.rpcForOptopia.get_balance(self.account.address)
        if balance_result == None:
            return None
        balance_wei = int(balance_result['result'], 16)
        balance_bera = self.web3ForOptopia.from_wei(balance_wei, 'ether')
        return Decimal(balance_bera)


    def swap_optopia_to_eth(self, alias, private_key):
        self.account = self.web3ForOptopia.eth.account.from_key(private_key) 
        balance = self.get_Optopia_balance()
        log_and_print(f"alias {alias}, Optopia_eth balance= {balance}")

        if balance is None or balance < Decimal('0.01'):
            log_and_print(f"alias {alias}, balance too low, operation skipped")
            excel_manager.update_info(alias, f"too less Optopia_eth balance->{balance} skipped", "swap_optopia_to_eth")
            return
        else:
            amount = float(round(balance / Decimal('10.0'), 3)) 
            log_and_print(f"alias {alias}, amount= {amount} Optopia_eth balance= {balance}")

        BALANCE_PRECISION = math.pow(10, 18)  # 主币精度，18位
        value = int(amount * BALANCE_PRECISION)  # 计算要发送的amount
        hex_value = hex(value)[2:]
        __contract_addr = Web3.to_checksum_address("0x4200000000000000000000000000000000000010")
        MethodID="0x32b7006d"
        param_1="000000000000000000000000deaddeaddeaddeaddeaddeaddeaddeaddead0000"
        param_2= hex_value.zfill(64)
        param_3="0000000000000000000000000000000000000000000000000000000000000000"
        param_4="0000000000000000000000000000000000000000000000000000000000000080"
        param_5="0000000000000000000000000000000000000000000000000000000000000000"
        data = MethodID + param_1 + param_2 + param_3 + param_4 + param_5
        try:
            response = self.rpcForOptopia.get_gas_price()
            if 'error' in response:
                raise Exception(f"get_gas_price Error: {response}")
            gasprice = int(response['result'], 16) * 2
            log_and_print(f"{alias} swap_optopia_to_eth gasprice = {gasprice}")
            response = self.rpcForOptopia.transfer(
                self.account, __contract_addr, value, self.gaslimitForOptopia, gasprice, data=data)
            log_and_print(f"{alias} swap_optopia_to_eth response = {response}")
            if 'error' in response:
                raise Exception(f" transfer Error: {response}")
            hasResult = response["result"]
            log_and_print(f"{alias} swap_optopia_to_eth.transfer successfully hash = {hasResult}")
            self.QueueForSwapFromOptopiatoEth.append((alias, hasResult))

        except Exception as e:
            log_and_print(f"{alias} swap_optopia_to_eth failed: {e}")
            excel_manager.update_info(alias, f" {e}", "swap_optopia_to_eth")

    def swap_eth_to_optopia(self, alias, private_key):
        amount = round(random.uniform(0.001, 0.009), 3)
        self.account = self.web3ForSepolia.eth.account.from_key(private_key) 
        balance = self.get_eth_balance()
        log_and_print(f"alias {alias},balance= {balance} amount= {amount}")
        if balance == None or balance < Decimal(amount):
            log_and_print(f"alias {alias},swap_eth_to_optopia balance= {balance} amount= {amount} too less balance skipped")
            excel_manager.update_info(alias, f"too less balance->{balance} amount = {amount} skipped","swap_eth_to_optopia")
            return
        __contract_addr = Web3.to_checksum_address("0x4e8059f4Df6174a5a88376E4AA959B9E7f36F2c3")
        MethodID="0xb1a1a882"
        param_1="0000000000000000000000000000000000000000000000000000000000030d40"
        param_2="0000000000000000000000000000000000000000000000000000000000000040"
        param_3="0000000000000000000000000000000000000000000000000000000000000000"
        data = MethodID + param_1 + param_2 + param_3
        BALANCE_PRECISION = math.pow(10, 18)  # 主币精度，18位
        value = int(amount * BALANCE_PRECISION)  # 计算要发送的amount
        try:
            response = self.rpcForSepolia.get_gas_price()
            if 'error' in response:
                raise Exception(f"get_gas_price Error: {response}")
            gasprice = int(response['result'], 16) * 2
            log_and_print(f"{alias} swap_eth_to_optopia gasprice = {gasprice}")
            response = self.rpcForSepolia.transfer(
                self.account, __contract_addr, value, self.gaslimitForSepolia, gasprice, data=data)
            log_and_print(f"{alias} swap_eth_to_optopia response = {response}")
            if 'error' in response:
                raise Exception(f" transfer Error: {response}")
            hasResult = response["result"]
            log_and_print(f"{alias} swap_eth_to_optopia.transfer successfully hash = {hasResult}")
            self.QueueForSwapFromEthtoOptopia.append((alias, hasResult))

        except Exception as e:
            log_and_print(f"{alias} swap_optopia_to_eth failed: {e}")
            excel_manager.update_info(alias, f" {e}", "swap_optopia_to_eth")


    def check_all_transaction_for_SwapFromOptopiatoEth(self):
        for alias, tx_hash in self.QueueForSwapFromOptopiatoEth:
            log_and_print(f"{alias} start checking transaction status for swap_optopia_to_eth")
            code,msg = self.check_transaction_statusForOptopia(tx_hash)
            log_and_print(f"{alias} swap_optopia_to_eth tx_hash = {tx_hash} code = {code} msg = {msg}")
            excel_manager.update_info(alias, f"tx_hash = {tx_hash} code = {code} msg = {msg}", "swap_optopia_to_eth")
        self.QueueForSwapFromOptopiatoEth.clear()

    def check_transaction_statusForOptopia(self, tx_hash, timeout=300, interval=5):
        """检查交易的状态，返回是否确认和交易状态。使用计数器实现超时。"""
        max_attempts = timeout // interval  # 计算最大尝试次数
        attempts = 0  # 初始化尝试次数计数器

        while attempts < max_attempts:  # 循环直到达到最大尝试次数
            try:
                receipt = self.web3ForOptopia.eth.get_transaction_receipt(tx_hash)                
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

    def check_all_transaction_for_SwapFromEthtoOptopia(self):
        for alias, tx_hash in self.QueueForSwapFromEthtoOptopia:
            log_and_print(f"{alias} start checking transaction status for swap_eth_to_optopia")
            code,msg = self.check_transaction_statusForSepolia(tx_hash)
            log_and_print(f"{alias} swap_eth_to_optopia tx_hash = {tx_hash} code = {code} msg = {msg}")
            excel_manager.update_info(alias, f"tx_hash = {tx_hash} code = {code} msg = {msg}", "swap_eth_to_optopia")
        self.QueueForSwapFromEthtoOptopia.clear()

    def check_transaction_statusForSepolia(self, tx_hash, timeout=300, interval=5):
        """检查交易的状态，返回是否确认和交易状态。使用计数器实现超时。"""
        max_attempts = timeout // interval  # 计算最大尝试次数
        attempts = 0  # 初始化尝试次数计数器

        while attempts < max_attempts:  # 循环直到达到最大尝试次数
            try:
                receipt = self.web3ForSepolia.eth.get_transaction_receipt(tx_hash)                
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
    excel_manager = excelWorker("OptopiaSwap", log_and_print)
    app = OptopiaSwap()


    alais_list = UserInfoApp.find_alias_by_path()
    for alias in alais_list:
        log_and_print(f"statring running by alias {alias}")
        private_key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        app.swap_eth_to_optopia(alias, private_key)
        time.sleep(3)
    app.check_all_transaction_for_SwapFromEthtoOptopia()

    alais_list = UserInfoApp.find_alias_by_path()
    for alias in alais_list:
        log_and_print(f"statring running by alias {alias}")
        private_key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        app.swap_eth_to_optopia(alias, private_key)
        time.sleep(3)
    app.check_all_transaction_for_SwapFromEthtoOptopia()

    excel_manager.save_msg_and_stop_service()
