
#https://www.intract.io

from eth_account.messages import encode_defunct
import time
import math
import sys
import web3
import requests
import random
import datetime
import json
from fake_useragent import UserAgent
import os
from dotenv import load_dotenv
load_dotenv()

# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# 现在可以从tools目录导入UserInfo
from tools.UserInfo import UserInfo
from tools.socket5SwitchProxy import socket5SwitchProxy
# 现在可以从tools目录导入excelWorker
from tools.excelWorker import excelWorker

# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\MintChainGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class MintChainGM:
    def __init__(self):
        self.alias = None
        self.account = None
        self.session = None
        self.headers = {
            'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 116)}.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'referer': 'https://www.mintchain.io/mint-forest',
            'origin': 'https://www.mintchain.io', 
        }

    def create_new_session(self,proxyinfo):
        ua = UserAgent()
        self.headers['user-agent'] = ua.random
        self.headers.pop('Authorization', None)
        self.session = requests.Session()
        self.session.cookies.clear()
        self.session.proxies = proxyinfo
    # 获取 nonce
    def calcNonce(self, e=1e6, t=9999999, r=None):
        # 处理参数逻辑，确定正确的 e 和 t 范围
        if r is not None and not isinstance(r, bool) and not n(e, t, r):  # `n` 函数的细节未知，需要自行实现
            t = None
            r = None

        if r is None:
            if isinstance(t, bool):
                r = t
                t = None
            elif isinstance(e, bool):
                r = e
                e = None

        if e is None and t is None:
            e = 0
            t = 1
        else:
            e = float(e) if e is not None else 0
            t = float(t) if t is not None else e
            if e > t:
                e, t = t, e

        # 生成随机数
        if r or e % 1 != 0 or t % 1 != 0:
            u = random.random()
            precision = len(str(u)) - 2  # 减去 '0.'
            return min(e + u * (t - e + float("1e-" + str(precision))), t)
        else:
            return random.randint(e, t)  # 假设 `l(e, t)` 等价于生成 [e, t] 范围内的随机整数

    def mint_forest_event(self):
        Nonce = self.calcNonce()
        return f"You are participating in the Mint Forest event: \n {self.account.address}\n\nNonce: {Nonce}"

    def _sign_message(self,msg):
        res = self.account.sign_message(encode_defunct(text=msg))
        return res.signature.hex()

    def post_login(self,msg, signature):
        url = f"https://www.mintchain.io/api/tree/login"

        payload = {
            "address":self.account.address,
            "message":msg,
            "signature":signature
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} post_login data:{data}")
        return data

    def get_totalUser(self):
        # run_or_not = random.randint(0, 1)  # 生成 0 或 1
        # if run_or_not == 0:
        #     return None
        url = f"https://www.mintchain.io/api/tree/total-user"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_totalUser data:{data}")
        return data


    def get_energylist(self):
        url = f"https://www.mintchain.io/api/tree/energy-list"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_energylist data:{data}")
        return data


    def get_merank(self):
        url = f"https://www.mintchain.io/api/tree/me-rank"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_merank data:{data}")
        return data


    def get_asset(self):
        url = f"https://www.mintchain.io/api/tree/asset"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_asset data:{data}")
        return data

    def get_leaderboard(self):
        url = f"https://www.mintchain.io/api/tree/leaderboard?page=1"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_leaderboard data:{data}")
        return data

    def get_activity(self):
        url = f"https://www.mintchain.io/api/tree/activity?page=1"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_activity data:{data}")
        return data

    def get_userinfo(self):
        url = f"https://www.mintchain.io/api/tree/user-info"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_userinfo data:{data}")
        return data

    def get_tasklist(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://www.mintchain.io/api/tree/task-list"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_tasklist data:{data}")
        return data


    def get_experiments(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://discord.com/api/v9/experiments"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_experiments data:{data}")
        return data

    def post_claim(self,amount = 500):
        url = f"https://www.mintchain.io/api/tree/claim"
        payload = {
            "amount":amount,
            "freeze": False,
            "id":str(amount) + "_",
            "includes":[],
            "type": "daily",
            "uid":[]
        }
        response = self.session.post(url, headers=self.headers, json=payload,timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} post_claim data:{data}")
        return data


    def get_open(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0 or energy == 0:
            return None
        url = f"https://www.mintchain.io/api/tree/turntable/open"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_open data:{data}")
        return data

    def post_inject(self,energy):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0 or energy == 0:
            return None
        url = f"https://www.mintchain.io/api/tree/inject"
        payload = {
            "address":self.account.address,
            "energy": energy,
        }
        response = self.session.post(url, headers=self.headers, json=payload,timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} post_inject data:{data}")
        return data

    def run(self,alias, account,proxyinfo):
        self.alias = alias
        self.account = account
        self.create_new_session(proxyinfo)
        try:
            msg = self.mint_forest_event()
            hex = self._sign_message(msg)
            response = self.post_login(msg, hex)
            auth_token = response['result']['access_token']
            self.headers['authorization'] = 'Bearer ' + auth_token
            log_and_print(f"{alias} post_login successfully ")
        except Exception as e:
            log_and_print(f"{alias} post_login failed: {e}")
            excel_manager.update_info(alias, f" post_login failed: {e}")
            return False

        try:
            response = self.get_totalUser()
            #这不校验结果
        except Exception as e:
            pass

        try:
            response = self.get_merank()
            log_and_print(f"{alias} get_merank successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_merank failed: {e}")
            excel_manager.update_info(alias, f"get_merank failed: {e}")
            return False

        try:
            response = self.get_energylist()
            freeze = response['result'][0]['freeze']
            log_and_print(f"{alias} get_energylist successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_energylist failed: {e}")
            excel_manager.update_info(alias, f"get_energylist failed: {e}")
            return False

        try:
            response = self.get_asset()
            #这不校验结果
        except Exception as e:
            pass

        try:
            response = self.get_leaderboard()
            log_and_print(f"{alias} get_leaderboard successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_leaderboard failed: {e}")
            excel_manager.update_info(alias, f"get_leaderboard failed: {e}")
            return False


        try:
            response = self.get_activity()
            log_and_print(f"{alias} get_activity successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_activity failed: {e}")
            excel_manager.update_info(alias, f"get_activity failed: {e}")
            return False

        try:
            response = self.get_userinfo()
            log_and_print(f"{alias} get_userinfo successfully ")
            energy = response['result']['energy']
            treeEnergy = response['result']['tree']
        except Exception as e:
            log_and_print(f"{alias} get_userinfo failed: {e}")
            excel_manager.update_info(alias, f"get_userinfo failed: {e}")
            return False

        try:
            response = self.get_tasklist()
            response = self.get_experiments()
            #这不校验结果
        except Exception as e:
            pass

        if freeze == False:
            try:
                response = self.post_claim()
                log_and_print(f"{alias} post_claim successfully ")
            except Exception as e:
                log_and_print(f"{alias} post_claim failed: {e}")
                excel_manager.update_info(alias, f"post_claim failed: {e}")
                return False

        try:
            response = self.get_userinfo()
            log_and_print(f"{alias} get_userinfo successfully ")
            energy = response['result']['energy']
            treeEnergy = response['result']['tree']
        except Exception as e:
            log_and_print(f"{alias} get_userinfo failed: {e}")
            excel_manager.update_info(alias, f"get_userinfo failed: {e}")
            return False

        try:
            response = self.get_energylist()
            freeze = response['result'][0]['freeze']
            log_and_print(f"{alias} get_energylist successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_energylist failed: {e}")
            excel_manager.update_info(alias, f"get_energylist failed: {e}")
            return False

        try:
            response = self.get_merank()
            log_and_print(f"{alias} get_merank successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_merank failed: {e}")
            excel_manager.update_info(alias, f"get_merank failed: {e}")
            return False

        try:
            response = self.post_inject(energy)
            log_and_print(f"{alias} post_inject successfully ")
        except Exception as e:
            log_and_print(f"{alias} post_inject failed: {e}")
            excel_manager.update_info(alias, f"post_inject failed: {e}")
            return False

        try:
            response = self.get_tasklist()
            response = self.get_experiments()
            response = self.get_open()
            #这不校验结果
        except Exception as e:
            pass

        try:
            response = self.get_userinfo()
            log_and_print(f"{alias} get_userinfo successfully ")
            energy = response['result']['energy']
            treeEnergy = response['result']['tree']
            log_and_print(f"{alias} energy {energy} treeEnergy {treeEnergy}")
            excel_manager.update_info(alias, f"energy {energy} treeEnergy {treeEnergy}")
        except Exception as e:
            log_and_print(f"{alias} get_userinfo failed: {e}")
            excel_manager.update_info(alias, f"get_userinfo failed: {e}")
            return False

default_account_path = rf'\\192.168.3.142\SuperWind\Study\account_config\minchaint_account.json'

if __name__ == '__main__':
    app = MintChainGM()
    retry_list = []
    failed_list = []
    proxyApp = socket5SwitchProxy(logger = log_and_print)
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("MintChainGM", log_and_print)
    alais_list = UserInfoApp.find_alias_by_path(config_file = default_account_path)
    for alias in alais_list:
        log_and_print(f"statring running by alias {alias}")
        key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        account = web3.Account.from_key(key)    
        proxyName = UserInfoApp.find_socket5proxy_by_alias_in_file(alias)
        if not proxyName:
            log_and_print(f"cannot find proxy username = {alias}")
            excel_manager.update_info(alias, f"cannot find proxy ")
            continue
        result, proxyinfo = proxyApp.change_proxy_until_success(proxyName)
        if result == False:
            log_and_print(f"change_proxy_until_success failed {alias}")
            excel_manager.update_info(alias, f"change_proxy_until_success failed")
            retry_list.append((alias, account))
            continue

        if(app.run(alias, account,proxyinfo) == False):
            retry_list.append((alias, account))

    if len(retry_list) != 0:
        log_and_print("start retry faile case")
        time.sleep(10)

    for alias, account in retry_list:
        proxyName = UserInfoApp.find_socket5proxy_by_alias_in_file(alias)
        if not proxyName:
            log_and_print(f"cannot find proxy username = {alias}")
            excel_manager.update_info(alias, f"cannot find proxy ")
            continue
        result, proxyinfo = proxyApp.change_proxy_until_success(proxyName)
        if result == False:
            log_and_print(f"change_proxy_until_success failed {alias}")
            excel_manager.update_info(alias, f"change_proxy_until_success failed")
            continue
        time.sleep(5)   
        if(app.run(alias, account,proxyinfo) == False):
            failed_list.append((alias, account))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for alias, account in failed_list:
        log_and_print(f"final failed username = {alias}")
    excel_manager.save_msg_and_stop_service()





