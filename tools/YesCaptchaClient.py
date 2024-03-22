import requests
import time
import datetime
from requests.exceptions import SSLError
def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log(text):
    message = log_message(text)
    print(message)

class YesCaptchaClient:
    def __init__(self,  client_key, logger = log,):
        self.client_key = client_key
        self.base_url = 'https://api.yescaptcha.com'
        self.logger = logger

    def create_task(self, website_url, website_key, task_type):
        url = f'{self.base_url}/createTask'
        params = {
            "clientKey": self.client_key,
            "task": {
                "websiteURL": website_url,
                "websiteKey": website_key,
                "type": task_type
            }
        }
        response = requests.post(url, json=params)
        result = response.json()
        self.logger(f'create_task result: {result}')
        return result

    def get_task_result(self, task_id):
        url = f'{self.base_url}/getTaskResult'
        params = {
            "clientKey": self.client_key,
            "taskId": task_id
        }
        while True:
            try:
                response = requests.post(url, json=params)
                result = response.json()
                self.logger(f'get_task_result response: {result}')
                if result['status'] == 'ready':
                    return result
                elif result['status'] == 'processing':
                    time.sleep(6)  # 等待6秒再次查询
                else:
                    raise Exception("Unexpected task status")
            except SSLError as e:
                print(f"SSL Error: {e}")
                time.sleep(6)


    def get_recaptcha_token(self, website_url, website_key, task_type):
        task_response = self.create_task(website_url, website_key, task_type)
        if 'taskId' in task_response:
            task_id = task_response['taskId']
            result = self.get_task_result(task_id)
            if result and 'solution' in result and 'gRecaptchaResponse' in result['solution']:
                return result['solution']['gRecaptchaResponse']
            else:
                raise Exception(f"人机验证失败")
        else:
            raise Exception("Failed to create captcha task")

# 示例用法
if __name__ == "__main__":
    # berachain
    # website_url = 'https://artio.faucet.berachain.com'
    # website_key = '0x4AAAAAAARdAuciFArKhVwt'
    # task_type = 'TurnstileTaskProxyless'

    # captcha_client = YesCaptchaClient()
    # try:
    #     recaptcha_token = captcha_client.get_recaptcha_token(website_url, website_key, task_type)
    #     print(f"Recaptcha token: {recaptcha_token}")
    # except Exception as e:
    #     print(f"get_recaptcha_token Error: {e}")

    #genomefi
    website_url = 'https://event.genomefi.io/'
    website_key = '6LcK_aApAAAAAPAUR8Zo96ZMXGQF12jeUKR2KeGr'
    task_type = 'NoCaptchaTaskProxyless'

    captcha_client = YesCaptchaClient(client_key="df06ea524cda53aedea083e1c5ec334f656ed3d034874")
    try:
        recaptcha_token = captcha_client.get_recaptcha_token(website_url, website_key, task_type)
        print(f"Recaptcha token: {recaptcha_token}")
    except Exception as e:
        print(f"get_recaptcha_token Error: {e}")