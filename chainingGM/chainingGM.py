import os
import time
import re
import requests
from EmailSearcher import EmailSearcher
import datetime

import json

# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\ChainingGM_{current_time}.log'

accountfile_path = rf'\\192.168.3.142\SuperWind\Study\account.json'

def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a') as log_file:
        print(message)
        log_file.write(message + '\n')



def find_user_credentials(category, exclude=None):
    credentials_list = []
    try:
        with open(accountfile_path, 'r') as file:
            data = json.load(file)

        for user in data["users"]:
            accounts = user["accounts"]
            if category in accounts and (exclude is None or exclude not in accounts[category]["exception"]):
                username = accounts[category]["username"]
                password = accounts[category]["password"]
                credentials_list.append({"username": username, "password": password})

    except json.JSONDecodeError:
        log_and_print("Invalid JSON data")
    except KeyError as e:
        log_and_print(f"Missing key in JSON data: {e}")
    except FileNotFoundError:
        log_and_print(f"File '{accountfile_path}' not found")

    return credentials_list



class ChainingGM:
    def __init__(self, emailSearcher):
        self.session = requests.Session()
        self.emailSearcher = emailSearcher
        self.headers = {}
        self.code = None

    def getpoints():
        url = f"https://api.chainingview.io/api/user/myDetails/userEnergyCount"
        response = self.session.get(url, headers=self.headers, timeout=60)
        response = response.json()
        log_and_print(f"response:{response}")
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
        log_and_print(f"response:{response}")
        return data


    def sign(self):
        url = f"https://api.chainingview.io/api/user/myDetails/sign"
        response = self.session.get(url, headers=self.headers, timeout=60)
        response = response.json()
        log_and_print(f"response:{response}")
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
        log_and_print(f"response:{response}")
        return data

    def run(self, username, password):
        try:
            response = self.requestSendCode(username)
            if response.get('code') != 200:
                if response.get('code') == 500:
                    time.sleep(15)
                raise Exception(f"Error: Response is {response}")
            log_and_print(f"requestSendCode successfully username = {username}")
        except Exception as e:
            log_and_print(f"requestSendCode failed username = {username}, msg: {e}")
            return False

        try:
            code = self.emailSearcher.search_email_by_subject(username, password)
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
            response = self.sign()
            if response.get('code') != 200 and response.get('code') != 500:
                raise Exception(f"Error: Response is {response}")
            log_and_print(f"sign successfully username = {username}")
        except Exception as e:
            log_and_print(f"sign failed username = {username}, msg: {e}")
            return False
        return True


if __name__ == '__main__':
    emailSearcher= EmailSearcher(subject = 'Chaining View', code_length = 6, logger = log_and_print)
    app = ChainingGM(emailSearcher)
    retry_list = []
    credentials_list = find_user_credentials("outlook", "ChainingGM")

    # 遍历账户列表并处理每个账户
    for credentials in credentials_list:
        username = credentials["username"]
        password = credentials["password"]
        if(app.run(username, password) == False):
            retry_list.append((username, password))
    failed_list = []
    for username, password in retry_list:
        if(app.run(username, password) == False):
            failed_list.append((username, password))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for username, password in failed_list:
        log_and_print(f"final failed username = {username}")

