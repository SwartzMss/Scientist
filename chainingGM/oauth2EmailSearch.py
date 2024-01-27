import requests
import re
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta
import pytz
import sys
import time


# 替换为你的实际数据
subject = 'Chaining View'
code_length = 6  # 假设验证码长度为6
#access_token = 'EwB4A8l6BAAUs5+HQn0N+h2FxWzLS31ZgQVuHsYAAXarl8LRvcXKh6B569hy8wAeVsSWcr2J49SZqpAfUZeCiCwI+Noav3ZbsoE82zeU/UGfH08DDTB+FF3HD3sv6yHzCxmdaaTDlFnpfas2s0xhDtYlaa0EjbyxHfHNL1C2wPdj4KKO4Gk7L1vXoSuzrp1IP0nC+ytLDUzXEdRJA1Rcytx4CY33CduzheO3J9uGUWrbNJw9npuUfgxow+/hy74eHfigdQPfE1Bahk/ODCNjFbU9pHhEwN87Keb9NifjHIQjebKU2lLpQTS9xxf4AvNeezG5DzQ+jPbPNl+FkHGiAU3VDdsH7zhFYbsQhQB0VMDxmCNeyrdkRJgz86w0T7IDZgAACPUwE2csy2ymSAKQgczbmzDz9MVwhJdTmFs1n7ytwsVJh/kSreYlbAKKtWTFR+mJz+nOfDNfW6L6gxY6lrpl2Crt+gC6NsZy/J21xReA2iMrW+nu/TwU5/eMabm9ealfX1zCCya9euUst3ZNJewJk1oB1OOkw9819Go2/ifYT58SIqZJpx9zh6WSyZMcjDg2yJYj/RczPgbWQ1lqvVkGgmBZYoASr1ejQ3Y3y06exykq2FXJU+jY6HM3fxU8P4MsqpqQiZHztAMGtZQba8liV4x5rpoREZFZtcKnjda3j0zDjsu5/wlkXXWLQ1rYJ5iL7+pk8ricRwurrtE8fdmLvV/2mz7HYV7Bty4h9DkpK2Ud2DUmPREokoiL4PMp9aiSPaSJKfNCiGtufkOF44rZ//38ne7+CYc6DcccQihsHvJworsmT8ft6SbvTs42GoeX/ITPx+eW7QfXU0a8JqKGuDfWhnsP1dqIvSDK/zrYzSQJ0oGOtDbf/UDT+JUtmoYfQEGDk5Bqwl2qv7zuykaCkNvXeL2f0m8S2FscyU9PLHtzd4IlW55Qxho/2IarHor9TQAZvfqdV6LLsbEz8W5y8zKVxdCyL96FtPl8vqx5BZpgorPBSCPTVwr8/vabKWcPHnDz49ld2IO2XlefEeKFvJY43y24QfdDX70ahgK/PsXE4dtV38uleGJtvGOJlIJ817++aFLRu1JAtOrNEFLDMsJ571VJpzJn8lYxsS2Aq0tqXvrOBpRcNtnEc1KXtXqZdr+ts8OvUtvfVvJ3ya4OvHlNUIMC'
tenant_id =  'e46fcf06-daa1-4fb2-99c6-4e7056199334'
#refresh_token = '0.AScCBs9v5KHask-Zxk5wVhmTNH3Cij1XIM1Kj95NIErCIDYzAL0.AgABAAEAAAAmoFfGtYxvRrNriQdPKIZ-AgDs_wUA9P9X66784P9kLGBll5_1RVwv6HUAZkfN6PSxd_KNznWaQo9wqakIlfHM24AW4JuoE-a45yfv2YhwfrrRFyVkoz4lQbZkwXbOmSM3bdgL0xW_M35SJ2IEtEoKMq4wZLOgh9N70IbfghYsSBie9_3qouYHIllOgjI71hneDvZbq81R3r6ytfxq-ajKVbPjI5GA1_b5U4FUn65QRCR1mH9VLGmMbVf5_dSU3OVfJaMhghSwy7O8y-1LpqV-xGlOP9JyAjrZoR1duJ_FCdBZTtuShRFm6m0AFa3fG7qiD6IzgX5p7N-5jvnFXrOjeFq0N1tlTM9NSH_-7q6K7ManVY3Yf3kd2qdFTSqCy5zfuZFY4I9wd9s715I75zy_dUg9I3BbNFFs33ijqlhEr4YgdlcaudFpVme12tdrG3qzg_BvU73k1JTz57_LTuQ5isHKyprFQ5jjI0mZD7W79K_EozZg1n54HG7W8pXqw6XlQruP0AxqPbsmfZzoT9iz6ECWYUNcNhjGOWs_OmqUlMPbSETi-h9C9UCHqG6cPz3MmT3m7hkDV9zat-3r2TclgIWoQstvF3pXZx9wgmyHCrHK8mYS3Rds3psYESySx4S-lTcsWOpPaYU9Efka3d-U7f63g-IlWvjBZl68k15drvvuUlc6WDW26-0YF45qijv4uduNp1TqbdUUSdQFkUkV4dK1Vnjj0ntWsQI9zj_bDhr8V8FbxZdJi1mbWn8yX07w3qZtWODqfGgxigBbzUBtYeNrUNeLkirxZES7IXwU1wyF4da-Ipmh0giLIUsgHYN_s_oqQplzzRsber-D0_FJoAcuY0a1caat2hr054HFKqdEdwAcNIleMAzyAxqFjJJGYWKz6UZdRnf1m9uRWnesfsypjWfvCFHmpIzrqxykLRo7JIab7qM4yyLkUfZLOjsLdDfZT8ssEtbeotO3T1XD7HHi32c_BcPQasZoI5l9nuz4j8_Zu_t2lVnhRp9q3TZb3WDkwr6qHKam25yABo-p_3gns1jiakem8ckwF-F-v0Xt2AFzDVr-s7W4CPq0v_84jya2sn5gzpLA-BEo9pgM_NIkhQHH3XuLFwNXoWv8JE6tfxuU4azqLEbcBf9exmsl4baTVjqbLHdOSsx8AMuX_WCUPIfn3Os5_d37UynroVprKHLRyKU7d6M50lLSIvFxYAWpkMu7rd7lbYKZmqiiRYbHVQGzg_nQUMyL6q_tODOP3TujToO8prcf6VAzIrGAbcrUF5zKRru8y79Hx01-vh_3_07RCoqAGpU3JTN06JA20RIGf3BUf499MsvgdHir4dXg30U81notkbmlpokrWC0Zfn8eT0qrXA5izQWi_ye9yEy9xzIqOHtQqAc7gRNc-Zc-6X8YkJJY4gBEjxGFw6lmDBHS39Yfz5Vo7F1k_hP7A3uZu2cHZG_4scGXKimx-ha0SW9FQDIc'
client_id = '3d8ac27d-2057-4acd-8fde-4d204ac22036'
client_secret = 'fi.8Q~~lgC43g4l5ECZqr8Bxe~qD4Fmd3phtDaU3'
redirect_uri = 'https://login.microsoftonline.com/common/oauth2/nativeclient'

class oauth2EmailSearch:
    def __init__(self, subject, code_length, logger, access_token, refresh_token):
        self.subject = subject
        self.code_length = code_length
        self.logger = logger
        self.access_token = access_token
        self.refresh_token = refresh_token

    def refreshToken(self):
        token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        refresh_response = requests.post(token_url, data={
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': "https://login.microsoftonline.com/common/oauth2/nativeclient",
            'scope': 'Mail.ReadBasic Mail.Read Mail.ReadWrite offline_access'
        })
        #self.logger(f"refresh_response = {refresh_response}")
        new_access_token_data = refresh_response.json()
        access_token = new_access_token_data.get("access_token")
        #self.logger(f"access_token = {access_token}")
        self.access_token = access_token


    def search_email_by_subject(self, max_attempts=6, wait_time=10):
        url = 'https://graph.microsoft.com/v1.0/me/messages?$orderby=receivedDateTime DESC&$top=3'

        for attempt in range(max_attempts):
            time.sleep(wait_time)
            headers = {'Authorization': 'Bearer ' + self.access_token}
            #self.logger(f"Attempt {attempt+1}/{max_attempts}")
            response = requests.get(url, headers=headers)
            if response.status_code == 401:
                #self.logger("AuthenticationToken has expired")
                self.refreshToken()
                continue
            if response.status_code != 200:
                self.logger("Failed to fetch emails")
                continue
            emails = response.json().get('value')
            
            for email in emails:
                if self.subject in email.get('subject', '') and email.get('bodyPreview', ''):
                    email_date = email.get("receivedDateTime")
                    
                    if email_date:
                        # 使用 datetime.fromisoformat 来解析日期字符串
                        email_datetime = datetime.fromisoformat(email_date.rstrip('Z'))
                        email_datetime = email_datetime.replace(tzinfo=pytz.utc)
                        current_datetime = datetime.now(pytz.utc)

                        time_diff = current_datetime - email_datetime
                        if time_diff > timedelta(minutes=1):
                            self.logger("Email is too old.")
                            continue

                    # 此处假设邮件内容为HTML格式
                    html_content = email['body']['content']
                    soup = BeautifulSoup(html_content, "html.parser")
                    text = soup.get_text()
                    #self.logger(f"text =  {text}")
                    # 使用正则表达式查找六位数字的验证码
                    codes = re.findall(rf'(?<!\d)\d{{{self.code_length}}}(?!\d)', text)
                    if codes:
                        #self.logger(f"codes:{codes[0]}")
                        return codes[0]  # 返回找到的第一个验证码

        self.logger("Reached maximum attempts, no new email found.")
        return None  # 如果没有找到验证码，返回 None


