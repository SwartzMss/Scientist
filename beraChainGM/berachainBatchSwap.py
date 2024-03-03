import requests
from web3 import Web3
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
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.web3.eth.account.from_key(private_key) 
        self.headers = {
            'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 116)}.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',

        }

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

    def encode_swap_data(self,  batch_swap_steps, deadline = 99999999, swap_kind = 0):
        tolerance_slippage = 0.02
        swap_steps_encoded = [
            (
                Web3.to_checksum_address(step["poolId"]),
                Web3.to_checksum_address("0x0000000000000000000000000000000000000000") if index == 0 else Web3.to_checksum_address(step["assetIn"]),
                step["amountIn"],
                Web3.to_checksum_address(step["assetOut"]),
                0 if index < len(batch_swap_steps) - 1 else int(step["amountOut"] * (1 - tolerance_slippage)),  # 在最后一个步骤应用2%的滑点
                step["userData"]
            )
            for index, step in enumerate(batch_swap_steps)
        ]

        encoded_data = encode(
            ["uint8", "(address,address,uint256,address,uint256,bytes)[]", "uint256"],
            [swap_kind, swap_steps_encoded, deadline]
        )
        encoded_data_hex = encoded_data.hex()
        log_and_print(f"encoded_data_hex = {encoded_data_hex}")
        return encoded_data_hex

    def get_balance(self):
        balance_result = self.rpc.get_balance(self.account.address)
        if balance_result == None:
            return None
        balance_wei = int(balance_result['result'], 16)
        balance_bera = self.web3.from_wei(balance_wei, 'ether')
        return Decimal(balance_bera)

    def parse_swap_steps_from_json(self, json_str):
        log_and_print(f"json_str = {json_str}")
        # 从解析后的数据中构造batch_swap_steps列表
        batch_swap_steps = [
            {
                "poolId": step["pool"],
                "assetIn": step["assetIn"],
                "amountIn": int(step["amountIn"]),
                "assetOut": step["assetOut"],
                "amountOut": int(step["amountOut"]),
                "userData": b""  # 假设userData始终为空
            }
            for step in json_str.get("steps", [])  # 使用get以避免KeyError，如果没有"steps"则默认为空列表
        ]

        return batch_swap_steps

    def ge_response_for_swap_bera_to_stgusdc(self, amount):
        amountValue =  Web3.to_wei(amount, 'ether')
        session = requests.Session()
        url = f"https://artio-80085-dex-router.berachain.com/dex/route?quoteAsset=0x6581e59A1C8dA66eD0D313a0d4029DcE2F746Cc5&baseAsset=0x5806E416dA447b267cEA759358cF22Cc41FAE80F&amount={amountValue}&swap_type=given_in"
        response = session.get(url, headers=self.headers, timeout=60)
        return response

    def swap_bera_to_stgusdc(self, amount = 0.1):
        try:
            response = self.ge_response_for_swap_bera_to_stgusdc(amount)
            if response.status_code != 200:
                raise Exception(f" Error: {response.status_code }")
            log_and_print(f"{alias} ge_response_for_swap_bera_to_stgusdc successfully")
        except Exception as e:
            log_and_print(f"{alias} ge_response_for_swap_bera_to_stgusdc failed: {e}")
            excel_manager.update_info(alias, f" ge_response_for_swap_bera_to_stgusdc failed: {e}")
            return False 

        try:
            data = response.json()
            batch_swap_steps = self.parse_swap_steps_from_json(data)
            param = self.encode_swap_data(batch_swap_steps)
            log_and_print(f"{alias} encode_swap_data successfully")
        except Exception as e:
            log_and_print(f"{alias} encode_swap_data failed: {e}")
            excel_manager.update_info(alias, f" encode_swap_data failed: {e}")
            return False 
        
        __contract_addr = "0x0d5862FDbdd12490f9b4De54c236cff63B038074"
        MethodID="0xe3414c00" 
        data = MethodID + param
        BALANCE_PRECISION = math.pow(10, 18)  # 主币精度，18位
        value = int(amount * BALANCE_PRECISION)  # 计算要发送的amount
        try:
            response = self.rpc.transfer(
                self.account, __contract_addr, value, 50000, data=data)
            if 'error' in response:
                raise Exception(f"Error: {response}")
            hasResult = response["result"]
            log_and_print(f"{alias} swap_bera_to_stgusdc.transfer successfully hash = {hasResult}")
        except Exception as e:
            log_and_print(f"{alias} swap_bera_to_stgusdc.transfer failed: {e}")
            excel_manager.update_info(alias, f" swap_bera_to_stgusdc.transfer failed: {e}")
            return False 
        return True

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
        bera_swap = BerachainBatchSwap(private_key=key)
        balance = bera_swap.get_balance()
        log_and_print(f"alias {alias}, balance: {balance}")
        time.sleep(5)
        if balance == None or balance <= Decimal("0.2"):
            log_and_print(f"alias {alias}, too less balance skipped")
            time.sleep(5)
            continue
        tx_hash = bera_swap.swap_bera_to_stgusdc()
        log_and_print(f"alias {alias}, 交易哈希: {tx_hash}")
        time.sleep(5)
        # is_success = bera_transfer.check_transaction_status(tx_hash)
        # if is_success:
        #     print("交易成功！")
        # else:
        #     print("交易失败或仍在挂起状态。")
