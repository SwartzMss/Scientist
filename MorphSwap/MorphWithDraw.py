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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\MorphWithDrawGM_{current_time}.log'

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')



class MorphWithDrawForMorp:
    def __init__(self, ):
        self.rpcForSepolia = Rpc(rpc="https://eth-sepolia-public.unifra.io", chainid=11155111, logger = log_and_print)
        self.web3ForSepolia = Web3(Web3.HTTPProvider("https://eth-sepolia-public.unifra.io"))
        self.rpcForMorphTest = Rpc(rpc="https://rpc-testnet.morphl2.io", chainid=2710, logger = log_and_print)
        self.web3ForMorphTest = Web3(Web3.HTTPProvider("https://rpc-testnet.morphl2.io"))
        self.account = None
        self.QueueForwithdrawTo = []
        self.QueueForproveWithdrawalTransaction = []
        self.QueueForproveWithdrawalTransactionResult = []
        self.QueueForfinalizeWithdrawalTransaction = []
        self.QueueForfinalizeWithdrawalTransactionResult = []
        self.headers = {
            'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 116)}.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
        }

    def get_MorphTest_eth_balance(self):
        balance_result = self.rpcForMorphTest.get_balance(self.account.address)
        if balance_result == None:
            return None
        balance_wei = int(balance_result['result'], 16)
        balance_bera = self.web3ForSepolia.from_wei(balance_wei, 'ether')
        return Decimal(balance_bera)

    def encodeABI_withdrawTo(self,amount):
        amount = Web3.to_wei(amount, 'ether')
        encoded_data = encode(
            ["address", "address", "uint256","uint32","bytes"],
            [Web3.to_checksum_address("0xdeaddeaddeaddeaddeaddeaddeaddeaddead0000"), self.account.address,amount,0, b'']
        )
        encoded_data_hex = encoded_data.hex()
        log_and_print(f"encodeABI_withdrawTo  = {encoded_data_hex}")
        return encoded_data_hex

    def check_transaction_status(self, tx_hash, timeout=300, interval=10,type = 0):
        """type = 0 代表sepolia  1代表morpthTest"""
        """检查交易的状态，返回是否确认和交易状态。使用计数器实现超时。"""
        max_attempts = timeout // interval  # 计算最大尝试次数
        attempts = 0  # 初始化尝试次数计数器

        while attempts < max_attempts:  # 循环直到达到最大尝试次数
            try:
                if type == 0:
                    receipt = self.web3ForSepolia.eth.get_transaction_receipt(tx_hash)                
                else:
                    receipt = self.web3ForMorphTest.eth.get_transaction_receipt(tx_hash)                
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

    def withdrawTo_action(self,alias, private_key):
        self.account = self.web3ForMorphTest.eth.account.from_key(private_key) 
        balance = self.get_MorphTest_eth_balance()
        log_and_print(f"alias {alias}, MorphTest_eth balance= {balance}")

        if balance is None or balance < Decimal('0.1'):
            log_and_print(f"alias {alias}, balance too low, operation skipped")
            excel_manager.update_info(alias, f"too less MorphTest_eth balance->{balance} skipped", "withdrawTo_action")
            return
        else:
            amount = round(balance / Decimal('10.0'), 3)
            log_and_print(f"alias {alias}, amount= {amount} MorphTest_eth balance= {balance}")
            # 进行其他相关的操作
        __contract_addr = Web3.to_checksum_address("0x4200000000000000000000000000000000000010")
        param = self.encodeABI_withdrawTo(amount)
        MethodID="0xa3a79548" 
        try:
            data = MethodID + param
            response = self.rpcForMorphTest.get_gas_price()
            if 'error' in response:
                raise Exception(f"get_gas_price Error: {response}")
            gasprice = int(response['result'], 16) * 2
            log_and_print(f"{alias} withdrawTo_action gasprice = {gasprice}")
            response = self.rpcForMorphTest.transfer(
                self.account, __contract_addr, 0, gasprice, data=data)
            log_and_print(f"{alias} withdrawTo_action response = {response}")
            if 'error' in response:
                raise Exception(f"transfer Error: {response}")
            hasResult = response["result"]
            log_and_print(f"{alias} withdrawTo_action successfully hash = {hasResult}")
            self.QueueForwithdrawTo.append((alias, private_key, hasResult, amount))
        except Exception as e:
            log_and_print(f"{alias} withdrawTo_action failed: {e}")
            excel_manager.update_info(alias, f" {e}", "withdrawTo_action")


    def check_all_transaction_for_withdrawTo(self):
        for alias, private_key, tx_hash,amount in self.QueueForwithdrawTo:
            log_and_print(f"{alias} start checking transaction status for withdrawTo")
            code,msg = self.check_transaction_status(tx_hash,type = 1)
            log_and_print(f"{alias} withdrawTo tx_hash = {tx_hash} code = {code} msg = {msg}")
            excel_manager.update_info(alias, f"tx_hash = {tx_hash} code = {code} msg = {msg}","withdrawTo")
            if code != True:
                continue
            self.QueueForproveWithdrawalTransaction.append((alias, private_key,amount))
        self.QueueForwithdrawTo.clear()

    def check_all_transaction_for_proveWithdrawalTransaction(self):
        for alias, private_key, tx_hash,amount in self.QueueForproveWithdrawalTransactionResult:
            log_and_print(f"{alias} start checking transaction status for QueueForproveWithdrawalTransactionResult")
            code,msg = self.check_transaction_status(tx_hash,type = 0)
            log_and_print(f"{alias} QueueForproveWithdrawalTransactionResult tx_hash = {tx_hash} code = {code} msg = {msg}")
            excel_manager.update_info(alias, f"tx_hash = {tx_hash} code = {code} msg = {msg}","QueueForproveWithdrawalTransactionResult")
            if code != True:
                continue
            self.QueueForfinalizeWithdrawalTransaction.append((alias, private_key,amount))
        self.QueueForproveWithdrawalTransactionResult.clear()

    def check_all_transaction_for_finalizeWithdrawalTransactionResult(self):
        for alias, private_key, tx_hash,amount in self.QueueForfinalizeWithdrawalTransactionResult:
            log_and_print(f"{alias} start checking transaction status for QueueForfinalizeWithdrawalTransactionResult")
            code,msg = self.check_transaction_status(tx_hash,type = 0)
            log_and_print(f"{alias} QueueForfinalizeWithdrawalTransactionResult tx_hash = {tx_hash} code = {code} msg = {msg}")
            excel_manager.update_info(alias, f"tx_hash = {tx_hash} code = {code} msg = {msg}","QueueForfinalizeWithdrawalTransactionResult")
        self.QueueForfinalizeWithdrawalTransactionResult.clear()


if __name__ == "__main__":
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("MorphWithDrawGM", log_and_print)
    app = MorphWithDrawForMorp()

    alais_list = UserInfoApp.find_alias_by_path()
    for alias in alais_list:
        time.sleep(3)
        log_and_print(f"statring running by alias {alias}")
        private_key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        #private_key = "0x3ac2a9da02016f712051c87732e21cc7bf72fd18416b3d2a79fcb065bcea742c"
        app.withdrawTo_action(alias, private_key)
        
    app.check_all_transaction_for_withdrawTo()
    # app.batch_proveWithdrawalTransaction()
    # app.check_all_transaction_for_proveWithdrawalTransaction()
    excel_manager.save_msg_and_stop_service()