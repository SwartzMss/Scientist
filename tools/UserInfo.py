import os
import time
import sys
import re
import datetime
import random
import json

accountfile_path = rf'\\192.168.3.142\SuperWind\Study\account.json'



class UserInfo:
    def __init__(self, logger, accountfile_path = rf'\\192.168.3.142\SuperWind\Study\account.json'):
        self.accountfile_path = accountfile_path
        self.logger = logger  # logger 参数是传递给类的 log_and_print 函数

    def find_user_credentials_for_chaining(self, category, exclude=None):
        credentials_list = []
        try:
            with open(self.accountfile_path, 'r') as file:
                data = json.load(file)

            for user in data["users"]:
                accounts = user.get("accounts", {})
                if category in accounts:
                    account = accounts[category]
                    # 跳过包含排除项的账户
                    if exclude is not None and "exception" in account and exclude in account["exception"]:
                        continue

                    username = account.get("username")
                    access_token = account.get("access_token")
                    refresh_token = account.get("refresh_token")

                    # 如果access_token或refresh_token不存在，可以选择跳过或添加默认值
                    if access_token is None or refresh_token is None:
                        continue  # 或者使用默认值，例如 access_token = access_token or "default_value"

                    credentials_list.append({"username": username, "access_token": access_token, "refresh_token": refresh_token})

        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File '{accountfile_path}' not found")

        return credentials_list

    def find_user_credentials_for_interact(self, category, exclude=None):
        credentials_list = []
        try:
            with open(self.accountfile_path, 'r') as file:
                data = json.load(file)

            for user in data["users"]:
                username = user.get("alias")
                accounts = user.get("accounts", {})
                if category in accounts:
                    account = accounts[category]
                    # 跳过包含排除项的账户
                    if exclude is not None and "exception" in account and exclude in account["exception"]:
                        continue
                    access_token = account.get("key")
                    # 如果access_token或refresh_token不存在，可以选择跳过或添加默认值
                    if access_token is None:
                        continue  

                    credentials_list.append({"username": username, "access_token": access_token})

        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File '{accountfile_path}' not found")

        return credentials_list
    
    def find_user_credentials_for_reiki(self, category, exclude=None):
        credentials_list = []
        try:
            with open(self.accountfile_path, 'r') as file:
                data = json.load(file)

            for user in data["users"]:
                username = user.get("alias")
                proxy = user.get("proxy")
                accounts = user.get("accounts", {})
                if category in accounts:
                    account = accounts[category]
                    # 跳过包含排除项的账户
                    if exclude is not None and "exception" in account and exclude in account["exception"]:
                        continue
                    access_token = account.get("key")
                    # 如果access_token或refresh_token不存在，可以选择跳过或添加默认值
                    if access_token is None:
                        continue  

                    credentials_list.append({"username": username, "access_token": access_token})

        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File '{accountfile_path}' not found")

        return credentials_list