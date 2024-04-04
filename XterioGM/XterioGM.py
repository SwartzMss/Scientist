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
from web3 import Web3
from fake_useragent import UserAgent
from eth_account.messages import encode_defunct
from eth_abi import encode
# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)
from datetime import datetime
from tools.rpc import Rpc
# 现在可以从tools目录导入UserInfo
from tools.UserInfo import UserInfo
from tools.socket5SwitchProxy import socket5SwitchProxy
# 现在可以从tools目录导入excelWorker
from tools.excelWorker import excelWorker
from tools.YesCaptchaClient import YesCaptchaClient

# 获取当前时间并格式化为字符串
current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\XterioGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

    def check_transaction_status(self, tx_hash, timeout=300, interval=10):
        """检查交易的状态，返回是否确认和交易状态。使用计数器实现超时。"""
        max_attempts = timeout // interval  # 计算最大尝试次数
        attempts = 0  # 初始化尝试次数计数器

        while attempts < max_attempts:  # 循环直到达到最大尝试次数
            try:
                receipt = self.web3.eth.get_transaction_receipt(tx_hash)                
                if receipt is not None:
                    if receipt.status == 1:
                        return True, "success"  # 交易已确认且成功
                    else:
                        return False, "failure"  # 交易已确认但失败
            except Exception as e:
                log_and_print(f"Error checking transaction status: {e}")
            
            time.sleep(interval)  # 等待一段时间再次检查
            attempts += 1  # 更新尝试次数

        # 超时后返回False，表示交易状态未知或未确认，状态为挂起
        return False, "pending"


    def get_nonce(self):
        """获取当前账户的交易数，以确定nonce."""
        return self.rpc.get_transaction_nonce(self.account.address)['result']

    def encodeABI_claimUtility(self,taskNum):
        encoded_data = encode(
            ["uint8"],
            [taskNum]
        )
        encoded_data_hex = encoded_data.hex()
        log_and_print(f"encodeABI_claimUtility = {encoded_data_hex}")
        return encoded_data_hex

    def claimUtility(self,taskNum):
        log_and_print(f"{alias} claimUtility  taskNum {taskNum}")
        __contract_addr = Web3.to_checksum_address("0xBeEDBF1d1908174b4Fc4157aCb128dA4FFa80942")
        param = self.encodeABI_claimUtility(taskNum)
        MethodID="0x8e6e1450" 
        try:
            data = MethodID + param
            gasprice = int(self.rpc.get_gas_price()['result'], 16) * 2
            response = self.rpc.transfer(
                self.account, __contract_addr, 0, self.gaslimit, gasprice, data=data)
            if 'error' in response:
                raise Exception(f"action Error: {response}")
            hasResult = response["result"]
            txIsSucceed,msg = self.check_transaction_status(hasResult)
            if  txIsSucceed != True:
                raise Exception(f"check_transaction_status Error: {msg}")
            response = self.post_triggert(hasResult)
            if response["err_code"] != 0:
                raise Exception(f"post_triggert Error: {response}")
        except Exception as e:
            log_and_print(f"{alias} claimUtility  failed: {e}")
            excel_manager.update_info(alias, f" claimUtility failed: {e}")
            return False

    def post_triggert(self,txHash):
        url = f"https://api.xter.io/baas/v1/event/trigger"

        payload = {
                "eventType":"PalioIncubator::*",
                "network":"XTERIO",
                "txHash":txHash,
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} post_triggert data:{data}")
        return data



    def post_prop(self,taskNum):
        url = f"https://api.xter.io/palio/v1/user/{self.account.address}/prop"

        payload = {
                "prop_id": taskNum
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} taskNum {taskNum} post_prop data:{data}")
        return data

    def get_tasks(self):
        url = f"https://api.xter.io/palio/v1/user/{self.account.address}/task"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_tasks data:{data}")
        return data

    def get_incubation(self):
        url = f"https://api.xter.io/palio/v1/user/{self.account.address}/incubation"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_incubation data:{data}")
        return data

    def analyze_incubation(self, data):
        # 获取props数组
        props = data['data']['props']

        # 获取当前日期，用于比较（此处需根据实际情况调整）
        current_date = datetime.utcnow().date()

        # 分类存储props_id
        need_claimUtility = []
        claimed_but_not_proped = []

        for prop in props:
            # 提取并转换UpdatedAt日期
            updated_at = datetime.strptime(prop['UpdatedAt'].split('T')[0], "%Y-%m-%d").date()
            
            # 检查是否需要claimUtility或prop
            if prop['total'] > prop['cons_total']:
                # claimUtility已执行但prop未执行
                claimed_but_not_proped.append(prop['props_id'])
            elif prop['total'] == prop['cons_total'] and updated_at < current_date:
                # 需要执行claimUtility
                need_claimUtility.append(prop['props_id'])

        # 返回结果
        return need_claimUtility, claimed_but_not_proped

    def post_task(self,taskNum):
        url = f"https://api.xter.io/palio/v1/user/{self.account.address}/task"
        payload = {
                "task_id": taskNum
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} post_task taskNum {taskNum} data:{data}")
        return data

    def get_ticket(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0 or energy == 0:
            return None
        url = f"https://api.xter.io/palio/v1/user/{self.account.address}/ticket"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_ticket data:{data}")
        return data

    def get_recent(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0 or energy == 0:
            return None
        url = f"https://api.xter.io/market/v1/items/recent"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_recent data:{data}")
        return data


    def get_unread(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0 or energy == 0:
            return None
        url = f"https://api.xter.io/message/v1/state/unread"
        response = self.session.get(url, headers=self.headers, timeout=10)
        data = response.json()
        log_and_print(f"{self.alias} get_unread data:{data}")
        return data

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
            response = self.get_unread()
            response = self.get_ticket()
            response = self.get_recent()
            #这不校验结果
        except Exception as e:
            pass

        try:
            response = self.get_incubation()
            need_claimUtility, claimed_but_not_proped = self.analyze_incubation(response)
            log_and_print(f"{alias} incubation successfully ")
            
        except Exception as e:
            log_and_print(f"{alias} get_incubation failed: {e}")
            excel_manager.update_info(alias, f"get_incubation failed: {e}")
            return False


        for taskNum in need_claimUtility:
            result = self.claimUtility(taskNum)
            if result == False:
                return False
            claimed_but_not_proped.append(taskNum)

        for taskNum in claimed_but_not_proped:
            try:
                response = self.post_prop(taskNum)
                if response["err_code"] != 0:
                    raise Exception(f" Error: {response}")
            except Exception as e:
                log_and_print(f"{alias} post_prop failed: {e}")
                excel_manager.update_info(alias, f"post_prop failed: {e}")
                return False

        try:
            task_ids = []
            response = self.get_tasks()
            if response["err_code"] != 0:
                raise Exception(f"Error: {response}")
            for task in response['data']['list']:
                task_id = task['ID']
                for user_task in task['user_task']:
                    if user_task['status'] == 1:
                        task_ids.append(task_id)  # 将满足条件的task_id添加到数组中
            log_and_print(f"{alias} get_tasks successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_tasks failed: {e}")
            excel_manager.update_info(alias, f"get_tasks failed: {e}")
            return False


        for taskNum in task_ids:
            try:
                response = self.post_task(taskNum)
                if response["err_code"] != 0:
                    raise Exception(f" Error: {response}")
            except Exception as e:
                log_and_print(f"{alias} post_prop failed: {e}")
                excel_manager.update_info(alias, f"post_prop failed: {e}")
                return False

        try:
            response = self.get_unread()
            response = self.get_ticket()
            response = self.get_recent()
            #这不校验结果
        except Exception as e:
            pass

        try:
            response = self.get_point()
            #这不校验结果
        except Exception as e:
            pass

        try:
            task_ids = []
            response = self.get_tasks()
            if response["err_code"] != 0:
                raise Exception(f"Error: {response}")
            for task in response['data']['list']:
                task_id = task['ID']
                for user_task in task['user_task']:
                    if user_task['status'] == 1:
                        task_ids.append(task_id)  # 将满足条件的task_id添加到数组中
            log_and_print(f"{alias} get_tasks successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_tasks failed: {e}")
            excel_manager.update_info(alias, f"get_tasks failed: {e}")
            return False


        for taskNum in task_ids:
            try:
                response = self.post_task(taskNum)
                if response["err_code"] != 0:
                    raise Exception(f" Error: {response}")
            except Exception as e:
                log_and_print(f"{alias} post_prop failed: {e}")
                excel_manager.update_info(alias, f"post_prop failed: {e}")
                return False

        try:
            response = self.get_point()
            if response["err_code"] != 0:
                raise Exception(f" Error: {response}")
            boost_sum = sum(item['value'] + 1 for item in response['data']['boost'])
            point_sum = sum(item['value'] for item in response['data']['point'])
            rank = response['data']['rank']
            log_and_print(f"{alias} boost_sum {boost_sum}  point_sum {point_sum} rank {rank} ")
            excel_manager.update_info(alias, f"boost_sum {boost_sum}  point_sum {point_sum} rank {rank}")
        except Exception as e:
            log_and_print(f"{alias} get_point failed: {e}")
            excel_manager.update_info(alias, f"get_point failed: {e}")
            return False


default_account_path = rf'\\192.168.3.142\SuperWind\Study\account_config\xterio_account.json'

if __name__ == '__main__':
    proxyApp = socket5SwitchProxy(logger = log_and_print)
    failed_list = []
    retry_list = [] 
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("XterioGM", log_and_print)
    client_key = UserInfoApp.find_yesCaptch_clientkey()
    app = XterioGM()

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
