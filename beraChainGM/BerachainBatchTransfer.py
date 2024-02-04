import requests
from web3 import Web3
from eth_account.messages import encode_defunct
import time
import math
import sys
import web3
import requests
import random
import datetime
import json
import os
# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# 现在可以从tools目录导入Rpc
from tools.rpc import Rpc


class BerachainBatchTransfer:
    def __init__(self, private_key, rpc_url='https://artio.rpc.berachain.com', chain_id=80085):
        self.rpc = Rpc(rpc=rpc_url, chainid=chain_id)
        self.private_key = private_key
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.web3.eth.account.from_key(private_key) 
        self.chain_id = chain_id

    def get_nonce(self):
        """获取当前账户的交易数，以确定nonce."""
        return self.rpc.get_transaction_nonce(self.account.address)['result']

    def get_balance(self):
        """获取指定地址的BERA余额."""
        balance_result = self.rpc.get_balance(self.account.address)
        balance_wei = int(balance_result['result'], 16)
        balance_bera = self.web3.from_wei(balance_wei, 'ether')
        return balance_bera

    def send_transaction(self, value):
        '''发送单个转账'''
        nonce = int(self.get_nonce(), 16)
        BALANCE_PRECISION = math.pow(10, 18)  # 主币精度，18位
        amount = int(value * BALANCE_PRECISION)  # 计算要发送的amount
        # 准备交易数据
        tx_data = {
            'nonce': Web3.to_hex(nonce),
            'chainId': self.chain_id,
            'to': '0xcab666f5c024bb15f7f1f743e4c28423d2aaf3a2',
            'value':  Web3.to_hex(Web3.to_wei(value, 'ether')),
            'gas': Web3.to_hex(21000),
            'gasPrice': Web3.to_hex(self.web3.to_wei('5', 'gwei'))
        }

        # 签名交易
        signed_tx = self.account.sign_transaction(tx_data)
        
        # 发送交易并返回交易哈希
        tx_hash = self.rpc.send_raw_transaction(signed_tx.rawTransaction.hex())['result']
        return tx_hash

    def check_transaction_status(self, tx_hash):
        """检查交易的状态"""
        receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        # 在某些Web3库版本中，状态为布尔值。在其他版本中，状态为十六进制数。
        if receipt is not None:
            # 成功的交易状态为1，失败的为0
            return receipt.status == 1
        else:
            # 如果没有找到收据，交易可能还在挂起状态
            return False

# if __name__ == "__main__":
#     private_key = "xx"
#     bera_transfer = BerachainBatchTransfer(private_key=private_key)
#     nonce = bera_transfer.get_nonce()
#     balance = bera_transfer.get_balance()
#     print(f"nonce = {nonce} balance = {balance}")
#     sys.exit()
#     tx_hash = bera_transfer.send_transaction(0.08)
#     print(f"交易哈希: {tx_hash}")
#     is_success = bera_transfer.check_transaction_status(tx_hash)
#     if is_success:
#         print("交易成功！")
#     else:
#         print("交易失败或仍在挂起状态。")