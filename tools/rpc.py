import requests
from requests.exceptions import SSLError
import math
import time
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }

def mylog(message):
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

    def get_gaslimit(self, transaction):
        """估算交易所需的gas量，带重试逻辑"""
        data = {
            "jsonrpc": "2.0",
            "method": "eth_estimateGas",
            "params": [transaction],
            "id": 1
        }
        max_retries = 5  # 设置最大重试次数
        for attempt in range(max_retries):
            try:
                response = requests.post(self.rpc, json=data, headers=headers, proxies=self.proxies)
                res_data = response.json()
                if res_data and 'error' not in res_data:
                    return int(res_data['result'], 16)  # 正常情况下返回结果
                elif res_data and 'error' in res_data:
                    raise Exception(f"Error: {res_data['error']}")  # 抛出异常以处理错误
            except Exception as e:
                self.logger(f"Attempt {attempt + 1} failed - estimate_gas Error: {e}")
                time.sleep(2)  # 发生异常时暂停2秒
    
        # 所有尝试失败后记录错误并返回None
        self.logger("Failed to estimate gas after several attempts.")
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
                dataInfo =  response.json()
                if dataInfo and 'error' in dataInfo:
                    raise Exception(f"Error: {dataInfo}")
                return dataInfo
            except Exception as e:
                self.logger(f"Attempt {attempt+1} failed - get_gas_price Error: {e}")
                time.sleep(2)

        # 所有重试尝试后还是失败，则返回None
        print("Failed to get gas price after several attempts.")
        return None

    def get_transaction_nonce(self, address):
        data = {"jsonrpc":"2.0","method":"eth_getTransactionCount","params":[address,'latest'],"id":1}
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.post(self.rpc, json=data, headers=headers, proxies=self.proxies)
                data = response.json()
                if data and 'error' in data:
                    raise Exception(f"Error: {response}")
                return data

            except Exception as e:
                self.logger(f"Attempt {attempt + 1} failed - get_transaction_nonce Error: {e}")
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
        max_retries = 5  # 设置最大重试次数
        for attempt in range(max_retries):
            try:
                response = requests.post(self.rpc, json=data, headers=headers, proxies=self.proxies)
                result = response.json()
                if result and 'error' in result:
                    raise Exception(f"Error from server: {result['error']}")

                # 直接返回 JSON 响应
                return result

            except Exception as e:
                self.logger(f"Attempt {attempt + 1} failed - get_balance Error: {e}")
                time.sleep(2)  # 发生异常时等待2秒再重试

        # 如果所有重试尝试后还是失败，则记录错误并返回None
        self.logger("Failed to get balance after several attempts.")
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
        """执行转账交易
        参数：
        account: 发送方账户
        to: 收款地址
        amount: 发送金额
        gasprice: gas价格，如果没有提供，则通过get_gas_price获取
        **kw: 其他交易参数
        """
        # 转换输入参数的格式
        amount = int(amount, 16) if isinstance(amount, str) else int(amount)
        if gasprice is not None:
            gasprice = int(gasprice, 16) if isinstance(gasprice, str) else int(gasprice)
        else:
            gasprice_result = self.get_gas_price()
            if gasprice_result is None or 'error' in gasprice_result:
                self.logger("Failed to fetch gas price.")
                return None
            gasprice = int(gasprice_result['result'], 16)
    
        last_response = None  # 初始化最后一次响应变量
    
        # 尝试发送交易，最多重试max_retries次
        for attempt in range(max_retries):
            nonce = self.get_transaction_nonce(account.address)
            if nonce is None:
                self.logger("Failed to fetch nonce.")
                return None
            transaction = {
                'from': account.address,
                'to': to,
                'value': hex(amount),
                'gasPrice': hex(gasprice),
                'nonce': hex(nonce),
                'chainId': self.chainid,  # 确保包含chainId
                'data': kw.get('data', '0x')
            }
            gaslimit = self.get_gaslimit(transaction)  # 自动获取gaslimit
            if gaslimit is None:
                self.logger("Failed to estimate gas limit.")
                continue
    
            transaction['gas'] = hex(gaslimit)
            transaction.update(kw)
    
            signed = account.signTransaction(transaction)
            response = self.send_raw_transaction(signed.rawTransaction.hex())
    
            if response and 'error' not in response:
                return response  # 交易成功发送
            elif response and 'error' in response:
                error_message = response['error'].get('message', '')
                if 'nonce too low' in error_message:
                    self.logger(f"Attempt {attempt+1} failed, nonce too low. Retrying...")
                    continue  # 如果因为nonce过低而失败，则重试
                elif 'transaction underpriced' in error_message:
                    self.logger(f"Attempt {attempt+1} failed, transaction underpriced. Increasing gas price by 10% and retrying...")
                    gasprice = int(gasprice * 1.1)  # 增加10%的gas价格
                    continue  # 如果因为交易价格过低而失败，则增加gas价格并重试
                last_response = response  # 保存错误响应
            else:
                last_response = response  # 保存错误响应
                break  # 如果响应为空或有其他未处理的错误，则终止尝试
    
        # 所有尝试后仍未成功发送交易，返回最后一次失败的response
        self.logger("Failed to send transaction after retries.")
        return last_response



