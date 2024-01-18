
#https://www.intract.io

from eth_account.messages import encode_defunct
import time
import math
import web3
import requests
import random
import os
from dotenv import load_dotenv
load_dotenv()

class Dapp:
    def __init__(self, account):
        self.account = account
        self.headers = {}

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
        print('wallet:' + str(self.account.address))
        msg = f"Please sign this message to verify your identity. Nonce: {nonce}"
        res = self.account.sign_message(encode_defunct(text=msg))
        return res.signature.hex()


    def gm(self):
        url = f"https://api.intract.io/api/qv1/auth/gm-streak"
        response = session.post(url, headers=self.headers, timeout=60)
        data = response.json()
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

    def run(self):
        try:
            nonce = self.get_nonce()['data']['nonce']
            hex = self._sign_message(nonce)
            data,auth_token = self.wallet(hex)
            self.headers['authorization'] = 'Bearer ' + auth_token
            print(f"login successfully id = {hex} ,set_cookies = {auth_token}")
        except Exception as e:
            print(f"login: {e}")
            return


        try:
            gm = self.gm()
            streakCount=gm['streakCount']
            longestStreakCount=gm['longestStreakCount']
            streakTimestamp=gm['streakTimestamp']
            print(f"gm:{streakCount} {longestStreakCount} {streakTimestamp}")
        except Exception as e:
            print(f"gm: {e}")
            return

            


if __name__ == '__main__':
    proxy_list = ['http://127.0.0.1:7890']
    proxies = {'http': random.choice(proxy_list),
               'https': random.choice(proxy_list)}
    session = requests.Session()
    session.proxies = proxies
    privkey='0x00'#可以直接把私钥放这里
    account = web3.Account.from_key(privkey)
    address = account.address
    
    life = Dapp(account)
    app = life.run()
