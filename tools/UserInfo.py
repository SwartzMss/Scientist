import os
import time
import sys
import re
import datetime
import random
import json

captchfile_path = rf'\\192.168.3.142\SuperWind\Study\account_config\account_captch.json'
socket5proxyfile_path = rf'\\192.168.3.142\SuperWind\Study\account_config\account_socket5proxy.json'
clashproxyfile_path = rf'\\192.168.3.142\SuperWind\Study\account_config\account_clashproxy.json'
emailfile_path = rf'\\192.168.3.142\SuperWind\Study\account_config\account_email.json'
ethfile_path = rf'\\192.168.3.142\SuperWind\Study\account_config\account_eth.json'
solfile_path = rf'\\192.168.3.142\SuperWind\Study\account_config\account_sol.json'
appfile_path = rf'\\192.168.3.142\SuperWind\Study\account_config\account_app.json'
dcfile_path = rf'\\192.168.3.142\SuperWind\Study\account_config\account_dc.json'
analogfile_path = rf'\\192.168.3.142\SuperWind\Study\account_config\account_analog.json'
default_account_path = rf'\\192.168.3.142\SuperWind\Study\account_config\default_account.json'

def simplePrint(text):
    print(text)

class UserInfo:
    def __init__(self, logger = simplePrint):
        self.logger = logger  # logger 参数是传递给类的 log_and_print 函数

    def find_yesCaptch_clientkey(self):
        try:
            # 从文件中加载JSON数据
            with open(captchfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            return data.get("YesCaptchClientKey", None)
            
        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File {captchfile_path} not found")
        return None

    def find_2Captch_clientkey(self):
        try:
            # 从文件中加载JSON数据
            with open(captchfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            return data.get("2captcha", None)
            
        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File {captchfile_path} not found")
        return None

    def find_alias_by_path(self, config_file = default_account_path):
        alias_list = []
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            for item in data:
                alias = item.get("alias")  # 使用get方法安全地获取别名
                if alias:  # 确保别名存在
                    alias_list.append(alias)

        except json.JSONDecodeError:
            self.logger("Invalid JSON data")
        except KeyError as e:
            self.logger(f"Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File {config_file} not found")
        random.shuffle(alias_list)  # 打乱顺序
        return alias_list

    def find_socket5proxy_by_alias_in_file(self, alias):
        try:
            # 从文件中加载JSON数据
            with open(socket5proxyfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # 遍历用户列表，查找对应的proxy
            for user in data.get("users", []):
                if user.get("alias") == alias:
                    return user.get("proxy", [])
            
        except json.JSONDecodeError:
            self.logger(f"File {socket5proxyfile_path} Invalid JSON data")
        except KeyError as e:
            self.logger(f"File {socket5proxyfile_path} Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File {socket5proxyfile_path} not found")
        return []


    def find_clashproxy_by_alias_in_file(self, alias):
        try:
            # 从文件中加载JSON数据
            with open(clashproxyfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # 遍历用户列表，查找对应的proxy
            for user in data.get("users", []):
                if user.get("alias") == alias:
                    return user.get("proxy", [])
            
        except json.JSONDecodeError:
            self.logger(f"File {clashproxyfile_path} Invalid JSON data")
        except KeyError as e:
            self.logger(f"File {clashproxyfile_path} Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File {clashproxyfile_path} not found")
        return []

    def find_outlookinfo_by_alias_in_file(self, alias):
        try:
            # 从文件中加载JSON数据
            with open(emailfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            for user in data.get("users", []):
                if user['alias'] == alias:
                    # 获取并返回用户名和密码
                    account_info = user['outlook']
                    return account_info['username'], account_info['password'], account_info['access_token'], account_info['refresh_token']
            
        except json.JSONDecodeError:
            self.logger(f"File {emailfile_path}  Invalid JSON data")
        except KeyError as e:
            self.logger(f" File {emailfile_path}  Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File {emailfile_path} not found")
        return None,None,None,None

    def find_solinfo_by_alias_in_file(self, alias):
        try:
            with open(solfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for user in data.get("users", []):
                if user['alias'] == alias:
                    eth_info = user['eth']
                    return eth_info['key']

        except json.JSONDecodeError:
            self.logger(f"File {solfile_path}  Invalid JSON data")
        except KeyError as e:
            self.logger(f"File {solfile_path}  Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File {solfile_path} not found")
        return None

    def find_ethinfo_by_alias_in_file(self, alias):
        try:
            with open(ethfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for user in data.get("users", []):
                if user['alias'] == alias:
                    eth_info = user['eth']
                    return eth_info['key']

        except json.JSONDecodeError:
            self.logger(f"File {ethfile_path}  Invalid JSON data")
        except KeyError as e:
            self.logger(f"File {ethfile_path}  Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File {ethfile_path} not found")
        return None    

    
    def find_analoginfo_by_alias_in_file(self, alias):
        try:
            with open(analogfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for user in data.get("users", []):
                if user['alias'] == alias:
                    eth_info = user['eth']
                    return eth_info['key']

        except json.JSONDecodeError:
            self.logger(f"File {analogfile_path}  Invalid JSON data")
        except KeyError as e:
            self.logger(f"File {analogfile_path}  Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File {analogfile_path} not found")
        return None

    def find_dcinfo_by_alias_in_file(self, alias):
        try:
            with open(dcfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for user in data.get("users", []):
                if user['alias'] == alias:
                    eth_info = user['token']
                    return eth_info['key']

        except json.JSONDecodeError:
            self.logger(f"File {dcfile_path}  Invalid JSON data")
        except KeyError as e:
            self.logger(f"File {dcfile_path}  Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File {dcfile_path} not found")
        return None

    def find_appinfo_by_alias_in_file(self, alias):
        try:
            with open(appfile_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            for user in data.get("users", []):
                if user['alias'] == alias:
                    # 获取并返回用户名和密码
                    app_info = user['APP']
                    return app_info['index'], app_info['devid']

        except json.JSONDecodeError:
            self.logger(f" File {appfile_path} Invalid JSON data")
        except KeyError as e:
            self.logger(f"File {appfile_path} Missing key in JSON data: {e}")
        except FileNotFoundError:
            self.logger(f"File {appfile_path} not found")
        return None,None



if __name__ == '__main__':
    app = UserInfo()
    clientkey = app.find_yesCaptch_clientkey()
    simplePrint(clientkey)
    alais_list = app.find_alias_by_path(rf'\\192.168.3.142\SuperWind\Study\account_config\berachain.json')
    for alais in alais_list:
        # simplePrint(alais)
        # index,password = app.find_appinfo_by_alias_in_file(alais)
        # simplePrint(f"alais = {alais} index = {index} password = {password}")
        # key = app.find_ethinfo_by_alias_in_file(alais)
        # simplePrint(f"alais = {alais} key = {key}")
        # usrname,passwd,accesstoken,refreshtoken = app.find_outlookinfo_by_alias_in_file(alais)
        # simplePrint(f"alais = {alais} usrname = {usrname} passwd = {passwd} accesstoken = {accesstoken} refreshtoken = {refreshtoken}")
        proxyList = app.find_socket5proxy_by_alias_in_file(alais)
        for proxy in proxyList:
            simplePrint(f"alais = {alais} proxy = {proxy}")
        proxyList = app.find_clashproxy_by_alias_in_file(alais)
        for proxy in proxyList:
            simplePrint(f"alais = {alais} proxy = {proxy}")