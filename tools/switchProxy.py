import requests
import yaml
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


app = ClashAPIManager()
app.change_proxy('🇭🇰 HK | 香港 05')