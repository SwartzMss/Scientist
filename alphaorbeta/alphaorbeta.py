
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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\alphaorbeta_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class alphaorbeta:
    def __init__(self):
        self.alias = None
        self.account = None
        self.session = None
        self.userId = None
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
            'referer': 'https://app.alphaorbeta.com',
            'origin': 'https://www.mintchain.io', 
        }

    def create_new_session(self,proxyinfo):
        ua = UserAgent()
        self.headers['user-agent'] = ua.random
        self.headers.pop('Authorization', None)
        self.session = requests.Session()
        self.session.cookies.clear()
        self.session.proxies = proxyinfo

    def signature(self):
        message = "Please click “sign” to confirm your identity as the owner of this address."
        res = self.account.sign_message(encode_defunct(text=message))
        return res.signature.hex()


    def put_signInOrSignUpByWallet(self,signature):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/signInOrSignUpByWallet"
        message = "Please click “sign” to confirm your identity as the owner of this address."
        payload = {
                "address": self.account.address,
                "message":message,
                "signature":signature
        }
        response = self.session.put(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias}post_signInOrSignUpByWallet data:{data}")
        return data

    def get_daily(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userQuest/user/{self.userId}/daily"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_daily data:{data}")
        return data

    def post_checkin(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userQuest/checkin/user/{self.userId}/complete?version=v2"
        response = self.session.post(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} post_checkin data:{data}")
        return data

    def get_points(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/point/user/{self.userId}"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_points data:{data}")
        return data

    def get_profile(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0 or energy == 0:
            return None
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/user/{self.userId}/profile"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_profile data:{data}")
        return data

    def get_hasPoppedMembershipCard(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0 or energy == 0:
            return None
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/user/{self.userId}/hasPoppedMembershipCard"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_hasPoppedMembershipCard data:{data}")
        return data

    def run(self,alias, account,proxyinfo):
        self.alias = alias
        self.account = account
        self.userId = None
        self.create_new_session(proxyinfo)

        try:
            signature = self.signature()
            response = self.put_signInOrSignUpByWallet(signature)
            if 'error' in response:
                raise Exception(f"Error: {response}")
            token = response["jwt"]
            self.userId = response["userId"]
            self.headers['authorization'] = 'Bearer ' + token
            log_and_print(f"{alias} post_signInOrSignUpByWallet successfully ")
        except Exception as e:
            log_and_print(f"{alias} post_signInOrSignUpByWallet failed: {e}")
            excel_manager.update_info(alias, f"post_signInOrSignUpByWallet failed: {e}")
            return False

        try:
            response = self.get_points()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            for balance in response:
                total_balance = int(balance['totalBalance'])
                decimal = balance['decimal']
                if balance['point'] == 'abETH':
                    abETH_value = total_balance / (10 ** decimal)
                elif balance['point'] == 'abCHIPS':
                    abCHIPS_value = total_balance / (10 ** decimal)
            log_and_print(f"{alias} get_points successfully  abETH_value {abETH_value} abCHIPS_value {abCHIPS_value}")
        except Exception as e:
            log_and_print(f"{alias} get_points failed: {e}")
            excel_manager.update_info(alias, f"get_points failed: {e}")
            return False


        try:
            response = self.get_profile()
            response = self.get_hasPoppedMembershipCard()
            #这不校验结果
        except Exception as e:
            pass

        try:
            response = self.get_daily()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            claimed_value = response['DAILY_CHECKIN']['claimed']
            log_and_print(f"{alias} get_daily successfully claimed_value {claimed_value}")
        except Exception as e:
            log_and_print(f"{alias} get_daily failed: {e}")
            excel_manager.update_info(alias, f"get_daily failed: {e}")
            return False

        if claimed_value == 0:
            try:
                response = self.post_checkin()
                if 'error' in response:
                    raise Exception(f"Error: {response}")
                log_and_print(f"{alias} post_checkin successfully ")
            except Exception as e:
                log_and_print(f"{alias} post_checkin failed: {e}")
                excel_manager.update_info(alias, f"post_checkin failed: {e}")
                return False
        try:
            response = self.get_profile()
            response = self.get_hasPoppedMembershipCard()
            #这不校验结果
        except Exception as e:
            pass


        try:
            response = self.get_daily()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            claimed_value = response['DAILY_CHECKIN']['claimed']
            log_and_print(f"{alias} get_daily successfully claimed_value {claimed_value}")
        except Exception as e:
            log_and_print(f"{alias} get_daily failed: {e}")
            excel_manager.update_info(alias, f"get_daily failed: {e}")
            return False

        try:
            response = self.get_points()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            for balance in response:
                total_balance = int(balance['totalBalance'])
                decimal = balance['decimal']
                if balance['point'] == 'abETH':
                    abETH_value = total_balance / (10 ** decimal)
                elif balance['point'] == 'abCHIPS':
                    abCHIPS_value = total_balance / (10 ** decimal)
            log_and_print(f"{alias} get_points successfully  abETH_value {abETH_value} abCHIPS_value {abCHIPS_value}")
            excel_manager.update_info(alias, f"abETH_value {abETH_value} abCHIPS_value {abCHIPS_value} claimed_value {claimed_value}")
        except Exception as e:
            log_and_print(f"{alias} get_points failed: {e}")
            excel_manager.update_info(alias, f"get_points failed: {e}")
            return False

if __name__ == '__main__':
    app = alphaorbeta()
    retry_list = []
    failed_list = []
    proxyApp = socket5SwitchProxy(logger = log_and_print)
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("alphaorbeta", log_and_print)
    alais_list = UserInfoApp.find_alias_by_path()
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





