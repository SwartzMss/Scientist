#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import math
import web3
import random
import urllib
import sys
import secrets
import requests
import datetime
from fake_useragent import UserAgent
from eth_account.messages import encode_defunct
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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\MidleGM_{current_time}.log'

def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')

class MidleGM:
    def __init__(self):
        self.alias = None
        self.session = None
        self.account = None
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://app.midle.io',
            'referer': 'https://app.midle.io',
            'Apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI2NGFkNDgzNDkwNzhjZWVlODI0NGM4NjQiLCJ1c2VySWQiOiI2M2M5MDRlNTYxNjFhOWVhMjY1ZDk4OGIiLCJleHAiOjE2ODkxNjQyMTJ9.ad2u1V5GodVnd6Taqj8A91F9g_jiblSlNA4G3JnYH4Y'
        }
    def create_new_session(self,proxyinfo):
        ua = UserAgent()
        self.headers['user-agent'] = ua.random
        self.headers.pop('Authorization', None)
        self.session = requests.Session()
        self.session.cookies.clear()
        self.session.proxies = proxyinfo


    def signMessage(self,message):
        res = self.account.sign_message(encode_defunct(text=message))
        return res.signature.hex()

    def post_wallet(self,message,signMsg):
        url = f"https://backend-v2.midle.io/auth/wallet"
        payload = {
            "accountAddress":self.account.address,
            'message':message,
            'ref':'662e3ef851f36fe8945bd10e',
            'signature':signMsg
        }
        response = self.session.post(url, headers=self.headers, json=payload, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} post_wallet data:{data}")
        return data

    def get_metamaskloginmessage(self):
        url = f"https://backend-v2.midle.io/auth/wallet/metamaskloginmessage?wallet={self.account.address}"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_metamaskloginmessage data:{data}")
        return data

    def get_init(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://backend-v2.midle.io/home/init"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_init data:{data}")
        return data


    def get_active(self):
        url = f"https://backend-v2.midle.io/rewards/active"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_active data:{data}")
        return data

    def get_self(self):
        url = f"https://backend-v2.midle.io/home/self"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_self data:{data}")
        return data

    def get_user(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://backend-v2.midle.io/home/user"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_self data:{data}")
        return data

    def post_claim(self,message,signMsg):
        url = f"https://backend-v2.midle.io/rewards/claim"
        response = self.session.post(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} post_wallet data:{data}")
        return data

    def run(self,alias, account,proxyinfo):
        self.create_new_session(proxyinfo)
        self.alias = alias
        self.account = account

        try:
            response = self.get_metamaskloginmessage()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} get_metamaskloginmessage successfully ")
            message = response['message']
        except Exception as e:
            log_and_print(f"{alias} get_metamaskloginmessage failed: {e}")
            excel_manager.update_info(alias, f"get_metamaskloginmessage failed: {e}")
            return False

        try:
            signature = self.signMessage(message)
            log_and_print(f"{alias} signMessage successfully ")
        except Exception as e:
            log_and_print(f"{alias} signMessage failed: {e}")
            excel_manager.update_info(alias, f"signMessage failed: {e}")
            return False

        try:
            response = self.post_wallet(message,signature)
            if 'error' in response:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} post_wallet successfully ")
            self.headers['Authorization'] = 'Bearer ' + response['accessToken']
        except Exception as e:
            log_and_print(f"{alias} post_wallet failed: {e}")
            excel_manager.update_info(alias, f"post_wallet failed: {e}")
            return False

        try:
            response = self.get_init()
            response = self.get_user()
            #这不校验结果
        except Exception as e:
            pass

        try:
            response = self.get_active()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} get_active successfully ")
            claims = response['claims']
        except Exception as e:
            log_and_print(f"{alias} get_active failed: {e}")
            excel_manager.update_info(alias, f"get_active failed: {e}")
            return False

        try:
            response = self.get_self()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} get_self successfully ")
            currentXp = response['profile']['currentXp']
            currentTicket = response['profile']['currentTicket']
        except Exception as e:
            log_and_print(f"{alias} get_self failed: {e}")
            excel_manager.update_info(alias, f"get_self failed: {e}")
            return False

        try:
            response = self.get_init()
            response = self.get_user()
            #这不校验结果
        except Exception as e:
            pass

        if claims == True:
            excel_manager.update_info(alias, f"currentXp {currentXp} claims {claims} currentTicket {currentTicket}")
            return True

        try:
            response = self.post_claim(message,signature)
            if response["success"] != True:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} post_claim successfully ")
        except Exception as e:
            log_and_print(f"{alias} post_claim failed: {e}")
            excel_manager.update_info(alias, f"post_claim failed: {e}")
            return False

        try:
            response = self.get_active()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} get_active successfully ")
            claims = response['claims']
        except Exception as e:
            log_and_print(f"{alias} get_active failed: {e}")
            excel_manager.update_info(alias, f"get_active failed: {e}")
            return False

        try:
            response = self.get_self()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} get_self successfully ")
            currentXp = response['profile']['currentXp']
            currentTicket = response['profile']['currentTicket']
        except Exception as e:
            log_and_print(f"{alias} get_self failed: {e}")
            excel_manager.update_info(alias, f"get_self failed: {e}")
            return False

        excel_manager.update_info(alias, f"currentXp {currentXp} claims {claims} currentTicket{currentTicket}")


        try:
            response = self.get_init()
            response = self.get_user()
            #这不校验结果
        except Exception as e:
            pass

if __name__ == '__main__':
    proxyApp = socket5SwitchProxy(logger = log_and_print)
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("MidleGM", log_and_print)
    app = MidleGM()
    retry_list = []
    failed_list = []
    
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
