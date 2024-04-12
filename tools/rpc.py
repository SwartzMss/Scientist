import requests
from requests.exceptions import SSLError
import math
import time
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }

def mylog(text):
    print(message)

class Rpc:
    """
    eth rpc方法
    """
    def __init__(self, rpc='https://rpc.ankr.com/eth_goerli', chainid=5, proxies=None,logger = mylog):
        self.rpc = rpc
        self.chainid = chainid
        self.proxies = proxies
        self.logger = logger

    def get_transaction_nonce(self, address):
        """获取交易数"""
        data = {"jsonrpc":"2.0","method":"eth_getTransactionCount","params":[address,'pending'],"id":1}
        try:
            res = requests.post(self.rpc, json=data, headers=headers,  proxies=self.proxies)
            return res.json()
        except Exception as e:
            self.logger(f"get_transaction_nonce  Error: {e}")
            time.sleep(2)
            # 处理错误，例如重试或返回默认值
            return None

    def get_current_block(self):
        """获取最新区块"""
        data = {"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}
        try:
            res = requests.post(self.rpc, json=data, headers=headers,  proxies=self.proxies)
            return res.json()
        except Exception as e:
            self.logger(f"get_current_block  Error: {e}")
            time.sleep(2)
            # 处理错误，例如重试或返回默认值
            return None

    def get_block_detail(self, number):
        """获取区块hash"""
        if isinstance(number, int):
            number = hex(number)
        data = {"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[number,True],"id":1}
        try:
            res = requests.post(self.rpc, json=data, headers=headers,  proxies=self.proxies)
            return res.json()
        except Exception as e:
            self.logger(f"get_block_detail  Error: {e}")
            time.sleep(2)
            # 处理错误，例如重试或返回默认值
            return None

    def call(self, to, data):
        data = {"jsonrpc":"2.0","method":"eth_call","params":[{"to": to, "data": data}, "latest"],"id":1}
        try:
            res = requests.post(self.rpc, json=data, headers=headers,  proxies=self.proxies)
            return res.json()
        except Exception as e:
            self.logger(f"call  Error: {e}")
            time.sleep(2)
            # 处理错误，例如重试或返回默认值
            return None

    def get_transaction(self, txhash):
        """获取的交易详情"""
        data = {"jsonrpc":"2.0","method":"eth_getTransactionByHash","params":[txhash],"id":1}
        try:
            res = requests.post(self.rpc, json=data, headers=headers,  proxies=self.proxies)
            return res.json()
        except Exception as e:
            self.logger(f"get_transaction  Error: {e}")
            time.sleep(2)
            # 处理错误，例如重试或返回默认值
            return None

    def get_gas_price(self):
        """获取gas"""
        data = {"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.post(self.rpc, json=data, headers=headers, proxies=self.proxies)
                return response.json()
            except Exception as e:
                self.logger(f"Attempt {attempt+1} failed - get_gas_price Error: {e}")
                time.sleep(2)

        # 所有重试尝试后还是失败，则返回None
        print("Failed to get gas price after several attempts.")
        return None

    def get_transaction_count_by_address(self, address):
        data = {"jsonrpc":"2.0","method":"eth_getTransactionCount","params":[address,'latest'],"id":1}
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.post(self.rpc, json=data, headers=headers, proxies=self.proxies)
                return response.json()
            except Exception as e:
                self.logger(f"Attempt {attempt + 1} failed - get_transaction_count_by_address Error: {e}")
                time.sleep(2)

        # 所有重试尝试后还是失败，则记录并返回None
        self.logger("Failed to get transaction count after several attempts.")
        return None

    def send_raw_transaction(self, hex):
        """广播交易"""
        data = {"jsonrpc":"2.0","method":"eth_sendRawTransaction","params":[hex],"id":1}
        try:
            res = requests.post(self.rpc, json=data, headers=headers,  proxies=self.proxies)
            return res.json()
        except Exception as e:
            self.logger(f"send_raw_transaction  Error: {e}")
            time.sleep(2)
            # 处理错误，例如重试或返回默认值
            return None

    def get_balance(self, address):
        """获取余额"""
        data = {"jsonrpc": "2.0", "method": "eth_getBalance", "params": [address, 'latest'], "id": 1}
        try:
            res = requests.post(self.rpc, json=data, headers=headers, proxies=self.proxies)
            return res.json()  # (int(res.json()['result'], 16)) / math.pow(10, 18)
        except Exception as e:
            self.logger(f"get_balance Exception Error: {e}")
            time.sleep(2)
            # 处理错误，例如重试或返回默认值
            return None

    def get_code(self, address, block="latest"):
        block = hex(block) if isinstance(block, int) else block
        data = {"jsonrpc":"2.0","method":"eth_getCode","params":[address, block],"id":1}
        try:
            res = requests.post(self.rpc, json=data, headers=headers,  proxies=self.proxies)
            return res.json()
        except Exception as e:
            self.logger(f"get_code  Error: {e}")
            time.sleep(2)
            # 处理错误，例如重试或返回默认值
            return None

    def transfer(self, account, to, amount, gaslimit, gasprice=None, max_retries=3, **kw):
        """离线交易
        参数：
        account: 发送方账户
        to: 收款地址
        amount: 发送金额
        gaslimit: 交易的gas限制
        gasprice: gas价格，如果没有提供，则通过get_gas_price获取
        **kw: 其他交易参数
        """
        # 转换输入参数的格式
        amount = int(amount, 16) if isinstance(amount, str) else int(amount)
        gaslimit = int(gaslimit, 16) if not isinstance(gaslimit, int) else gaslimit
        gasprice = int(gasprice, 16) if isinstance(gasprice, str) else int(gasprice) if gasprice is not None else int(self.get_gas_price()['result'], 16)

        last_response = None  # 初始化最后一次响应变量

        # 尝试发送交易，最多重试max_retries次
        for attempt in range(max_retries):
            nonce = int(self.get_transaction_count_by_address(account.address)['result'], 16)
            tx = {'from': account.address, 'value': amount, 'to': to, 'gas': gaslimit, 'gasPrice': gasprice, 'nonce': nonce, 'chainId': self.chainid}
            if kw:
                tx.update(kw)

            signed = account.signTransaction(tx)
            response = self.send_raw_transaction(signed.rawTransaction.hex())

            if response and 'error' not in response:
                return response  # 交易成功发送
            elif response and 'error' in response:
                error_message = response['error'].get('message', '')
                if 'nonce too low' in error_message:
                    self.logger(f"Attempt {attempt+1} failed, nonce too low. Retrying...")
                    last_response = response  # 更新最后一次响应
                    time.sleep(2)
                    continue  # 如果因为nonce过低而失败，则重试
                elif 'transaction underpriced' in error_message:
                    self.logger(f"Attempt {attempt+1} failed, transaction underpriced. Increasing gas price by 10% and retrying...")
                    gasprice = int(gasprice * 1.1)  # 增加10%的gas价格
                    last_response = response  # 更新最后一次响应
                    time.sleep(2)
                    continue  # 如果因为交易价格过低而失败，则增加gas价格并重试
                else:
                    last_response = response  # 更新最后一次响应
                    break  # 如果因为其他原因失败，则不再重试
            else:
                last_response = response  # 更新最后一次响应
                break

        # 所有尝试后仍未成功发送交易，返回最后一次失败的response
        self.logger("Failed to send transaction after retries.")
        return last_response


