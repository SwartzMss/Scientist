#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import math
import web3
import random
import urllib
import sys
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
from tools.switchProxy import ClashAPIManager
# 现在可以从tools目录导入excelWorker
from tools.excelWorker import excelWorker


# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\CapxGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class CapxGM:
    def __init__(self):
        self.alias = None
        self.session = None
        self.gaslimit = 200000
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
            'Origin':'https://app.capx.fi',
        }
    def create_new_session(self):
        ua = UserAgent()
        self.headers['user-agent'] = ua.random
        self.headers.pop('Authorization', None)
        self.session = requests.Session()
        self.session.cookies.clear()


    def sign(self):
        msg=f"Sign in with Ethereum to the capx app."
        res = self.account.sign_message(encode_defunct(text=msg))
        return res.signature.hex()

    def post_identity(self):
        url = f"https://embed.api.obvious.technology/v1/events/identity"

        payload = {
            "address":self.account.address,
            "smart":False,
            "provider":"OKX Wallet",
            "smart_account":"",
            "smart_account_version":"2"
        }
        self.headers['Access-Key'] = '196c53ab-03cd-407b-a859-95f770785368'
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=60)
        self.headers.pop('Access-Key', None)  # 如果'Access-Key'不存在，返回None，不会抛出异常
        data = response.json()
        log_and_print(f"{self.alias} post_identity data:{data}")
        return data

    def post_auth(self,signature):
        url = f"https://us-central1-capx-app.cloudfunctions.net/wallet/auth"

        payload = {
            "data":
            {
                "address":self.account.address,
                "message":"Sign in with Ethereum to the capx app.",
                "signature":signature
            }
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=60)
        data = response.json()
        log_and_print(f"{self.alias} post_auth data:{data}")
        return data

    def post_signInWithCustomToken(self,token):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyDR430YgDlW1Llt_QJyGnLn8-sQmkUKIfY"

        payload = {
            "token":token,
            "returnSecureToken":True
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=60)
        data = response.json()
        log_and_print(f"{self.alias} post_signInWithCustomToken data:{data}")
        return data

    def get_wallet(self):
        url = f"https://us-central1-capx-app.cloudfunctions.net/users/wallet"

        response = self.session.get(
            url, headers=self.headers, timeout=60)
        data = response.json()
        log_and_print(f"{self.alias} get_wallet data:{data}")
        return data

    def get_faucet(self):
        url = f"https://us-central1-capx-app.cloudfunctions.net/users/faucet"

        response = self.session.get(
            url, headers=self.headers,timeout=60)
        data = response.json()
        log_and_print(f"{self.alias} get_faucet data:{data}")
        return data   

    def run(self,alias, account):
        self.create_new_session()
        self.alias = alias
        self.account = account
        try:
            hex = self.sign()
            #response = self.post_identity()
            response = self.post_auth(hex)
            token = response['result']['token']
            response = self.post_signInWithCustomToken(token)
            if 'error' in response:
                raise Exception(f"post_signInWithCustomToken Error: {response}")
            accessToken = response['idToken']
            self.headers['Authorization'] = 'Bearer '+ accessToken
            response  = self.get_wallet()
            if response['result']['success'] == False and response['result']['message'] != "Funds can be requested once every 24hrs":
                raise Exception(f"get_wallet Error: {response}")
            response = self.get_faucet()
            if response['result']['success'] == False and response['result']['message'] != "Funds can be requested once every 24hrs":
                raise Exception(f"get_faucet Error: {response}")
            log_and_print(f"{alias} faucet successfully ")
            excel_manager.update_info(alias, f"faucet successfully")
            self.session.close()
        except Exception as e:
            self.session.close()
            log_and_print(f"{alias} faucet failed: {e}")
            excel_manager.update_info(alias, f"faucet failed: {e}")
            return False
        

if __name__ == '__main__':
    app = CapxGM()
    proxyApp = ClashAPIManager(logger = log_and_print)
    failed_list = []
    retry_list = [] 
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("CapxGM", log_and_print)

    credentials_list = UserInfoApp.find_user_credentials_for_eth("CapxGM")
    for credentials in credentials_list:
        alias = credentials["alias"]
        key = credentials["key"]
        proxyName = UserInfoApp.find_proxy_by_alias_in_file(alias)
        if proxyName== None:
            log_and_print(f"cannot find proxy username = {alias}")
            continue
        proxyApp.change_proxy(proxyName)
        time.sleep(5)   
        account = web3.Account.from_key(key)    
        if(app.run(alias, account) == False):
            retry_list.append((alias, account))

    if len(retry_list) != 0:
        log_and_print("start retry faile case")
        time.sleep(10)

    for alias, account in retry_list:
        proxyName = UserInfoApp.find_proxy_by_alias_in_file(alias)
        if proxyName== None:
            log_and_print(f"cannot find proxy username = {alias}")
            continue
        proxyApp.change_proxy(proxyName)
        time.sleep(5)   
        if(app.run(alias, account) == False):
            failed_list.append((alias, account))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for alias, account in failed_list:
        log_and_print(f"final failed username = {alias}")
    excel_manager.save_msg_and_stop_service()
    proxyApp.change_proxy("🇭🇰 HK | 香港 01")
