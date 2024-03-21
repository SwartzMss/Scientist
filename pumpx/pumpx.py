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
from tools.socket5SwitchProxy import socket5SwitchProxy
# 现在可以从tools目录导入excelWorker
from tools.excelWorker import excelWorker


# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\PumpxGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class PumpxGM:
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
        }
    def create_new_session(self,proxyinfo):
        ua = UserAgent()
        self.headers['user-agent'] = ua.random
        self.headers.pop('Authorization', None)
        self.session = requests.Session()
        self.session.cookies.clear()
        self.session.proxies = proxyinfo

    def post_challenge(self):
        url = f"https://lending.pumpx.io/lending/api/v1/auth/challenge"

        payload = {
            "address":self.account.address,
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} post_challenge data:{data}")
        return data

    def signature(self, msg):
        res = self.account.sign_message(encode_defunct(text=msg))
        return res.signature.hex()

    def post_login(self,msg, signature):
        url = f"https://lending.pumpx.io/lending/api/v1/auth/login"

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

    def get_status(self):
        url = f"https://pumpx.io/api/v1/xbn/mission/sign/status"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_status data:{data}")
        return data

    def get_invitecode(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://pumpx.io/api/v1/xbn/user/invite-code"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_invitecode data:{data}")
        return data

    def get_points(self):
        url = f"https://pumpx.io/api/v1/xbn/mission/points"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_points data:{data}")
        return data

    def get_check(self):
        url = f"https://pumpx.io/api/v1/xbn/pre-airdrop/check"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_check data:{data}")
        return data


    def get_collections(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://lending.pumpx.io/lending/api/v1/nft/collections"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_collections data:{data}")
        return data

    def post_sign(self):
        url = f"https://pumpx.io/api/v1/xbn/mission/sign"
        response = self.session.post(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} post_sign data:{data}")
        return data

    def post_blast(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://rpc.blast.io/"
        payload = {
                "jsonrpc":"2.0","id":4,"method":"eth_getBalance",
                "params": [self.account.address,"latest"]
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} post_blast data:{data}")
        return data

    def run(self,alias, account,proxyinfo):
        self.create_new_session(proxyinfo)
        self.alias = alias
        self.account = account
        try:
            response = self.post_challenge()
            msg = response["login_message"]
            log_and_print(f"{alias} post_challenge successfully ")
        except Exception as e:
            log_and_print(f"{alias} post_challenge failed: {e}")
            excel_manager.update_info(alias, f"post_challenge failed: {e}")
            return False
        
        try:
            signature = self.signature(msg)
            log_and_print(f"{alias} sign successfully ")
        except Exception as e:
            log_and_print(f"{alias} sign failed: {e}")
            excel_manager.update_info(alias, f"sign failed: {e}")
            return False

        try:
            response = self.post_login(msg,signature)
            accessToken = response['token']
            self.headers['Authorization'] = 'Bearer '+ accessToken
            log_and_print(f"{alias} post_login successfully ")
        except Exception as e:
            log_and_print(f"{alias} post_login failed: {e}")
            excel_manager.update_info(alias, f"post_login failed: {e}")
            return False

        try:
            response = self.get_status()
            log_and_print(f"{alias} first get_status successfully ")
        except Exception as e:
            log_and_print(f"{alias} first get_status failed: {e}")
            excel_manager.update_info(alias, f" first get_status failed: {e}")
            return False 

        try:
            response = self.get_points()
            sign_points = response["sign_points"]
            log_and_print(f"{alias} first get_points successfully sign_points = {sign_points}")
        except Exception as e:
            log_and_print(f"{alias} first get_points failed: {e}")
            excel_manager.update_info(alias, f"first get_points failed: {e}")
            return False 

        try:
            response = self.get_invitecode()
            log_and_print(f"{alias} get_invitecode successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_invitecode failed: {e}")
            excel_manager.update_info(alias, f"get_invitecode failed: {e}")
            return False 

        try:
            response = self.get_check()
            log_and_print(f"{alias} get_check successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_check failed: {e}")
            excel_manager.update_info(alias, f"get_check failed: {e}")
            return False 

        try:
            response = self.get_status()
            log_and_print(f"{alias} first get_status successfully ")
        except Exception as e:
            log_and_print(f"{alias} first get_status failed: {e}")
            excel_manager.update_info(alias, f" first get_status failed: {e}")
            return False 
        try:
            response = self.post_blast()
            log_and_print(f"{alias} first post_blast successfully ")
        except Exception as e:
            log_and_print(f"{alias} first post_blast failed: {e}")
            excel_manager.update_info(alias, f"first post_blast failed: {e}")
            return False 

        try:
            response = self.post_sign()
            if 'error' in response and 'already signed' in response['error'].get('message', ''):
                log_and_print(f"{alias} already signed")
                excel_manager.update_info(alias, f"already signed: sign_points = {sign_points}")
                return True
            points = response["points"]
            log_and_print(f"{alias} post_sign successfully post_sign = {points}")
        except Exception as e:
            log_and_print(f"{alias} post_sign failed: {e}")
            excel_manager.update_info(alias, f"get_check failed: {e}")
            return False 

        try:
            response = self.post_blast()
            log_and_print(f"{alias} second post_blast successfully ")
        except Exception as e:
            log_and_print(f"{alias} second post_blast failed: {e}")
            excel_manager.update_info(alias, f"second post_blast failed: {e}")
            return False 
        try:
            response = self.get_status()
            log_and_print(f"{alias} second get_status successfully ")
        except Exception as e:
            log_and_print(f"{alias} second get_status failed: {e}")
            excel_manager.update_info(alias, f"second get_status failed: {e}")
            return False 

        try:
            response = self.get_points()
            sign_points = response["sign_points"]
            log_and_print(f"{alias} second get_points successfully sign_points = {sign_points}")
            excel_manager.update_info(alias, f"second get_points sign_points = {sign_points}")
        except Exception as e:
            log_and_print(f"{alias} second get_points failed: {e}")
            excel_manager.update_info(alias, f"second get_points failed: {e}")
            return False 

if __name__ == '__main__':
    app = PumpxGM()
    proxyApp = socket5SwitchProxy(logger = log_and_print)
    failed_list = []
    retry_list = [] 
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("PumpxGM", log_and_print)

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
