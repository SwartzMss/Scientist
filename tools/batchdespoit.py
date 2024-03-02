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
# 现在可以从tools目录导入Rpc
from tools.rpc import Rpc

def log_and_print(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - {text}")

#BNB https://bsc-dataseed.binance.org/ 56
#openbnb https://opbnb-mainnet-rpc.bnbchain.org 204
#matic https://rpc-mainnet.maticvigil.com 137
class BatchDeposit:
    def __init__(self, private_key, rpc_url='https://rpc-mainnet.maticvigil.com', chain_id=137):
        self.rpc = Rpc(rpc=rpc_url, chainid=chain_id)
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.web3.eth.account.from_key(private_key)
        self.chain_id = chain_id

    def get_balance(self, to_address):
        balance_result = self.rpc.get_balance(to_address)
        if balance_result == None:
            return None
        balance_wei = int(balance_result['result'], 16)
        balance_bera = self.web3.from_wei(balance_wei, 'ether')
        return Decimal(balance_bera)

    def get_nonce(self):
        """获取当前账户的交易数，以确定nonce."""
        return self.rpc.get_transaction_nonce(self.account.address)['result']

    def get_gas_price(self):
        return self.rpc.get_gas_price()['result']

    def send_transaction_from_swartz(self, swartz_key, to_address, value):
        '''使用Swartz账户发送单个转账'''
        nonce = int(self.get_nonce(), 16)
        gas_price = int(self.get_gas_price(),16)
        tx_data = {
            'nonce': Web3.to_hex(nonce),
            'chainId': self.chain_id,
            'to': Web3.to_checksum_address(to_address),
            'value':  Web3.to_wei(value, 'ether'),
            'gas': Web3.to_hex(21000),
            'gasPrice': Web3.to_hex(self.web3.to_wei(gas_price, 'wei'))
        }
        signed_tx = self.account.sign_transaction(tx_data)
        data = self.rpc.send_raw_transaction(signed_tx.rawTransaction.hex())
        if data == None or 'error' in data:
            return None
        tx_hash = data['result']
        return tx_hash

    def check_transaction_status(self, tx_hash):
        """检查交易的状态"""
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            if receipt is not None:
                return receipt.status == 1  # 交易成功
            else:
                return False  # 交易收据未找到，可能还在挂起状态
        except TimeExhausted:
            log_and_print("Transaction receipt request timed out.")
            return False  # 超时时返回False
        except Exception as e:
            log_and_print(f"An error occurred: {e}")
            return False  # 处理其他可能的异常

if __name__ == "__main__":
    swartz_key = "xx"
    # 初始化UserInfoApp等
    UserInfoApp = UserInfo(log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_eth("swartz")

    for credentials in credentials_list:
        time.sleep(5)
        alias = credentials["alias"]
        key = credentials["key"]
        account = web3.Account.from_key(key)    
        # 这里假设每个用户都要接收固定金额的转账
        app = BatchDeposit(private_key=swartz_key)
        gas_price = app.get_gas_price()
        log_and_print(f"alias {alias}, gas_price: {gas_price}")
        balance = app.get_balance(account.address)
        log_and_print(f"alias {alias}, balance: {balance}")
        if balance == None or balance >= Decimal("0.4"):
            continue
        # 使用Swartz账户向每个用户发送转账
        tx_hash = app.send_transaction_from_swartz(swartz_key, account.address, 0.4)
        log_and_print(f"alias {alias}, 交易哈希: {tx_hash}")
        time.sleep(10)  # 控制请求速度
        is_success = app.check_transaction_status(tx_hash)
        if is_success:
            print("交易成功！")
        else:
            print("交易失败或仍在挂起状态。")
