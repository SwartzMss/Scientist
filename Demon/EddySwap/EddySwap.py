
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
from dotenv import load_dotenv
load_dotenv()

class Dapp:
    def __init__(self, account, rpc):
        self.account = account
        self.rpc = rpc
        self.gaslimit = 200000
# SWAP
    def SWAP_ZETA_MATIC(self):
        """SWAP_ZETA_MATIC"""
        __contract_addr = '0x2ca7d64A7EFE2D62A725E2B35Cf7230D6677FfEe'  # 合约地址
        MethodID="0x7ff36ab5"
        param_1="0000000000000000000000000000000000000000000000000000000000000000"
        param_2="0000000000000000000000000000000000000000000000000000000000000080"
        param_3="000000000000000000000000"+self.account.address.strip('0x')#地址
        param_4="0000000000000000000000000000000000000000000000000000000065a8bfa9"
        param_5="0000000000000000000000000000000000000000000000000000000000000002"
        param_6="0000000000000000000000005f0b1a82749cb4e2278ec87f8bf6b618dc71a8bf"
        param_7="00000000000000000000000078b3e25e43bbf6d87cf7f3445debd1a35230ce67"


        data = MethodID+param_1+param_2+param_3+param_4+param_5+param_6+param_7
        value = 0.5 #转账的数量
        BALANCE_PRECISION = math.pow(10, 18)  # 主币精度，18位
        amount = int(value * BALANCE_PRECISION)  # 计算要发送的amount
        res = self.rpc.transfer(
            self.account, __contract_addr, amount, self.gaslimit, data=data)
        return res

# 余额查询
    def bsc_get_balance(self):
        """获取余额"""
        res = self.rpc.get_balance(self.account.address)
        return (int(res['result'], 16)) / math.pow(10,18) #需要除以10的18次方

    def run(self):
        bsc_get_balance = self.bsc_get_balance()
        print(f"balance:{bsc_get_balance}")

        try:
            print("SWAP")
            SWAP_ZETA_MATIC = self.SWAP_ZETA_MATIC()
            print(f"SWAP:{SWAP_ZETA_MATIC}")
            pass
        except Exception as e:
            print(f"SWAP: {e}")
            return


if __name__ == '__main__':
    proxy_list = ['http://127.0.0.1:7890']
    proxies = {'http': random.choice(proxy_list),
               'https': random.choice(proxy_list)}
    session = requests.Session()
    session.proxies = proxies
    rpc=Rpc("https://zetachain-athens-evm.blockpi.network/v1/rpc/public", chainid=7001,proxies=proxies)
    privkey='0x00' #可以直接把私钥放这里
    account = web3.Account.from_key(privkey)
    address = account.address
    
    life = Dapp(account, rpc)
    app = life.run()
