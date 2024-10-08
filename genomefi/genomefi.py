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
log_file_path = rf'\\192.168.3.142\SuperWind\Study\GenomefiGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')

class QuestionPicker:
    def __init__(self, filename = rf'E:\HardCode\web3\Scientist\genomefi\Question.txt'):
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

class GenomefiGM:
    def __init__(self):
        self.QuestionPickerApp = QuestionPicker()
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
        }
    def create_new_session(self,proxyinfo):
        ua = UserAgent()
        self.headers['user-agent'] = ua.random
        self.headers.pop('Authorization', None)
        self.session = requests.Session()
        self.session.cookies.clear()
        self.session.proxies = proxyinfo

    def generate_nonce(self,bits=96):
        ALPHANUMERIC = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

        def random_string_for_entropy(bits, charset=ALPHANUMERIC):
            length = math.ceil(bits / (math.log2(len(charset))))
            return random_string(length, charset)

        def random_string(length, charset=ALPHANUMERIC):
            if len(charset) < 2 or len(charset) > 256:
                raise ValueError("Charset length must be between 2 and 256 characters")
            return ''.join(secrets.choice(charset) for _ in range(length))

        nonce = random_string_for_entropy(bits)
        if not nonce or len(nonce) < 8:
            raise ValueError("Error during nonce creation")
        return nonce

    def clean_multiline_string(self,s):
        # 分割字符串为单行
        lines = s.splitlines()

        # 移除每一行的前导和尾随空白
        stripped_lines = [line.strip() for line in lines]

        # 重新组合为一个字符串，并用换行符连接
        return '\n'.join(stripped_lines)

    def signature(self):
        uri = "https://event.genomefi.io"
        version = 1
        chain_id = 137
        nonce = self.generate_nonce()
        #nonce = "VKeJDzdPXpfLpcUoN"
        issued_at = datetime.datetime.utcnow()

        # 在当前时间基础上加上 10 分钟来设置过期时间
        expiration_time = issued_at + datetime.timedelta(minutes=10)

        # 如果你需要将时间转换为字符串
        # 将时间转换为字符串，并确保精确到毫秒三位小数
        issued_at_str = issued_at.isoformat(timespec='milliseconds') + 'Z'  # 添加 'Z' 来表示 UTC 时间
        expiration_time_str = expiration_time.isoformat(timespec='milliseconds') + 'Z'


        message = f"""event.genomefi.io wants you to sign in with your Ethereum account:
        {self.account.address}

        Sign in GenomeFi.

        URI: https://event.genomefi.io
        Version: 1
        Chain ID: 137
        Nonce: {nonce}
        Issued At: {issued_at_str}
        Expiration Time: {expiration_time_str}"""

        message = self.clean_multiline_string(message)
        res = self.account.sign_message(encode_defunct(text=message))
        return message, res.signature.hex()

    def post_wallet(self,msg, signature,recaptcha_token):
        url = f"https://sazn9rq17l.execute-api.ap-northeast-2.amazonaws.com/staging/user/auth/login/wallet"

        payload = {
                "address":self.account.address,
                "message":msg,
                "reCode":recaptcha_token,
                "signed":signature
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} wallet data:{data}")
        return data

    def get_profile(self):
        url = f"https://sazn9rq17l.execute-api.ap-northeast-2.amazonaws.com/staging/user/auth/info/profile"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_profile data:{data}")
        return data

    def post_nft(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://sazn9rq17l.execute-api.ap-northeast-2.amazonaws.com/staging/user/event/task/quiz/nft"
        payload = {"prompt":self.QuestionPickerApp.get_random_question()}
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} post_nft data:{data}")
        return data

    def post_chat(self):
        if self.ischatDone == True:
            return None
        url = f"https://sazn9rq17l.execute-api.ap-northeast-2.amazonaws.com/staging/user/event/task/quiz/quest"
        payload = {"question":self.QuestionPickerApp.get_random_question()}
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} post_chat data:{data}")
        return data

    def get_status(self):
        url = f"https://sazn9rq17l.execute-api.ap-northeast-2.amazonaws.com/staging/user/event/dashboard/status"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_status data:{data}")
        return data

    def get_dashboard(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://sazn9rq17l.execute-api.ap-northeast-2.amazonaws.com/staging/user/event/dashboard"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_dashboard data:{data}")
        return data

    def get_mygallery(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://sazn9rq17l.execute-api.ap-northeast-2.amazonaws.com/staging/user/event/dashboard/nft/mygallery?page=1"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_mygallery data:{data}")
        return data

    def post_attendance(self):
        url = f"https://sazn9rq17l.execute-api.ap-northeast-2.amazonaws.com/staging/user/event/task/attendance"
        response = self.session.post(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} post_attendance data:{data}")
        return data

    def get_point(self):
        url = f"https://sazn9rq17l.execute-api.ap-northeast-2.amazonaws.com/staging/user/event/point?page=1&item=4"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_point data:{data}")
        return data


    def get_referral(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0:
            return None
        url = f"https://app.pump.markets/api/point/referral"
        response = self.session.get(
            url, headers=self.headers, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias} get_referral data:{data}")
        return data

    def run(self,alias, account,proxyinfo):
        self.create_new_session(proxyinfo)
        self.alias = alias
        self.account = account
        self.ischatDone = False
        try:
            message, signature = self.signature()
            log_and_print(f"{alias} sign successfully ")
        except Exception as e:
            log_and_print(f"{alias} sign failed: {e}")
            excel_manager.update_info(alias, f"sign failed: {e}")
            return False

        try:
            website_url = 'https://event.genomefi.io/'
            website_key = '6LcK_aApAAAAAPAUR8Zo96ZMXGQF12jeUKR2KeGr'
            task_type = 'NoCaptchaTaskProxyless'
            recaptcha_token = self.captcha_client.get_recaptcha_token(website_url, website_key, task_type)
            log_and_print(f"{alias} get_recaptcha_token successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_recaptcha_token failed: {e}")
            excel_manager.update_info(alias, f"get_recaptcha_token failed: {e}")
            return False

        try:
            response = self.post_wallet(message,signature,recaptcha_token)
            token = response['accessToken']
            self.headers['authorization'] = 'Bearer ' + token
            log_and_print(f"{alias} post_wallet successfully ")
        except Exception as e:
            log_and_print(f"{alias} post_wallet failed: {e}")
            excel_manager.update_info(alias, f"post_wallet failed: {e}")
            return False

        try:
            response = self.get_profile()
            log_and_print(f"{alias} get_profile successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_profile failed: {e}")
            excel_manager.update_info(alias, f"get_profile failed: {e}")
            return False

        try:
            response = self.get_mygallery()
            log_and_print(f"{alias} get_mygallery successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_mygallery failed: {e}")
            excel_manager.update_info(alias, f"get_mygallery failed: {e}")
            return False

        try:
            response = self.get_dashboard()
            log_and_print(f"{alias} get_dashboard successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_dashboard failed: {e}")
            excel_manager.update_info(alias, f"get_dashboard failed: {e}")
            return False

        try:
            response = self.get_status()
            log_and_print(f"{alias} prepare get_status successfully ")
        except Exception as e:
            log_and_print(f"{alias} prepare get_status failed: {e}")
            excel_manager.update_info(alias, f"prepare get_status failed: {e}")
            return False

        try:
            response = self.get_profile()
            log_and_print(f"{alias}  get_profile successfully ")
        except Exception as e:
            log_and_print(f"{alias}  get_profile failed: {e}")
            excel_manager.update_info(alias, f" get_profile failed: {e}")
            return False

        try:
            response = self.get_point()
            points = response['pointTotal']
            log_and_print(f"{alias}  first get_point successfully ")
        except Exception as e:
            log_and_print(f"{alias} first get_point failed: {e}")
            excel_manager.update_info(alias, f"first get_point failed: {e}")
            return False

        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 1:
            try:
                response = self.post_chat()
                if response == None or response['success'] == False:
                    self.ischatDone = True
                log_and_print(f"{alias} 1  post_chat successfully self.ischatDone = {self.ischatDone}")
            except Exception as e:
                log_and_print(f"{alias} 1 post_chat failed: {e}")
                excel_manager.update_info(alias, f" post_chat failed: {e}")
                return False

        try:
            response = self.get_profile()
            log_and_print(f"{alias}  get_profile successfully ")
        except Exception as e:
            log_and_print(f"{alias}  get_profile failed: {e}")
            excel_manager.update_info(alias, f" get_profile failed: {e}")
            return False


        try:
            response = self.post_nft()
            log_and_print(f"{alias}  post_nft successfully")
        except Exception as e:
            log_and_print(f"{alias}  post_nft failed: {e}")
            excel_manager.update_info(alias, f" post_nft failed: {e}")
            return False

        try:
            response = self.post_chat()
            if response == None or response['success'] == False:
                self.ischatDone = True
            log_and_print(f"{alias} 2  post_chat successfully self.ischatDone = {self.ischatDone}")
        except Exception as e:
            log_and_print(f"{alias} 2 post_chat failed: {e}")
            excel_manager.update_info(alias, f" post_chat failed: {e}")
            return False

        try:
            response = self.get_dashboard()
            log_and_print(f"{alias} get_dashboard successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_dashboard failed: {e}")
            excel_manager.update_info(alias, f"get_dashboard failed: {e}")
            return False

        try:
            response = self.post_chat()
            if response == None or response['success'] == False:
                self.ischatDone = True
            log_and_print(f"{alias} 3  post_chat successfully self.ischatDone = {self.ischatDone}")
        except Exception as e:
            log_and_print(f"{alias} 3 post_chat failed: {e}")
            excel_manager.update_info(alias, f" post_chat failed: {e}")
            return False

        try:
            response = self.get_mygallery()
            log_and_print(f"{alias} get_mygallery successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_mygallery failed: {e}")
            excel_manager.update_info(alias, f"get_mygallery failed: {e}")
            return False

        try:
            response = self.post_chat()
            if response == None or response['success'] == False:
                self.ischatDone = True
            log_and_print(f"{alias} 4  post_chat successfully self.ischatDone = {self.ischatDone}")
        except Exception as e:
            log_and_print(f"{alias} 4 post_chat failed: {e}")
            excel_manager.update_info(alias, f" 4 post_chat failed: {e}")
            return False

        try:
            response = self.get_mygallery()
            log_and_print(f"{alias} get_mygallery successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_mygallery failed: {e}")
            excel_manager.update_info(alias, f"get_mygallery failed: {e}")
            return False


        try:
            response = self.post_chat()
            if response == None or response['success'] == False:
                self.ischatDone = True
            log_and_print(f"{alias} 5  post_chat successfully self.ischatDone = {self.ischatDone}")
        except Exception as e:
            log_and_print(f"{alias} 5 post_chat failed: {e}")
            excel_manager.update_info(alias, f" 5 post_chat failed: {e}")
            return False


        try:
            response = self.get_status()
            isAttendanceToday = response['data']['isAttendanceToday']
            log_and_print(f"{alias} frist get_status successfully ")
        except Exception as e:
            log_and_print(f"{alias} frist get_status failed: {e}")
            excel_manager.update_info(alias, f"frist get_status failed: {e}")
            return False

        # if isAttendanceToday == 0:
        #     try:
        #         response = self.post_attendance()
        #         if response['success'] == True:
        #             log_and_print(f"{alias} post_attendance successfully ")
        #         else:
        #             raise Exception(f"Error: {response}")
        #     except Exception as e:
        #         log_and_print(f"{alias} post_attendance failed: {e}")
        #         excel_manager.update_info(alias, f"post_attendance failed: {e}")
        #         return False

        try:
            response = self.get_profile()
            log_and_print(f"{alias} get_profile successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_profile failed: {e}")
            excel_manager.update_info(alias, f"get_profile failed: {e}")
            return False

        try:
            time.sleep(2)
            response = self.get_status()
            isAttendanceToday = response['data']['isAttendanceToday']
            log_and_print(f"{alias} second get_status successfully ")
        except Exception as e:
            log_and_print(f"{alias} second get_status failed: {e}")
            excel_manager.update_info(alias, f"second get_status failed: {e}")
            return False

        try:
            response = self.get_point()
            points = response['pointTotal']
            log_and_print(f"{alias} AttendanceToday successfully isAttendanceToday = {isAttendanceToday} points = {points}")
            excel_manager.update_info(alias, f"AttendanceToday successfully isAttendanceToday = {isAttendanceToday} points = {points}")
        except Exception as e:
            log_and_print(f"{alias} second get_point failed: {e}")
            excel_manager.update_info(alias, f"second get_point failed: {e}")
            return False

if __name__ == '__main__':
    proxyApp = socket5SwitchProxy(logger = log_and_print)
    failed_list = []
    retry_list = [] 
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("GenomefiGM", log_and_print)
    client_key = UserInfoApp.find_yesCaptch_clientkey()
    app = GenomefiGM()

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
