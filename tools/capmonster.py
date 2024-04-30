import requests
import time
import datetime
from requests.exceptions import SSLError
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log(text):
    message = log_message(text)
    print(message)

class capmonster:
    def __init__(self,  client_key, logger = log):
        self.client_key = client_key
        self.logger = logger

    def create_task(self, challengeScript, captchaScript, websiteKey,context,iv):
        url = f'https://api.capmonster.cloud/createTask'
        params = {
            "clientKey": self.client_key,
            "task": {
                "type": "AmazonTaskProxyless",
                "websiteURL": 'https://t9uupiatq0.execute-api.us-east-1.amazonaws.com',
                "challengeScript": challengeScript,
                "captchaScript": captchaScript,
                "websiteKey": websiteKey,
                "context": context,
                "iv": iv,
                "cookieSolution": True
            }
        }
        response = requests.post(url, json=params)
        if response.status_code != 200:
            raise Exception(f"create_task failed {response.status_code} {response.text}")
        result = response.json()
        self.logger(f'create_task result: {result}')
        return result

    def get_task_result(self, task_id):
        url = f'https://api.capmonster.cloud/getTaskResult'
        params = {
            "clientKey": self.client_key,
            "taskId": task_id
        }
        while True:
            try:
                response = requests.post(url, json=params)
                result = response.json()
                self.logger(f'get_task_result response: {result}')
                if result['status'] == 'ready' or result['errorId'] != 0 :
                    return result
                elif result['status'] == 'processing':
                    time.sleep(6)  # 等待6秒再次查询
                else:
                    raise Exception("Unexpected task status")
            except SSLError as e:
                print(f"SSL Error: {e}")
                time.sleep(6)


    def get_recaptcha_token(self, challengeScript, captchaScript, websiteKey,context,iv):
        task_response = self.create_task(challengeScript, captchaScript, websiteKey,context,iv)
        if 'taskId' in task_response:
            task_id = task_response['taskId']
            result = self.get_task_result(task_id)
            if result and 'solution' in result and 'cookies' in result['solution']:
                return result['solution']['cookies']['aws-waf-token']
            else:
                raise Exception(f"人机验证失败")
        else:
            raise Exception("Failed to create captcha task")

# 示例用法
if __name__ == "__main__":
    pass