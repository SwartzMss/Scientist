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

    def find_yesCaptch_clientkey(self):
        try:
            # 从文件中加载JSON数据
            with open(self.accountfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            return data.get("YesCaptchClientKey", None)
            
        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File '{accountfile_path}' not found")
        return None

    def find_user_outlook_token(self, exclude=None):
        credentials_list = []
        try:
            with open(self.accountfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for user in data["users"]:
                if "exception" in user and ("ALL" in user["exception"] or (exclude is not None and exclude in user["exception"])):
                    continue
                alias = user.get("alias")
                accounts = user.get("accounts", {})
                if "outlook" in accounts:
                    account = accounts["outlook"]
                    username = account.get("username")
                    access_token = account.get("access_token")
                    refresh_token = account.get("refresh_token")

                    # 如果access_token或refresh_token不存在，可以选择跳过或添加默认值
                    if access_token is None or refresh_token is None or username is None:
                        continue

                    credentials_list.append({"alias": alias, "username": username,"access_token": access_token, "refresh_token": refresh_token})

        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File '{accountfile_path}' not found")

        return credentials_list


    def find_username_and_password_by_alias_in_file(self, alias):
        try:
            # 从文件中加载JSON数据
            with open(self.accountfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # 遍历用户列表，查找对应的proxy
            for user in data.get("users", []):
                if user['alias'] == alias:
                    # 获取并返回用户名和密码
                    account_info = user['accounts']['outlook']
                    return account_info['username'], account_info['password']
            
        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File '{accountfile_path}' not found")
        return None,None

    def find_proxy_by_alias_in_file(self, alias):
        try:
            # 从文件中加载JSON数据
            with open(self.accountfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # 遍历用户列表，查找对应的proxy
            for user in data.get("users", []):
                if user.get("alias") == alias:
                    return user.get("proxy", [])
            
        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File '{accountfile_path}' not found")
        return []
    
    def find_user_credentials_for_eth(self, exclude=None):
        credentials_list = []
        try:
            with open(self.accountfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for user in data["users"]:
                # 跳过包含排除项的账户
                if "exception" in user and ("ALL" in user["exception"] or (exclude is not None and exclude in user["exception"])):
                    continue
                alias = user.get("alias")
                accounts = user.get("accounts", {})
                if "eth" in accounts:
                    account = accounts["eth"]
                    key = account.get("key")
                    # 如果access_token或refresh_token不存在，可以选择跳过或添加默认值
                    if key is None:
                        continue  

                    credentials_list.append({"alias": alias, "key": key})

        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File '{accountfile_path}' not found")

        return credentials_list

    def find_user_credentials_for_app(self, exclude=None):
        credentials_list = []
        try:
            with open(self.accountfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for user in data["users"]:
                 # 跳过包含排除项的账户
                if "exception" in user and ("ALL" in user["exception"] or (exclude is not None and exclude in user["exception"])):
                    continue
                alias = user.get("alias")
                accounts = user.get("accounts", {})
                if "APP" in accounts:
                    account = accounts["APP"]
                    index = account.get("index")
                    devid = account.get("devid")
                    # 如果access_token或refresh_token不存在，可以选择跳过或添加默认值
                    if index is None or devid is None:
                        continue  

                    credentials_list.append({"alias": alias, "index": index, "devid": devid})

        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File '{accountfile_path}' not found")

        return credentials_list