
#https://app.eddy.finance/

from eth_account.messages import encode_defunct
import sys
import time
import math
import web3
import requests
import random
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)

# 将父目录的父目录添加到sys.path中
sys.path.append(grandparent_dir)
sys.path.append(parent_dir)

from tools.rpc import Rpc

erc20dex_contract_addr = '0x0d5862FDbdd12490f9b4De54c236cff63B038074'
c20dex_abi_json_file = "IERC20DexModule.abi.json"

class berachainBatchSwap:
    def __init__(self, account, rpc):
        self.account = account
        self.rpc = rpc
        self.gaslimit = 300000
        
    def get_nonce(self):
        """获取当前账户的交易数，以确定nonce."""
        return self.rpc.get_transaction_nonce(self.account.address)['result']

# 余额查询
    def get_balance(self):
        """获取余额"""
        res = self.rpc.get_balance(self.account.address)
        return (int(res['result'], 16)) / math.pow(10,18) #需要除以10的18次方


    def get_targetswitchTokenNum(self, num):
        """获取目标token的数量"""
        with open(c20dex_abi_json_file, 'r') as file:
            abi_content = json.load(file)
        get_preview_swap_function = web3.eth.contract(
            address=contract_addr,
            abi=abi_content  # 替换为合约 ABI
        ).functions.getPreviewSwapExact

        # 替换以下参数为实际参数
        get_preview_swap_input_data = get_preview_swap_function(
            kind,  # uint8 类型参数
            pool_id,  # address 类型参数
            asset_in,  # address 类型参数
            amount_in,  # uint256 类型参数
            asset_out,  # address 类型参数
        ).call()

        amount = get_preview_swap_input_data[1]

        print(f'兑换数量为：{amount / 1000000000000000000}')
        return amount

    def swap_action(self):
        """SWAP_ZETA_MATIC"""
        __contract_addr = erc20dex_contract_addr
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

    def run(self):
        balance = self.get_balance()
        print(f"balance:{balance}")
        nonce = self.get_nonce()
        print(f"get_nonce:{nonce}")
        #return
        try:
            print("SWAP")
            result = self.swap_action()
            print(f"SWAP:{result}")
            pass
        except Exception as e:
            print(f"SWAP: {e}")
            return


if __name__ == '__main__':
    session = requests.Session()
    rpc=Rpc(rpc='https://artio.rpc.berachain.com', chainid=80085)
    privkey='xxx' #可以直接把私钥放这里
    account = web3.Account.from_key(privkey)
    address = account.address
    
    life = berachainBatchSwap(account, rpc)
    app = life.run()
