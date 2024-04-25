from eth_account.messages import encode_defunct
import time
import math
import sys
import web3
import requests
import random
import datetime
import json
from fake_useragent import UserAgent
import os
from dotenv import load_dotenv
load_dotenv()

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

# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\AnalogDCFaucet_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')

class AnalogDCFaucet:
    def __init__(self):
        self.session = None
        self.headers = {
        'authority': 'discord.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'authorization': '',
        'origin': 'https://discord.com',
        'referer': 'https://discord.com/channels/860069399627825163/1139090696175886376',
        'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'x-debug-options': 'bugReporterEnabled',
        'x-discord-locale': 'zh-CN',
        'x-discord-timezone': 'Asia/Shanghai',
        'Content-Type': 'application/json'
        }


    def create_new_session(self,proxyinfo):
        ua = UserAgent()
        self.headers['user-agent'] = ua.random
        self.headers.pop('Authorization', None)
        self.session = requests.Session()
        self.session.cookies.clear()
        self.session.proxies = proxyinfo

    def generate_nonce(self):
        s = 1420070400000

        def o(e):
            t = e - s
            if t <= 0:
                return "0"
            else:
                # 在Python中，对整数使用左移运算符 `<<` 来实现位左移
                return str(t << 22)

        # 获取当前时间的毫秒数
        current_millis = int(time.time() * 1000)
        return o(current_millis)

    def faucet(self, address):
        self.headers['authorization'] = "MTA3MDg4MTcyNTI1MDU0MzYyNg.GJFIQN.pM1qVW_CQ1Wv9VAMYRji2Bg-47Iwl8z8jSce9g"
        url = f"https://discord.com/api/v9/channels/1139090696175886376/messages"
        payload ={
            "content":  f"!faucet {address}",
            "flags": 0,
            "mobile_network_type": "unknown",
            "nonce": self.generate_nonce(),
            "tts": False
        }
        response = self.session.post(
            url, headers=self.headers,json=payload, timeout=60)
        data = response.json()
        log_and_print(f"{self.alias} post_login data:{data}")
        return data

    def run(self,alias, address,proxyinfo):
        self.alias = alias
        self.create_new_session(proxyinfo)
        self.faucet(address)


if __name__ == '__main__':
    app = AnalogDCFaucet()
    proxyApp = socket5SwitchProxy(logger = log_and_print)
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("AnalogDCFaucet", log_and_print)
    alais_list = UserInfoApp.find_alias_by_path()
    for alias in alais_list:
        log_and_print(f"statring running by alias {alias}")

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
        address = "an95DuPTMzfvWCv4Nv4BJjNp3bu9JTM56KBjiebaJZ5qrS2xb"
        app.run(alias, address, proxyinfo)
