import requests
import yaml
import random
import time
def myprint(text):
    print(text)

class socket5SwitchProxy:
    def __init__(self, logger = myprint):
        self.logger = logger  # logger 参数是传递给类的 log_and_print 函数

    def verify_ip_change(self,proxy_name):
        """验证IP地址是否成功切换"""
        try:
            response = requests.get("https://myip.ipip.net/", timeout=60, proxies=proxy_name)
            if response.status_code == 200:
                self.logger(f"Current IP Info: {response.text}")
                return True
            else:
                self.logger(f"Failed to verify IP change (Status code: {response.status_code})")
                return False
        except Exception as e:
            self.logger(f"Error: Unable to verify IP change {e}")
            return False

    def change_proxy_until_success(self, proxy_names):
        """遍历代理列表，尝试切换到每个代理，直到成功为止"""
        random.shuffle(proxy_names)
        for proxy_name in proxy_names:
            time.sleep(3)
            if self.verify_ip_change(proxy_name):
                self.logger(f"Successfully changed proxy and verified IP: {proxy_name}")
                return True, proxy_name
            else:
                self.logger(f"Proxy changed but IP verification failed: {proxy_name}")
        # 如果所有代理都尝试过且都失败了，返回False
        return False, proxy_name




if __name__ == '__main__':
    from UserInfo import UserInfo
    app = socket5SwitchProxy()
    usersinfo = UserInfo()
    proxyList = usersinfo.find_proxy_by_alias_in_file("JP03")
    app.change_proxy_until_success(proxyList)