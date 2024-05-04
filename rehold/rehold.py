#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import math
import web3
import random
import urllib
import sys
import datetime
import pytz
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
from tools.YesCaptchaClient import YesCaptchaClient

# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\ReholdGM_{current_time}.log'

def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')

class ReholdGM:
    def __init__(self):
        self.alias = None
        self.session = None
        self.account = None
        self.captcha_client = YesCaptchaClient(logger = log_and_print,client_key = client_key)
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
            'origin': 'https://app.rehold.io',
            'referer': 'https://app.rehold.io/?utm_source=referral&utm_campaign=YV7I&quoteTicker=usdt',
        }
    def create_new_session(self,proxyinfo):
        ua = UserAgent()
        self.headers['user-agent'] = ua.random
        self.headers.pop('Authorization', None)
        self.session = requests.Session()
        self.session.cookies.clear()
        self.session.proxies = proxyinfo


    def signMessage(self):
        msg = "Welcome to ReHold!\n\nThis request will not trigger a blockchain transaction or cost any gas fees.\n\nIt's needed to authenticate your wallet address."
        res = self.account.sign_message(encode_defunct(text=msg))
        return res.signature.hex()

    def post_signup(self):
        url = f"https://app.rehold.io/api/v2/auth/signup"
        payload = {
            "address":self.account.address,
        }
        response = self.session.post(url, headers=self.headers, json=payload, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} post_signup data:{data}")
        return data

    def get_points(self):
        url = f"https://app.rehold.io/api/v1/points/{self.account.address}"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_points data:{data}")
        return data

    def get_count(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://app.rehold.io/api/v2/duals/1/{self.account.address}/count"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_count data:{data}")
        return data

    def get_settings(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://app.rehold.io/api/v1/points/settings"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_settings data:{data}")
        return data

    def get_rates(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://app.rehold.io/api/v2/rates"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_rates data:{data}")
        return data

    def has_time_arrived(self, time_str):
        # 获取当前时间
        current_time = datetime.datetime.now()

        # 提供的时间字符串
        # 将字符串转换为datetime对象
        target_time = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")

        # 检查当前时间是否达到或超过目标时间
        return current_time >= target_time

    def post_claim(self,recaptchaResponse):
        url = f"https://app.rehold.io/api/v1/points/claim"
        payload = {
            "recaptchaResponse":recaptchaResponse,
            "recaptchaType":"turnstile"
        }
        response = self.session.post(url, headers=self.headers, json=payload, timeout=10)
        log_and_print(f"{self.alias} post_claim status_code :{response.status_code }")
        return response

    def has_time_arrived(self, time_str):
        # 获取当前时间
        current_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))

        # 提供的时间字符串
        # 将字符串转换为datetime对象，并设定为UTC时区
        target_time = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        target_time = target_time.replace(tzinfo=pytz.utc)

        # 将目标时间从UTC转换为UTC+8
        target_time = target_time.astimezone(pytz.timezone('Asia/Shanghai'))

        # 检查当前时间是否达到或超过目标时间
        return current_time >= target_time

    def run(self,alias, account,proxyinfo):
        self.create_new_session(proxyinfo)
        self.alias = alias
        self.account = account
        self.ischatDone = False
        try:
            signature = self.signMessage()
            self.headers['Authorization'] = signature
            log_and_print(f"{alias} signMessage successfully ")
        except Exception as e:
            log_and_print(f"{alias} signMessage failed: {e}")
            excel_manager.update_info(alias, f"signMessage failed: {e}")
            return False

        try:
            response = self.post_signup()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} post_signup successfully ")
        except Exception as e:
            log_and_print(f"{alias} post_signup failed: {e}")
            excel_manager.update_info(alias, f"post_signup failed: {e}")
            return False

        try:
            response = self.get_count()
            response = self.get_settings()
            response = self.get_rates()
            #这不校验结果
        except Exception as e:
            pass

        try:
            response = self.get_points()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} get_points successfully ")
            balance = response["balance"]
            nextClaimAt = response["nextClaimAt"]
        except Exception as e:
            log_and_print(f"{alias} get_points failed: {e}")
            excel_manager.update_info(alias, f"get_points failed: {e}")
            return False

        if nextClaimAt != None and self.has_time_arrived(nextClaimAt) == False:
            excel_manager.update_info(alias, f"balance: {balance} not yet time to claim")
            return True

        try:
            website_url = 'https://app.rehold.io/'
            website_key = '0x4AAAAAAAVz4bcj5K56cYD4'
            task_type = 'TurnstileTaskProxyless'
            recaptcha_token = self.captcha_client.get_recaptcha_token_by_TurnstileTaskProxyless(website_url, website_key, task_type)
            log_and_print(f"{alias} get_recaptcha_token successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_recaptcha_token failed: {e}")
            excel_manager.update_info(alias, f"get_recaptcha_token failed: {e}")
            return False

        try:
            response = self.get_count()
            response = self.get_settings()
            response = self.get_rates()
            #这不校验结果
        except Exception as e:
            pass
        try:
            response = self.post_claim(recaptcha_token)
            if response.status_code != 204:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} post_claim successfully ")
        except Exception as e:
            log_and_print(f"{alias} post_claim failed: {e}")
            excel_manager.update_info(alias, f"post_claim failed: {e}")
            return False

        try:
            response = self.get_count()
            response = self.get_settings()
            response = self.get_rates()
            #这不校验结果
        except Exception as e:
            pass

        try:
            response = self.get_points()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} get_points successfully ")
            balance = response["balance"]
            excel_manager.update_info(alias, f"balance: {balance} claimed")
        except Exception as e:
            log_and_print(f"{alias} get_points failed: {e}")
            excel_manager.update_info(alias, f"get_points failed: {e}")
            return False

if __name__ == '__main__':
    proxyApp = socket5SwitchProxy(logger = log_and_print)
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("ReholdGM", log_and_print)
    client_key = UserInfoApp.find_yesCaptch_clientkey()
    app = ReholdGM()
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
