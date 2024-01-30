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

# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\ChainingGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a') as log_file:
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
        response = self.session.get(url, headers=self.headers, timeout=60)
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
            url,json=data, timeout=60)
        data = response.json()
        #log_and_print(f"response:{response}")
        return data

    def getMyDetails(self):
        url = f"https://api.chainingview.io/api/user/myDetails/getMyDetails"
        response = self.session.get(url, headers=self.headers, timeout=60)
        response = response.json()
        #log_and_print(f"response:{response}")
        return response


    def getcount(self):
        url = f"https://api.chainingview.io/api/user/userMission/count"
        response = self.session.get(url, headers=self.headers, timeout=60)
        response = response.json()
        #log_and_print(f"response:{response}")
        return response


    def countdown(self):
        url = f"https://api.chainingview.io/api/user/config/countdown"
        form_data = {}
        response = self.session.post(url,data=form_data, headers=self.headers, timeout=60)
        response = response.json()
        #log_and_print(f"response:{response}")
        return response

    def sign(self):
        url = f"https://api.chainingview.io/api/user/myDetails/sign"
        response = self.session.get(url, headers=self.headers, timeout=60)
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
        response = self.session.post(url,data=form_data, timeout=60)
        data = response.json()
        #log_and_print(f"response:{response}")
        return data

    def run(self, username, access_token, refresh_token):
        self.create_new_session()
        try:
            response = self.requestSendCode(username)
            if response.get('code') != 200:
                if response.get('code') == 500:
                    time.sleep(30)
                raise Exception(f"Error: Response is {response}")
            log_and_print(f"requestSendCode successfully username = {username}")
        except Exception as e:
            log_and_print(f"requestSendCode failed username = {username}, msg: {e}")
            return False

        try:
            emailSearcher = oauth2EmailSearch(subject = 'Chaining View', code_length = 6, logger = log_and_print, access_token = access_token, refresh_token = refresh_token)
            code = emailSearcher.search_email_by_subject()
            if code == None:
                raise Exception("Error: cannot find verifi code")
            self.code = code
            log_and_print(f"search_email_by_subject successfully username = {username}")
        except Exception as e:
            log_and_print(f"search_email_by_subject failed username = {username}, msg: {e}")
            return False
        
        try:
            response = self.login(username, self.code)
            if response.get('code') != 200:
                raise Exception(f"Error: Response  is {response}")
            token = response['data']['token']
            self.headers['authorization'] = 'Bearer ' + token
            log_and_print(f"login successfully username = {username}")
        except Exception as e:
            log_and_print(f"login failed username = {username}, msg: {e}")
            return False

        try:
            response = self.getMyDetails()
            if response.get('code') != 200:
                raise Exception(f"Error: Response is {response}")
            log_and_print(f"getMyDetails successfully username = {username}")
        except Exception as e:
            log_and_print(f"getMyDetails failed username = {username}, msg: {e}")
            return False

        try:
            response = self.getpoints()
            if response.get('code') != 200:
                raise Exception(f"Error: Response is {response}")
            today_energy = response.get('data', {}).get('todayEnergy', 0)
            if today_energy != 0:
                log_and_print(f"already singed successfully username = {username}")
                return True
        except Exception as e:
            log_and_print(f"getpoints failed username = {username}, msg: {e}")
            return False

        try:
            response = self.getcount()
            if response.get('code') != 200:
                raise Exception(f"Error: Response is {response}")
            log_and_print(f"getcount successfully username = {username}")
        except Exception as e:
            log_and_print(f"getcount failed username = {username}, msg: {e}")
            return False

        try:
            response = self.countdown()
            if response.get('code') != 200:
                raise Exception(f"Error: Response is {response}")
            log_and_print(f"countdown successfully username = {username}")
        except Exception as e:
            log_and_print(f"countdown failed username = {username}, msg: {e}")
            return False

        try:
            response = self.sign()
            if response.get('code') != 200:
                raise Exception(f"Error: Response is {response}")
            log_and_print(f"sign successfully username = {username}")
            excel_manager.update_info(username, "sign successfully")
        except Exception as e:
            log_and_print(f"sign failed username = {username}, msg: {e}")
            return False
        return True


if __name__ == '__main__':
    app = ChainingGM()
    UserInfoApp = UserInfo(log_and_print)
    app = ChainingGM()
    retry_list = []

    excel_manager = excelWorker("ChainingGM", log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_chaining("outlook", "ChainingGM")
    for credentials in credentials_list:
        username = credentials["username"]
        access_token = credentials["access_token"]
        refresh_token = credentials["refresh_token"]
        if(app.run(username, access_token, refresh_token) == False):
            retry_list.append((username, access_token, refresh_token))

    failed_list = []
    time.sleep(60)
    log_and_print("start retry faile cause")
    for username, access_token, refresh_token in retry_list:
        if(app.run(username, access_token, refresh_token) == False):
            failed_list.append((username, password))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for username, access_token, refresh_token in failed_list:
        log_and_print(f"final failed username = {username}")
        excel_manager.update_info(username, "sign failed")
    excel_manager.save_msg_and_stop_service()



