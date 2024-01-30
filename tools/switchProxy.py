import requests

class ClashAPIManager:
    def __init__(self, logger,api_url = "http://127.0.0.1:62401", secret = "eee36ac0-20af-4fe9-bfb0-fb62ac4ffadc"):
        self.api_url = api_url
        self.headers = {"Authorization": f"Bearer {secret}"}
        self.logger = logger  # logger 参数是传递给类的 log_and_print 函数

#🇭🇰 HK | 香港 05
#🇸🇬 SG | 新加坡 02
    def change_proxy(self, proxy_name):
        """切换代理节点"""
        data = {"name": proxy_name}
        try:
            response = requests.put(f"{self.api_url}/proxies/GLOBAL", json=data, headers=self.headers)
            if response.status_code == 204:
                self.logger(f"Proxy successfully changed to {proxy_name}")
                return  True
            else:
                raise Exception(f" (Status code: {response.status_code})")
        except Exception as e:
            self.logger(f"Error: Unable to change proxyto {proxy_name} {e}")
            return False
