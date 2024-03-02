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

from enum import Enum
from typing import List, Tuple, NamedTuple, Union
from dataclasses import dataclass

import os
# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)
from tools.UserInfo import UserInfo
# 现在可以从tools目录导入Rpc
from tools.rpc import Rpc
def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    print(message)

class BerachainBatchSwap:
    def __init__(self, private_key, rpc_url='https://artio.rpc.berachain.com', chain_id=80085):
        self.rpc = Rpc(rpc=rpc_url, chainid=chain_id)
        self.private_key = private_key
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.web3.eth.account.from_key(private_key) 
        self.chain_id = chain_id

    def encode_swap_data(self, json_data):
        class SwapKind(Enum):
            GIVEN_IN = 0
            GIVEN_OUT = 1

        @dataclass
        class BatchSwapStep:
            poolId: types.ChecksumAddress  # 使用ChecksumAddress类型来表示地址
            assetIn: types.ChecksumAddress
            amountIn: int  # uint256在Python中可以用int表示，因为Python的int是无限精度的
            assetOut: types.ChecksumAddress
            amountOut: int
            userData: bytes  # Solidity的bytes类型在Python中用bytes表示

        # 这个元组类型表示了你描述的整体结构
        SwapDefinition = Tuple[SwapKind, List[BatchSwapStep], int]
            # 转换十六进制字符串为字节串
            data_bytes = Web3.to_bytes(hexstr=data_hex)
            signatureinfo_bytes = Web3.to_bytes(hexstr=signatureinfo_hex)
    
        # 定义参数值和它们的类型
        values = [
            deadline,  # deadline, uint256
            voyageId,  # voyageId, uint256
            destinations,  # destinations, uint16[]
            data_bytes,  # data, bytes32
            signatureinfo_bytes  # signatureinfo, bytes
        ]
        types = ['uint256', 'uint256', 'uint16[]', 'bytes32', 'bytes']
        
        # 使用eth_abi进行编码
        encoded_data = encode(types, values)
        
        # 返回编码后的十六进制字符串
        return encoded_data.hex()

    def get_balance(self):
        """获取指定地址的BERA余额."""
        balance_result = self.rpc.get_balance(self.account.address)
        if balance_result == None:
            return None
        balance_wei = int(balance_result['result'], 16)
        balance_bera = self.web3.from_wei(balance_wei, 'ether')
        return Decimal(balance_bera)

    def swap_bera_to_stgusdc(self):
        __contract_addr = "0x0d5862FDbdd12490f9b4De54c236cff63B038074"
        MethodID="0xe3414c00" 
        param_1="0000000000000000000000000000000000000000000000000000000000000000"
        param_2="0000000000000000000000000000000000000000000000000000000000000060"
        param_3="0000000000000000000000000000000000000000000000000000000005f5e0ff"
        param_4="0000000000000000000000000000000000000000000000000000000000000001"
        param_5="0000000000000000000000000000000000000000000000000000000000000020"
        param_6="000000000000000000000000a88572f08f79d28b8f864350f122c1cc0abb0d96"
        param_7="0000000000000000000000000000000000000000000000000000000000000000"
        param_8="000000000000000000000000000000000000000000000000016345785d8a0000"
        param_9="0000000000000000000000007eeca4205ff31f947edbd49195a7a88e6a91161b"
        param_10="000000000000000000000000000000000000000000000001a56b2fda1b140d3b"
        param_11="00000000000000000000000000000000000000000000000000000000000000c0"
        param_12="0000000000000000000000000000000000000000000000000000000000000000"


        data = MethodID+param_1+param_2+param_3+param_4+param_5+param_6+param_7+param_8+param_9+param_10+param_11+param_12
        value = 0.1 #转账的数量
        BALANCE_PRECISION = math.pow(10, 18)  # 主币精度，18位
        amount = int(value * BALANCE_PRECISION)  # 计算要发送的amount
        res = self.rpc.transfer(
            self.account, __contract_addr, amount, self.gaslimit, data=data)
        return res

    def check_transaction_status(self, tx_hash):
        """检查交易的状态"""
        receipt = self.web3.eth.get_transaction_receipt(tx_hash)
        # 在某些Web3库版本中，状态为布尔值。在其他版本中，状态为十六进制数。
        if receipt is not None:
            # 成功的交易状态为1，失败的为0
            return receipt.status == 1
        else:
            # 如果没有找到收据，交易可能还在挂起状态
            return False

if __name__ == "__main__":
    UserInfoApp = UserInfo(log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_eth("bearChainGM")

    for credentials in credentials_list:
        alias = credentials["alias"]
        key = credentials["key"]
        bera_transfer = BerachainBatchTransfer(private_key=key)
        balance = bera_transfer.get_balance()
        log_and_print(f"alias {alias}, balance: {balance}")
        time.sleep(5)
        if balance == None:
            continue
        continue # 这边只是check balance
        if balance <= Decimal("0.2"):
            log_and_print(f"alias {alias}, too less balance skipped")
            time.sleep(5)
            continue
        tx_hash = bera_transfer.send_transaction_to_swartz(balance - Decimal("0.01"))
        log_and_print(f"alias {alias}, 交易哈希: {tx_hash}")
        time.sleep(5)
        # is_success = bera_transfer.check_transaction_status(tx_hash)
        # if is_success:
        #     print("交易成功！")
        # else:
        #     print("交易失败或仍在挂起状态。")
