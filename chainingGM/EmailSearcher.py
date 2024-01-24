import email
import imaplib
import traceback
from bs4 import BeautifulSoup
import re
import pytz
import time
from email.utils import parsedate_to_datetime
import datetime

class EmailSearcher:
    def __init__(self, subject, code_length,logger):
        self.subject = subject
        self.code_length = code_length
        self.logger = logger  # logger 参数是传递给类的 log_and_print 函数

    def search_email_by_subject(self, username, password, max_attempts=6, wait_time = 10):
        # 邮箱设置
        imap_server = 'imap-mail.outlook.com'
        imap_port = 993
        # 建立与邮箱的连接
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        try:
            time.sleep(5)
            mail.login(username, password)
        except imaplib.IMAP4.error as e:
            mail.logout()  # 注销会话，而不是关闭邮箱，因为没有成功登录
            raise Exception(f"Error is {e}")
        
        mail.select("inbox")  # 选择收件箱


        for attempt in range(max_attempts):
            time.sleep(wait_time)
            #self.logger(f"Attempt {attempt+1}/{max_attempts}")
            # 搜索特定主题的邮件
            status, messages = mail.search(None, f'SUBJECT "{self.subject}"')
            if status != "OK":
                self.logger("No messages found!")
                continue
            message_ids = messages[0].split()
            # 获取最新的一封邮件的详细信息
            latest_email_id = message_ids[-1]  # 最新的邮件ID
            _, data = mail.fetch(latest_email_id, '(RFC822)')
            _, bytes_data = data[0]
            # 将邮件内容解析为消息对象
            msg = email.message_from_bytes(bytes_data)

            # 获取邮件发送时间
            email_date = msg.get("Date")

            if email_date:
                email_datetime = parsedate_to_datetime(email_date)
                current_datetime = datetime.datetime.now(pytz.utc)

                time_diff = current_datetime - email_datetime
                if time_diff > datetime.timedelta(minutes=1):
                    self.logger("Email is too old.")
                    continue

            # 从邮件正文提取验证码
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if "text/html" in content_type:
                        html_content = part.get_payload(decode=True).decode()
                        soup = BeautifulSoup(html_content, "html.parser")
                        text = soup.get_text()
                        #self.logger(f"text = {text}")
                        # 使用正则表达式查找六位数字的验证码
                        codes = re.findall(f"\\b\\d{{{self.code_length}}}\\b", text)
                        if codes:
                            #self.logger(f"codes:{codes[0]}")
                            mail.close()
                            mail.logout()
                            return codes[0]  # 返回找到的第一个验证码

        # 关闭邮箱连接
        mail.close()
        mail.logout()
        self.logger("Reached maximum attempts, no new email found.")
        return None  # 如果没有找到验证码，返回 None
