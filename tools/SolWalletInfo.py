import os
import sys
import datetime
from decimal import Decimal
from solathon import Client, PublicKey, Keypair
import base58

# 假设你的工具目录结构与之前类似
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)
from tools.UserInfo import UserInfo  # 这里假设你有相应的用户信息处理模块
from tools.excelWorker import excelWorker  # 同上，假设你有处理Excel的模块

def log_and_print(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - {text}")

class SolanaWalletInfo:
    def __init__(self, rpc_url):
        self.client = Client(rpc_url)

    def get_balance(self, address):
        balance_lamports = self.client.get_balance(address)
        balance_sol = Decimal(balance_lamports) / 1000000000  # 1 SOL = 1 billion Lamports
        return balance_sol


if __name__ == "__main__":
    solana_rpc_url = "https://api.mainnet-beta.solana.com"  # 主网RPC地址
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("wallet", log_and_print)
    alias_list = UserInfoApp.find_alias_by_path()

    # 收集地址信息
    for alias in alias_list:
        key = UserInfoApp.find_solinfo_by_alias_in_file(alias)  # 假设这个方法返回Base58编码的私钥
        decoded_key = base58.b58decode(key)

        # 检查 decoded_key 是否为元组，如果是，则取第一个元素
        if isinstance(decoded_key, tuple):
            decoded_key = decoded_key[0]
        
        # 使用解码后的私钥创建 Keypair
        keypair = Keypair.from_private_key(decoded_key)
        address = str(keypair.public_key)  # 从 Keypair 获取公钥（地址）
        excel_manager.update_info(alias, address, "address")

    sol_app = SolanaWalletInfo(solana_rpc_url)
    for alias in alias_list:
        key = UserInfoApp.find_solinfo_by_alias_in_file(alias)  # 假设这个方法返回Base58编码的私钥
        decoded_key = base58.b58decode(key)

        # 检查 decoded_key 是否为元组，如果是，则取第一个元素
        if isinstance(decoded_key, tuple):
            decoded_key = decoded_key[0]
        
        # 使用解码后的私钥创建 Keypair
        keypair = Keypair.from_private_key(decoded_key)
        address = str(keypair.public_key)  # 从 Keypair 获取公钥（地址）
        balance = sol_app.get_balance(address)  # 查询余额
        log_and_print(f"{alias} SOL_balance {balance}")
        excel_manager.update_info(alias, str(balance), "SOL_balance")
                
    excel_manager.save_msg_and_stop_service()
