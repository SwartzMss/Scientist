import os
import time
import sys
import re
import requests
from oauth2EmailSearch import oauth2EmailSearch
import datetime
import random
import json

# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# 现在可以从tools目录导入UserInfo
from tools.UserInfo import UserInfo

# 现在可以从tools目录导入excelWorker
from tools.excelWorker import excelWorker
from tools.switchProxy import ClashAPIManager
# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\ChainingGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class ChainingGM:
    def __init__(self):
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
        self.code = None
        self.session = None

    def create_new_session(self):
        self.session = requests.Session()

    def getpoints(self):
        url = f"https://api.chainingview.io/api/user/myDetails/userEnergyCount"
        response = self.session.get(url, headers=self.headers, timeout=10)
        response = response.json()
        #log_and_print(f"response:{response}")
        return response

    def login(self,username, code):
        url = f"https://api.chainingview.io/api/user/login"
        data={
            "email": username,
            "dynamicCode": code
        }
        response = self.session.post(
            url,json=data, timeout=10)
        data = response.json()
        #log_and_print(f"response:{response}")
        return data

    def getMyDetails(self):
        url = f"https://api.chainingview.io/api/user/myDetails/getMyDetails"
        response = self.session.get(url, headers=self.headers, timeout=10)
        response = response.json()
        #log_and_print(f"response:{response}")
        return response


    def getcount(self):
        url = f"https://api.chainingview.io/api/user/userMission/count"
        response = self.session.get(url, headers=self.headers, timeout=10)
        response = response.json()
        #log_and_print(f"response:{response}")
        return response


    def countdown(self):
        url = f"https://api.chainingview.io/api/user/config/countdown"
        form_data = {}
        response = self.session.post(url,data=form_data, headers=self.headers, timeout=10)
        response = response.json()
        #log_and_print(f"response:{response}")
        return response

    def sign(self):
        url = f"https://api.chainingview.io/api/user/myDetails/sign"
        response = self.session.get(url, headers=self.headers, timeout=10)
        response = response.json()
        #log_and_print(f"response:{response}")
        return response

    #请求发送验证码
    def requestSendCode(self, username):
        form_data = {
            'msgId': '102',
            'email': username
        }

        url = f"https://api.chainingview.io/api/user/email_code"
        response = self.session.post(url,data=form_data, timeout=10)
        data = response.json()
        #log_and_print(f"response:{response}")
        return data

    def run(self, alias, username, access_token, refresh_token):
        self.create_new_session()
        time.sleep(1)
        try:
            response = self.requestSendCode(username)
            if response.get('code') != 200:
                if response.get('code') == 500:
                    time.sleep(30)
                raise Exception(f"Error: Response is {response}")
            log_and_print(f"requestSendCode successfully username = {alias}")
        except Exception as e:
            log_and_print(f"requestSendCode failed username = {alias}, msg: {e}")
            excel_manager.update_info(alias, f"requestSendCode failed msg: {e}")
            return False

        try:
            emailSearcher = oauth2EmailSearch(subject = 'Chaining View', code_length = 6, logger = log_and_print, access_token = access_token, refresh_token = refresh_token)
            code = emailSearcher.search_email_by_subject()
            if code == None:
                raise Exception("Error: cannot find verifi code")
            self.code = code
            log_and_print(f"search_email_by_subject successfully username = {alias}")
        except Exception as e:
            log_and_print(f"search_email_by_subject failed username = {alias}, msg: {e}")
            excel_manager.update_info(alias, f"search_email_by_subject failed msg: {e}")
            return False
        
        try:
            response = self.login(username, self.code)
            if response.get('code') != 200:
                raise Exception(f"Error: Response  is {response}")
            token = response['data']['token']
            self.headers['authorization'] = 'Bearer ' + token
            log_and_print(f"login successfully username = {alias}")
        except Exception as e:
            log_and_print(f"login failed username = {alias}, msg: {e}")
            excel_manager.update_info(alias, f"login failed failed msg: {e}")
            return False

        try:
            response = self.getMyDetails()
            if response.get('code') != 200:
                raise Exception(f"Error: Response is {response}")
            isWalletBind = False
            if response.get("data", {}).get("user", {}).get("address"):
                isWalletBind = Ture
            log_and_print(f"getMyDetails successfully username = {alias} ")
        except Exception as e:
            excel_manager.update_info(alias, f"getMyDetails failed failed msg: {e}")
            log_and_print(f"getMyDetails failed username = {alias}, msg: {e}")
            return False

        try:
            response = self.getpoints()
            if response.get('code') != 200:
                raise Exception(f"Error: Response is {response}")
            today_energy = response.get('data', {}).get('todayEnergy', 0)
            if today_energy != 0:
                log_and_print(f"already singed successfully username = {alias}")
                excel_manager.update_info(alias, "already sign successfully")
                return True
        except Exception as e:
            log_and_print(f"getpoints failed username = {alias}, msg: {e}")
            excel_manager.update_info(alias, f"getpoints failed msg: {e}")
            return False

        try:
            response = self.getcount()
            if response.get('code') != 200:
                raise Exception(f"Error: Response is {response}")
            log_and_print(f"getcount successfully username = {alias}")
        except Exception as e:
            log_and_print(f"getcount failed username = {alias}, msg: {e}")
            excel_manager.update_info(alias, f"getcount failed msg: {e}")
            return False

        try:
            response = self.countdown()
            if response.get('code') != 200:
                raise Exception(f"Error: Response is {response}")
            log_and_print(f"countdown successfully username = {alias}")
        except Exception as e:
            log_and_print(f"countdown failed username = {alias}, msg: {e}")
            excel_manager.update_info(alias, f"countdown failed msg: {e}")
            return False

        try:
            response = self.sign()
            if response.get('code') != 200:
                raise Exception(f"Error: Response is {response}")
            log_and_print(f"sign successfully username = {alias} isWalletBind = {isWalletBind}")
            excel_manager.update_info(alias, f"sign successfully isWalletBind = {isWalletBind}")
            return True
        except Exception as e:
            log_and_print(f"sign failed username = {alias}, msg: {e}")
            excel_manager.update_info(alias, f"sign failed msg: {e}")
            return False
        


if __name__ == '__main__':
    app = ChainingGM()
    UserInfoApp = UserInfo(log_and_print)
    retry_list = [] 
    proxyApp = ClashAPIManager(logger = log_and_print)
    excel_manager = excelWorker("ChainingGM", log_and_print)
    credentials_list = UserInfoApp.find_user_outlook_token("ChainingGM")
    for credentials in credentials_list:
        alias = credentials["alias"]
        username = credentials["username"]
        access_token = credentials["access_token"]
        refresh_token = credentials["refresh_token"]

        proxyName = UserInfoApp.find_proxy_by_alias_in_file(alias)
        if not proxyName:
            log_and_print(f"cannot find proxy username = {alias}")
            continue
        if proxyApp.change_proxy_until_success(proxyName) == False:
            continue
        time.sleep(5)   
        if(app.run(alias, username, access_token, refresh_token) == False):
            retry_list.append((alias, username, access_token, refresh_token))


    if len(retry_list) != 0:
        log_and_print("start retry faile case")
        time.sleep(60)
    failed_list = []
    for alias, username, access_token, refresh_token in retry_list:
        if(app.run(alias, username, access_token, refresh_token) == False):
            failed_list.append(username)

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")
    else:
        for username in failed_list:
            log_and_print(f"final failed username = {username}")
    excel_manager.save_msg_and_stop_service()



