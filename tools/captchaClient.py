import requests
import time
import datetime
from requests.exceptions import SSLError
# https://github.com/2captcha/2captcha-python
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log(text):
    message = log_message(text)
    print(message)

class captchaClient:
    def __init__(self,  client_key, logger = log):
        self.client_key = client_key
        self.logger = logger

    def create_task(self, challengeScript, captchaScript, websiteKey,context,iv,proxyAddress,proxyPort,proxyLogin,proxyPassword):
        url = f'https://api.2captcha.com/createTask'
        params = {
            "clientKey": self.client_key,
            "task": {
                "type": "AmazonTask",
                "websiteURL": "https://app.alphaorbeta.com",
                "challengeScript": challengeScript,
                "captchaScript": captchaScript,
                "websiteKey": websiteKey,
                "context": context,
                "iv": iv,
                "proxyType": "socks5",
                "proxyAddress": proxyAddress,
                "proxyPort": proxyPort,
                "proxyLogin": proxyLogin,
                "proxyPassword": proxyPassword
            }
        }
        response = requests.post(url, json=params)
        result = response.json()
        self.logger(f'create_task result: {result}')
        return result

    def get_task_result(self, task_id):
        url = f'https://api.2captcha.com/getTaskResult'
        params = {
            "clientKey": self.client_key,
            "taskId": task_id
        }
        while True:
            try:
                response = requests.post(url, json=params)
                result = response.json()
                self.logger(f'get_task_result response: {result}')
                if result['status'] == 'ready' or  result['errorId'] != 0 :
                    return result
                elif result['status'] == 'processing':
                    time.sleep(6)  # 等待6秒再次查询
                else:
                    raise Exception("Unexpected task status")
            except SSLError as e:
                print(f"SSL Error: {e}")
                time.sleep(6)


    def get_recaptcha_token(self, challengeScript, captchaScript, websiteKey,context,iv,proxyAddress,proxyPort,proxyLogin,proxyPassword):
        task_response = self.create_task(challengeScript, captchaScript, websiteKey,context,iv,proxyAddress,proxyPort,proxyLogin,proxyPassword)
        if 'taskId' in task_response:
            task_id = task_response['taskId']
            result = self.get_task_result(task_id)
            if result and 'solution' in result and 'captcha_voucher' in result['solution']:
                return result['solution']['captcha_voucher'],result['solution']['existing_token']
            else:
                raise Exception(f"人机验证失败")
        else:
            raise Exception("Failed to create captcha task")

# 示例用法
if __name__ == "__main__":
    pass