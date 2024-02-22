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

from eth_account.messages import encode_defunct
# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)
# 现在可以从tools目录导入Rpc
from tools.rpc import Rpc

# 现在可以从tools目录导入UserInfo
from tools.UserInfo import UserInfo
from tools.switchProxy import ClashAPIManager
# 现在可以从tools目录导入excelWorker
from tools.excelWorker import excelWorker


# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\Qna3GM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class Qna3GM:
    def __init__(self,rpc_url='https://1rpc.io/opbnb', chain_id=204):
        self.rpc = Rpc(rpc=rpc_url, chainid=chain_id)
        self.alias = None
        self.session = None
        self.gaslimit = 200000
        self.account = None
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
        }
    def create_new_session(self):
        self.session = requests.Session()

    def sign(self):
        msg=f"""AI + DYOR = Ultimate Answer to Unlock Web3 Universe"""
        res = self.account.sign_message(encode_defunct(text=msg))
        return res.signature.hex()

    def calculate_unclaimed_score(self, json_data):
        try:
            items = json_data["data"]["userDetail"]["creditHistories"]["items"]
            # 计算分数总和
            score_sum = sum(item["score"] for item in items if not item.get("claimed", True))
        except KeyError:
            # 如果数据不完整（即缺少字段），则返回 0
            score_sum = 0
        
        return score_sum


    def post_login(self,signature):
        url = f"https://api.qna3.ai/api/v2/auth/login?via=wallet"

        payload = {
            "wallet_address": self.account.address,
            "signature": signature
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=60)
        data = response.json()
        log_and_print(f"{self.alias} post_login data:{data}")
        return data

    def post_loadUserDetail(self,id):
        url = f"https://api.qna3.ai/api/v2/graphql"

        payload = {
            "query": "query loadUserDetail($cursored: CursoredRequestInput!) {\n  userDetail {\n    checkInStatus {\n      checkInDays\n      todayCount\n    }\n    credit\n    creditHistories(cursored: $cursored) {\n      cursorInfo {\n        endCursor\n        hasNextPage\n      }\n      items {\n        claimed\n        extra\n        id\n        score\n        signDay\n        signInId\n        txHash\n        typ\n      }\n      total\n    }\n    invitation {\n      code\n      inviteeCount\n      leftCount\n    }\n    origin {\n      email\n      id\n      internalAddress\n      userWalletAddress\n    }\n    externalCredit\n    voteHistoryOfCurrentActivity {\n      created_at\n      query\n    }\n    ambassadorProgram {\n      bonus\n      claimed\n      family {\n        checkedInUsers\n        totalUsers\n      }\n    }\n  }\n}",
            "variables": {
                "headersMapping": {
                    "x-lang": "chinese",
                    "x-id": id,
                    "Authorization": self.headers['Authorization']
                },
                "cursored": {
                    "after": "",
                    "first": 20
                }
            }
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=60)
        data = response.json()
        log_and_print(f"{self.alias} post_loadUserDetail data:{data}")
        return data

    def checkIn(self):
        """day"""
        __contract_addr = '0xB342e7D33b806544609370271A8D074313B7bc30'  # 合约地址
        data = "0xe95a644f0000000000000000000000000000000000000000000000000000000000000001"
        res = self.rpc.transfer(
            self.account, __contract_addr, 0, self.gaslimit, data=data)
        log_and_print(f"{self.alias} checkIn data:{data}")
        return res
    
    def post_check(self,hash):
        url = f"https://api.qna3.ai/api/v2/my/check-in"
        data={
            "hash": hash,
            "via": "bnb"
        }
        response = self.session.post(
            url, headers=self.headers, json=data,timeout=60)
        data = response.json()
        log_and_print(f"{self.alias} post_check data:{data}")
        return data

            
    def run(self,alias, account):
        self.create_new_session()
        self.alias = alias
        self.account = account
        try:
            hex = self.sign()
            response = self.post_login(hex)
            accessToken = response['data']['accessToken']
            id = response['data']['user']['id']
            self.headers['Authorization'] = 'Bearer '+ accessToken
            log_and_print(f"{alias} login successfully ")
        except Exception as e:
            log_and_print(f"{alias} login failed: {e}")
            excel_manager.update_info(alias, f"login failed: {e}")
            return False

        try:
            user_info = self.post_loadUserDetail(id)
            todayCount=user_info['data']['userDetail']['checkInStatus']['todayCount']
            checkInDays=user_info['data']['userDetail']['checkInStatus']['checkInDays']
            externalCredit=user_info['data']['userDetail']['externalCredit']
            unclaimed_score = self.calculate_unclaimed_score(user_info)
            log_and_print(f"{alias} loadUserDetail successfully ")
        except Exception as e:
            log_and_print(f"{alias} loadUserDetail failed: {e}")
            excel_manager.update_info(alias, f" loadUserDetail failed: {e}")
            return False

        try:
            if todayCount==1:
                log_and_print(f"{alias} today has checkIn unclaimed_score = {unclaimed_score}")
                excel_manager.update_info(alias, f"today has checkIn unclaimed_score = {unclaimed_score}")
                return True
            response = self.checkIn()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            result = response['result']
            check_Res = self.post_check(result)
            log_and_print(f"{alias} GM succeed, unclaimed_score = {unclaimed_score}")
            excel_manager.update_info(alias, f" GM succeed unclaimed_score = {unclaimed_score}")
        except Exception as e:
            log_and_print(f"{alias} GM failed: {e}")
            excel_manager.update_info(alias, f" GM failed: {e} unclaimed_score = {unclaimed_score}")
            return False
        


if __name__ == '__main__':
    app = Qna3GM()
    proxyApp = ClashAPIManager(logger = log_and_print)
    failed_list = []
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("Qna3GM", log_and_print)

    credentials_list = UserInfoApp.find_user_credentials_for_eth("Qna3GM")
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
            failed_list.append((alias, account))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for alias, account in failed_list:
        log_and_print(f"final failed username = {alias}")
    excel_manager.save_msg_and_stop_service()
    proxyApp.change_proxy("🇭🇰 HK | 香港 01")
