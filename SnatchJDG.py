from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

class SnathJDG:
    def __init__(self, user_data_dir_path="./SnathJDG/cache/"):
        self.user_data_dir_path = user_data_dir_path
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        """初始化 WebDriver。"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument(f"--user-data-dir={self.user_data_dir_path}")
        return webdriver.Chrome(options=chrome_options)

    def login(self, url="https://passport.jd.com/new/login.aspx"):
        """登录指定的网址。"""
        self.driver.get(url)

    def logout(self):
        """退出并关闭浏览器。"""
        self.driver.quit()

if __name__ == "__main__":
    app = SnathJDG()
    app.login()
    time.sleep(20)
    app.logout()