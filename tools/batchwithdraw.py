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
#capx https://rpc-zkevm.capx.fi/sequencer-api 7116
class batchwithdraw:
    def __init__(self, private_key, rpc_url='https://rpc-zkevm.capx.fi/sequencer-api', chain_id=7116):
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
        data = self.rpc.get_transaction_nonce(self.account.address)
        if data == None:
            return None
        return data['result']

    def get_gas_price(self):
        data = self.rpc.get_gas_price()
        if data == None:
            return None
        return data['result']

    def send_transaction_to_swartz(self):
        gas_price = int(self.get_gas_price(),16)
        log_and_print(f"alias {alias}, gas_price: {gas_price}")
        balance = self.get_balance(self.account.address)
        log_and_print(f"alias {alias}, balance: {balance}")
        estimated_gas_fee = 21000 * gas_price
        balance_wei = self.web3.to_wei(balance, 'ether')
        max_value_wei = balance_wei - estimated_gas_fee
        nonce = int(self.get_nonce(), 16)
        if max_value_wei > 0:
            value = self.web3.from_wei(max_value_wei, 'ether')  # 将余额转换回ether单位，如果需要的话
        else:
            log_and_print("余额不足以支付预计的gas费用。")
            return None
        tx_data = {
            'nonce': Web3.to_hex(nonce),
            'chainId': self.chain_id,
            'to': Web3.to_checksum_address("0x6a8525171200b11c676ba33ea1915af35b0116fe"),
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
    # 初始化UserInfoApp等
    UserInfoApp = UserInfo(log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_eth("swartz")

    for credentials in credentials_list:
        time.sleep(5)
        alias = credentials["alias"]
        key = credentials["key"]
        account = web3.Account.from_key(key)    
        # 这里假设每个用户都要接收固定金额的转账
        app = batchwithdraw(private_key=key)
        # 使用Swartz账户向每个用户发送转账
        tx_hash = app.send_transaction_to_swartz()
        if tx_hash == None:
            continue
        log_and_print(f"alias {alias}, 交易哈希: {tx_hash}")
        time.sleep(10)  # 控制请求速度
        is_success = app.check_transaction_status(tx_hash)
        if is_success:
            print("交易成功！")
        else:
            print("交易失败或仍在挂起状态。")
