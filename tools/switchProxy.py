import requests
import yaml
import random
def myprint(text):
    print(text)

#config.yaml 配置文件在里面


class ClashAPIManager:
    def __init__(self, logger = myprint, config_path="C:/Users/swart/.config/clash/config.yaml"):
        config = self.load_config(config_path)
        # 设置API URL和密钥
        self.api_url = f"http://{config['external-controller']}"
        self.secret = config['secret']
        self.headers = {"Authorization": f"Bearer {self.secret}"}
        self.logger = logger  # logger 参数是传递给类的 log_and_print 函数

    def load_config(self, config_path):
        """从YAML配置文件中加载配置"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config
        except Exception as e:
            self.logger(f"Error loading config file: {e}")
            return {}

#🇭🇰 HK | 香港 05
#🇸🇬 SG | 新加坡 02
    def change_proxy(self, proxy_name):
        """切换代理节点"""
        data = {"name": proxy_name}
        try:
            response = requests.put(f"{self.api_url}/proxies/GLOBAL", json=data, headers=self.headers)
            if response.status_code == 204:
                self.logger(f"Proxy successfully changed to {proxy_name}")
                return True
            else:
                raise Exception(f"Failed to change proxy (Status code: {response.status_code})")
        except Exception as e:
            self.logger(f"Error: Unable to change proxy to {proxy_name} {e}")
            return False

    def get_all_proxies(self):
        """获取并打印所有代理信息"""
        try:
            response = requests.get(f"{self.api_url}/proxies", headers=self.headers)
            if response.status_code == 200:
                proxies = response.json()["proxies"]
                for key, value in proxies.items():
                    self.logger(f"Proxy Name: {key}, Type: {value['type']}")
            else:
                self.logger(f"Failed to get proxies (Status code: {response.status_code})")
        except Exception as e:
            self.logger(f"Error: Unable to get proxies {e}")


    def verify_ip_change(self):
        """验证IP地址是否成功切换"""
        try:
            response = requests.get("https://myip.ipip.net/", timeout=60)
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
            if self.change_proxy(proxy_name):
                if self.verify_ip_change():
                    self.logger(f"Successfully changed proxy and verified IP: {proxy_name}")
                    return True
                else:
                    self.logger(f"Proxy changed but IP verification failed: {proxy_name}")
            else:
                self.logger(f"Failed to change to proxy: {proxy_name}")
        # 如果所有代理都尝试过且都失败了，返回False
        return False

app = ClashAPIManager()
app.get_all_proxies()
app.change_proxy('🇺🇸 US | 美国 06')
app.verify_ip_change()