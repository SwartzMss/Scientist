
#https://www.intract.io

from eth_account.messages import encode_defunct
import time
import math
import sys
import web3
import requests
import random
import datetime
import json
import os
from dotenv import load_dotenv
load_dotenv()



# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\IntractSign_{current_time}.log'

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
        log_and_print("Invalid JSON data")
    except KeyError as e:
        log_and_print(f"Missing key in JSON data: {e}")
    except FileNotFoundError:
        log_and_print(f"File '{accountfile_path}' not found")

    return credentials_list

class IntractSign:
    def __init__(self):
        self.userName = None
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
            'Referer': 'https://www.intract.io/?referralCode=raF4SD&referralSource=REFERRAL_PAGE&referralLink=https%3A%2F%2Fwww.intract.io%2Freferral',
        }

    # 获取 nonce
    def get_nonce(self):
        url = f"https://api.intract.io/api/qv1/auth/generate-nonce"
        data={
            "walletAddress": self.account.address
        }
        response = session.post(
            url,json=data, timeout=60)
        data = response.json()
        return data

    def _sign_message(self,nonce):
        log_and_print('wallet:' + str(self.account.address))
        msg = f"Please sign this message to verify your identity. Nonce: {nonce}"
        res = self.account.sign_message(encode_defunct(text=msg))
        return res.signature.hex()


    def gm(self):
        url = f"https://api.intract.io/api/qv1/auth/gm-streak"
        response = session.post(url, headers=self.headers, timeout=60)
        data = response.json()
        log_and_print(f"xxxxx {data} ")
        return data

    def wallet(self,hex):
        url = f"https://api.intract.io/api/qv1/auth/wallet"
        data={
            "signature": hex,
            "userAddress": self.account.address,
            "chain": {
                "id": 56,
                "name": "BNB Smart Chain",
                "network": "BNB Smart Chain",
                "nativeCurrency": {
                    "decimals": 18,
                    "name": "BNB",
                    "symbol": "BNB"
                },
                "rpcUrls": {
                    "public": {
                        "http": ["https://bsc-dataseed1.bnbchain.org"]
                    },
                    "default": {
                        "http": ["https://snowy-wild-pallet.bsc.discover.quiknode.pro/5fdc7ecdeddbeaf85dd75144e556935542f04a18/"]
                    }
                },
                "blockExplorers": {
                    "etherscan": {
                        "name": "BscScan",
                        "url": "https://bscscan.com/"
                    },
                    "default": {
                        "name": "BscScan",
                        "url": "https://bscscan.com/"
                    }
                },
                "unsupported": False
            },
            "isTaskLogin": False,
            "width": "590px",
            "reAuth": False,
            "connector": "metamask",
            "referralCode": None,
            "referralLink": None,
            "referralSource": None
        }
        response = session.post(
            url,json=data, timeout=60)
        set_cookie_string = response.headers.get('set-cookie')
        start = set_cookie_string.find("auth-token=")
        if start != -1:
            start += len("auth-token=")
            end = set_cookie_string.find(";", start)
            auth_token = set_cookie_string[start:end] if end != -1 else set_cookie_string[start:]
        else:
            auth_token = None
        data = response.json()
        return data,auth_token

    def referral(self):
        url = f"https://api.intract.io/api/qv1/campaign/referral-session"
        data={
            "referralCode": "raF4SD",
            "referralLink": "https://www.intract.io/referral",
            "referralSource": "REFERRAL_PAGE"
        }
        response = session.post(
            url, headers=self.headers,json=data, timeout=60)
        data = response.json()
        return data

    def run(self,userName, account):
        self.userName = userName
        self.account = account
        try:
            nonce = self.get_nonce()['data']['nonce']
            hex = self._sign_message(nonce)
            data,auth_token = self.wallet(hex)
            self.headers['authorization'] = 'Bearer ' + auth_token
            log_and_print(f"{userName} login successfully ")
        except Exception as e:
            log_and_print(f"{userName} login failed: {e}")
            return False

        try:
            referral = self.referral()
            #这不校验结果
        except Exception as e:
            pass

        try:
            gm = self.gm()
            if "already done for today" in gm.get('message', ""):
                log_and_print(f"{userName} gm already done successfully")
                return True
            streakCount=gm['streakCount']
            log_and_print(f"{userName} gm successfully")
            '''
            {'streakCount': 1, 'longestStreakCount': 1, 'streakTimestamp': '2024-01-18T12:41:34.623Z',
             'streakDate': '2024-01-18', 'isFirstTimeMarked': True, 'expiredStreakCount': 0}'''

            ''' 这个是第一次登录
            {'streakCount': 0, 'expiredStreakCount': 0, 'longestStreakCount': 0, 'isFirstTimeMarked': True}'''
            return True
        except Exception as e:
            log_and_print(f"{userName} gm failed: {e}")
            return False

            


if __name__ == '__main__':
    proxy_list = ['http://127.0.0.1:7890']
    proxies = {'http': random.choice(proxy_list),
               'https': random.choice(proxy_list)}
    session = requests.Session()
    session.proxies = proxies
    app = IntractSign()

    failed_list = []
    credentials_list = find_user_credentials("eth", "IntractSign")
    for credentials in credentials_list:
        username = credentials["username"]
        access_token = credentials["access_token"]

        account = web3.Account.from_key(access_token)    
        if(app.run(username, account) == False):
            failed_list.append((username, account))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for username, failed_list in failed_list:
        log_and_print(f"final failed username = {username}")
