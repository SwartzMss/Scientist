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
from tools.YesCaptchaClient import YesCaptchaClient

# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\XterioGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')

class QuestionPicker:
    def __init__(self, filename = rf'E:\HardCode\web3\Scientist\XterioGM\Question.txt'):
        self.filename = filename
        self.questions = []
        self.used_questions = set()
        self.load_questions()

    def load_questions(self):
        with open(self.filename, 'r') as file:
            self.questions = [line.strip() for line in file.readlines() if line.strip()]

    def get_random_question(self):
        available_questions = list(set(self.questions) - self.used_questions)

        if not available_questions:
            self.used_questions.clear()
            available_questions = self.questions.copy()

        question = random.choice(available_questions)
        self.used_questions.add(question)
        return question

class XterioGM:
    def __init__(self, rpc_url="https://xterio.alt.technology", chain_id=112358):
        #self.QuestionPickerApp = QuestionPicker()
        self.rpc = Rpc(rpc=rpc_url, chainid=chain_id)
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.alias = None
        self.session = None
        self.gaslimit = 200000
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
            'referer': 'https://xter.io',
            'origin': 'https://xter.io', 
            'sec-ch-ua-platform': '"Windows"',
        }
    def create_new_session(self,proxyinfo):
        ua = UserAgent()
        self.headers['user-agent'] = ua.random
        self.headers.pop('Authorization', None)
        self.session = requests.Session()
        self.session.cookies.clear()
        self.session.proxies = proxyinfo

    def get_signMsg(self):
        url = f"https://api.xter.io/account/v1/login/wallet/{self.account.address}"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_signMsg data:{data}")
        return data


    def signature(self,message):
        res = self.account.sign_message(encode_defunct(text=message))
        return res.signature.hex()


    def post_wallet(self,signature):
        url = f"https://api.xter.io/account/v1/login/wallet"

        payload = {
                "address":self.account.address,
                "invite_code":"53f48ab9f7a4c936cd47941e6d3c8798",
                "provider":"METAMASK",
                "sign":signature,
                "type": "eth"
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} post_wallet data:{data}")
        return data

    def get_point(self):
        url = f"https://api.xter.io/palio/v1/user/{self.account.address}/point"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_point data:{data}")
        return data

    def get_nonce(self):
        """获取当前账户的交易数，以确定nonce."""
        return self.rpc.get_transaction_nonce(self.account.address)['result']

    def encodeABI_Nonce(self):
        nonce = self.get_nonce()
        encoded_data = encode(
            ["uint8"],
            [nonce]
        )
        encoded_data_hex = encoded_data.hex()
        log_and_print(f"encodeABI_Nonce = {encoded_data_hex}")
        return encoded_data_hex

    def claimUtility(self):
        __contract_addr = Web3.to_checksum_address("0xBeEDBF1d1908174b4Fc4157aCb128dA4FFa80942")
        param = self.encodeABI_Nonce(amount)
        MethodID="0x8e6e1450" 
        try:
            data = MethodID + param
            gasprice = int(self.rpc.get_gas_price()['result'], 16) * 2
            response = self.rpc.transfer(
                self.account, __contract_addr, 0, self.gaslimit, gasprice, data=data)
            if 'error' in response:
                raise Exception(f"Error: {response}")
            hasResult = response["result"]
            log_and_print(f"{alias} approve_action successfully hash = {hasResult}")
            self.QueueForApprovalResult.append((alias, private_key, hasResult, amount))
        except Exception as e:
            log_and_print(f"{alias} approve_action failed: {e}")
            excel_manager.update_info(alias, f" approve_action failed: {e}", "approve_action")
    def run(self,alias, account,proxyinfo):
        self.create_new_session(proxyinfo)
        self.alias = alias
        self.account = account
        try:
            response= self.get_signMsg()
            if response["err_code"] != 0:
                raise Exception(f"Error: {response}")
            signMsg = response["data"]["message"]
            log_and_print(f"{alias} get_signMsg successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_signMsg failed: {e}")
            excel_manager.update_info(alias, f"get_signMsg failed: {e}")
            return False

        try:
            signature = self.signature(signMsg)
            log_and_print(f"{alias} sign successfully ")
        except Exception as e:
            log_and_print(f"{alias} sign failed: {e}")
            excel_manager.update_info(alias, f"sign failed: {e}")
            return False

        try:
            response = self.post_wallet(signature)
            if response["err_code"] != 0:
                raise Exception(f"Error: {response}")
            token = response['data']["id_token"]
            self.headers['authorization'] = 'Bearer ' + token
            log_and_print(f"{alias} post_wallet successfully ")
        except Exception as e:
            log_and_print(f"{alias} post_wallet failed: {e}")
            excel_manager.update_info(alias, f"post_wallet failed: {e}")
            return False

        try:
            response = self.get_point()
            log_and_print(f"{alias} get_point successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_point failed: {e}")
            excel_manager.update_info(alias, f"get_point failed: {e}")
            return False


if __name__ == '__main__':
    proxyApp = socket5SwitchProxy(logger = log_and_print)
    failed_list = []
    retry_list = [] 
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("XterioGM", log_and_print)
    client_key = UserInfoApp.find_yesCaptch_clientkey()
    app = XterioGM()

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
