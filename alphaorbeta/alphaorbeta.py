
from eth_account.messages import encode_defunct
import time
import math
import sys
import web3
import requests
import random
import datetime
from web3 import Web3
import json
from fake_useragent import UserAgent
import os
from dotenv import load_dotenv
load_dotenv()

# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# 现在可以从tools目录导入UserInfo
from tools.UserInfo import UserInfo
# 现在可以从tools目录导入Rpc
from tools.rpc import Rpc
from tools.socket5SwitchProxy import socket5SwitchProxy
# 现在可以从tools目录导入excelWorker
from tools.excelWorker import excelWorker

# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\alphaorbeta_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')


class alphaorbeta:
    def __init__(self,rpc_url='https://1rpc.io/opbnb', chain_id=204):
        self.rpc = Rpc(rpc=rpc_url, chainid=chain_id)
        self.alias = None
        self.account = None
        self.session = None
        self.gaslimit = 400000
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.userId = None
        self.headers = {
            'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 116)}.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'referer': 'https://app.alphaorbeta.com/',
            'origin': 'https://app.alphaorbeta.com', 
        }

    def create_new_session(self,proxyinfo):
        ua = UserAgent()
        self.headers['user-agent'] = ua.random
        self.headers.pop('Authorization', None)
        self.session = requests.Session()
        self.session.cookies.clear()
        self.session.proxies = proxyinfo

    def signature(self):
        message = "Please click “sign” to confirm your identity as the owner of this address."
        res = self.account.sign_message(encode_defunct(text=message))
        return res.signature.hex()


    def put_signInOrSignUpByWallet(self,signature):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/signInOrSignUpByWallet"
        message = "Please click “sign” to confirm your identity as the owner of this address."
        payload = {
                "address": self.account.address,
                "message":message,
                "signature":signature
        }
        response = self.session.put(
            url, headers=self.headers,json=payload, timeout=120)
        data = response.json()
        log_and_print(f"{self.alias}post_signInOrSignUpByWallet data:{data}")
        return data

    def get_daily(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userQuest/user/{self.userId}/daily"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_daily data:{data}")
        return data

    def post_checkin(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userQuest/checkin/user/{self.userId}/complete?version=v2"
        response = self.session.post(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} post_checkin data:{data}")
        return data

    def get_points(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/point/user/{self.userId}"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_points data:{data}")
        return data

    def get_profile(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0 or energy == 0:
            return None
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/user/{self.userId}/profile"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_profile data:{data}")
        return data

    def get_endingSoonTask(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/vote?category=ENDING_SOON&chainId=204"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_endingSoonTask data:{data}")
        return data

    def get_votedTaskInfo(self,taskId):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/vote/{taskId}"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_votedTaskInfo data:{data}")
        return data

    def get_claimauthorize(self,taskId):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userReward/claim/user/{self.userId}/vote/{taskId}/authorize"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_claimauthorize data:{data}")
        return data

    def post_claim(self,taskId):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userReward/claim/user/{self.userId}/vote/{taskId}"
        response = self.session.post(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} post_claim data:{data}")
        return data

    def get_bnbSilverCriteriaAirdrop(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userQuest/bnbSilverCriteriaAirdrop/user/{self.userId}/claim"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_bnbSilverCriteriaAirdrop data:{data}")
        return data


    def get_votedTask(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/vote/user/{self.userId}?chainId=204"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_votedTask data:{data}")
        return data

    def get_unclaimedVoteTask(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/vote/user/{self.userId}?chainId=204&category=UNCLAIMED"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_unclaimedVoteTask data:{data}")
        return data

    def post_authorize(self,voteId,userVoteAmount,mockGameId,votedOptionId):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userVote/mockGame/authorize"
        payload = {
                "voteId": voteId,
                "userId":self.userId,
                "userVoteAmount":userVoteAmount,
                "mockGameId":mockGameId,
                "votedOptionId":votedOptionId,
                "version":"V2"
        }
        response = self.session.post(url, headers=self.headers, json=payload,timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} post_authorize voteId {voteId} data:{data}")
        return data

    def post_userVote(self,voteId,userVoteAmount,mockGameId,votedOptionId,hash):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userVote/mockGame"
        payload = {
                "hash": hash,
                "mockGameId":mockGameId,
                "userId":self.userId,
                "userVoteAmount":userVoteAmount,
                "voteId":voteId,
                "votedOptionId":votedOptionId,
                "version":"V2"
        }
        response = self.session.post(url, headers=self.headers, json=payload,timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} post_userVote data:{data}")
        return data

    def get_nftQuestauthorize(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userQuest/nftQuest/user/{self.userId}/silver/authorize"
        response = self.session.get(url, headers=self.headers, timeout=20)
        log_and_print(f"{self.alias} get_nftQuestauthorize data:{response}")
        return response


    def get_silverSbtCriteria(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userQuest/silverSbtCriteria/user/{self.userId}"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_silverSbtCriteria data:{data}")
        return data


    def get_userReward(self):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/userReward/summary/user/{self.userId}"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_userReward voteIddata:{data}")
        return data

    def get_detailVoteInfo(self,voteId):
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/vote/{voteId}/user/{self.userId}"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_detailVoteInfo voteId {voteId} data:{data}")
        return data

    def get_hasPoppedMembershipCard(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0 or energy == 0:
            return None
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/user/{self.userId}/hasPoppedMembershipCard"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_hasPoppedMembershipCard data:{data}")
        return data


    def get_lastWeekAbChipsSpendSILVER(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0 or energy == 0:
            return None
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/lastWeekAbChipsSpend/SILVER"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_lastWeekAbChipsSpendSILVER data:{data}")
        return data

    def get_lastWeekAbChipsSpendSILVERWOOD(self):
        run_or_not = random.randint(0, 1)  # 生成 0 或 1
        if run_or_not == 0 or energy == 0:
            return None
        url = f"https://t9uupiatq0.execute-api.us-east-1.amazonaws.com/prod/voting/lastWeekAbChipsSpend/WOOD"
        response = self.session.get(url, headers=self.headers, timeout=20)
        data = response.json()
        log_and_print(f"{self.alias} get_lastWeekAbChipsSpendSILVERWOOD data:{data}")
        return data

    def check_transaction_status(self, tx_hash, timeout=300, interval=5):
        """检查交易的状态，返回是否确认和交易状态。使用计数器实现超时。"""
        max_attempts = timeout // interval  # 计算最大尝试次数
        attempts = 0  # 初始化尝试次数计数器

        while attempts < max_attempts:  # 循环直到达到最大尝试次数
            time.sleep(interval)  # 等待一段时间再次检查
            try:
                receipt = self.web3.eth.get_transaction_receipt(tx_hash)                
                if receipt is not None:
                    if receipt.status == 1:
                        return True, "success"  # 交易已确认且成功
                    else:
                        return False, "failure"  # 交易已确认但失败
            except Exception as e:
                log_and_print(f"Error checking transaction status: {e}")
            
            attempts += 1  # 更新尝试次数

        # 超时后返回False，表示交易状态未知或未确认，状态为挂起
        return False, "pending"


    def perform_mintStellar(self,signature):
        log_and_print(f"{alias} perform_mintStellar ")
        __contract_addr = Web3.to_checksum_address("0xf2b05c3faf117c5d8301e74253f1cb84271aaad7")
        MethodID="0xf9286095"
        param_1="0000000000000000000000000000000000000000000000000000000000000040"
        param_2="00000000000000000000000000000000000000000000000000000000000000c0"
        param_3="0000000000000000000000000000000000000000000000000000000000000041"
        param_4=signature[2:66]
        param_5=signature[66:130]
        param_6_raw = signature[130:]  # 提取从130位置开始的所有字符
        param_6 = param_6_raw.ljust(64, '0')
        param_7="0000000000000000000000000000000000000000000000000000000000000006"
        param_8="73696c7665720000000000000000000000000000000000000000000000000000"

        try:
            data = MethodID + param_1 + param_2 + param_3 + param_4 + param_5 + param_6 +  param_7 + param_8
            gasprice = int(self.rpc.get_gas_price()['result'], 16) * 1.5
            response = self.rpc.transfer(
                self.account, __contract_addr, 0, self.gaslimit, gasprice, data=data)
            if 'error' in response:
                raise Exception(f"action Error: {response}")
            hasResult = response["result"]
            txIsSucceed,msg = self.check_transaction_status(hasResult)
            if  txIsSucceed != True:
                raise Exception(f"check_transaction_status hasResult {hasResult} Error: {msg}")
            return True,hasResult
        except Exception as e:
            log_and_print(f"{alias} perform_mintStellar  failed: {e}")
            excel_manager.update_info(alias, f" perform_mintStellar failed: {e}")
            return False,None

    def perform_claim(self,amount,voteContractAddress,createdAt,nonce,signature):
        log_and_print(f"{alias} perform_claim ")
        __contract_addr = Web3.to_checksum_address("0x0fc1b3e19458d2fc8a8f56f06e2ddc105257e00f")
        MethodID="0x7581b832"
        param_1="00000000000000000000000000000000000000000000000000000000000000a0"
        param_2=f"{int(amount):064x}"
        param_3=f"{int(voteContractAddress, 16):064x}"
        param_4=f"{int(createdAt):064x}"
        param_5=f"{int(nonce):064x}"
        param_6="0000000000000000000000000000000000000000000000000000000000000041"
        param_7 = signature[2:66]  # 去掉开头的 '0x' 并取接下来的64个字符
        param_8= signature[66:130]  # 继续取接下来的64个字符
        param_9_raw = signature[130:]  # 提取从130位置开始的所有字符
        param_9 = param_9_raw.ljust(64, '0')
        try:
            data = MethodID + param_1 + param_2 + param_3 + param_4 + param_5 + param_6 +  param_7 + param_8 + param_9
            gasprice = int(self.rpc.get_gas_price()['result'], 16) * 1.5
            response = self.rpc.transfer(
                self.account, __contract_addr, 0, self.gaslimit, gasprice, data=data)
            if 'error' in response:
                raise Exception(f"action Error: {response}")
            hasResult = response["result"]
            txIsSucceed,msg = self.check_transaction_status(hasResult)
            if  txIsSucceed != True:
                raise Exception(f"check_transaction_status hasResult {hasResult} Error: {msg}")
            return True,hasResult
        except Exception as e:
            log_and_print(f"{alias} perform_claim  failed: {e}")
            excel_manager.update_info(alias, f" perform_claim failed: {e}")
            return False,None


    def perform_voteForAbCHIPS(self,userVoteAmount,votedOptionId,voteContractAddress,createdAt,nonce,signature):
        log_and_print(f"{alias} perform_voteForAbCHIPS ")
        __contract_addr = Web3.to_checksum_address("0x0fc1b3e19458d2fc8a8f56f06e2ddc105257e00f")
        MethodID="0xe3706194"
        param_1="00000000000000000000000000000000000000000000000000000000000000e0"
        param_2=f"{int(userVoteAmount):064x}"
        param_3="0000000000000000000000000000000000000000000000000000000000000001"
        param_4=f"{int(votedOptionId):064x}"
        param_5=f"{int(voteContractAddress, 16):064x}"
        param_6=f"{int(createdAt):064x}"
        param_7=f"{int(nonce):064x}"
        param_8="0000000000000000000000000000000000000000000000000000000000000041"
        param_9 = signature[2:66]  # 去掉开头的 '0x' 并取接下来的64个字符
        param_10 = signature[66:130]  # 继续取接下来的64个字符
        param_11_raw = signature[130:]  # 提取从130位置开始的所有字符
        param_11 = param_11_raw.ljust(64, '0')
        try:
            data = MethodID + param_1 + param_2 + param_3 + param_4 + param_5 + param_6 +  param_7 + param_8 + param_9 + param_10 + param_11
            gasprice = int(self.rpc.get_gas_price()['result'], 16) * 1.5
            response = self.rpc.transfer(
                self.account, __contract_addr, 0, self.gaslimit, gasprice, data=data)
            if 'error' in response:
                raise Exception(f"action Error: {response}")
            hasResult = response["result"]
            txIsSucceed,msg = self.check_transaction_status(hasResult)
            if  txIsSucceed != True:
                raise Exception(f"check_transaction_status hasResult {hasResult} Error: {msg}")
            return True,hasResult
        except Exception as e:
            log_and_print(f"{alias} perform_voteForAbCHIPS  failed: {e}")
            excel_manager.update_info(alias, f" perform_voteForAbCHIPS failed: {e}")
            return False,None

    def run(self,alias, account,proxyinfo):
        self.alias = alias
        self.account = account
        self.userId = None
        self.create_new_session(proxyinfo)

        try:
            signature = self.signature()
            response = self.put_signInOrSignUpByWallet(signature)
            if 'error' in response:
                raise Exception(f"Error: {response}")
            token = response["jwt"]
            self.userId = response["userId"]
            self.headers['authorization'] = 'Bearer ' + token
            log_and_print(f"{alias} post_signInOrSignUpByWallet successfully ")
        except Exception as e:
            log_and_print(f"{alias} post_signInOrSignUpByWallet failed: {e}")
            excel_manager.update_info(alias, f"post_signInOrSignUpByWallet failed: {e}")
            return False

        try:
            response = self.get_profile()
            response = self.get_hasPoppedMembershipCard()
            #这不校验结果
        except Exception as e:
            pass


        try:
            response = self.get_points()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            for balance in response:
                total_balance = int(balance['totalBalance'])
                decimal = balance['decimal']
                if balance['point'] == 'abETH':
                    abETH_value = total_balance / (10 ** decimal)
                elif balance['point'] == 'abCHIPS':
                    abCHIPS_value = total_balance / (10 ** decimal)
            log_and_print(f"{alias} get_points successfully  abETH_value {abETH_value} abCHIPS_value {abCHIPS_value}")
        except Exception as e:
            log_and_print(f"{alias} get_points failed: {e}")
            excel_manager.update_info(alias, f"get_points failed: {e}")
            return False


        try:
            response = self.get_profile()
            response = self.get_hasPoppedMembershipCard()
            response = self.get_silverSbtCriteria()
            #这不校验结果
        except Exception as e:
            pass

        try:
            response = self.get_userReward()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            alpha_token_value = 0
            beta_token_value = 0
            for balance in response['rewards']:
                total_balance = int(balance['total'])
                decimal = balance['decimal']
                if balance['reward'] == 'ALPHA_TOKEN':
                    alpha_token_value = total_balance / (10 ** decimal)
                elif balance['reward'] == 'BETA_TOKEN':
                    beta_token_value = total_balance / (10 ** decimal)
            excel_manager.update_info(alias, f" {alpha_token_value} ", "alpha_token_value")
            excel_manager.update_info(alias, f" {beta_token_value} ", "beta_token_value")
            log_and_print(f"{alias} get_userReward successfully  alpha_token_value {alpha_token_value} beta_token_value {beta_token_value}")
        except Exception as e:
            log_and_print(f"{alias} get_userReward failed: {e}")
            excel_manager.update_info(alias, f"get_userReward failed: {e}")
            return False


        try:
            response = self.get_daily()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            claimed_value = response['DAILY_CHECKIN']['claimed']
            log_and_print(f"{alias} get_daily successfully claimed_value {claimed_value}")
        except Exception as e:
            log_and_print(f"{alias} get_daily failed: {e}")
            excel_manager.update_info(alias, f"get_daily failed: {e}")
            return False

        if claimed_value == 0:
            try:
                response = self.post_checkin()
                if 'error' in response:
                    raise Exception(f"Error: {response}")
                log_and_print(f"{alias} post_checkin successfully ")
            except Exception as e:
                log_and_print(f"{alias} post_checkin failed: {e}")
                excel_manager.update_info(alias, f"post_checkin failed: {e}")
                return False
        try:
            response = self.get_profile()
            response = self.get_hasPoppedMembershipCard()
            #这不校验结果
        except Exception as e:
            pass

        try:
            response = self.get_endingSoonTask()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            endingSoonTask_ids = [item['voteId'] for item in response['data'] if 'version' in item and item['version'] == "V2"]
            log_and_print(f"{alias} get_endingSoonTask successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_endingSoonTask failed: {e}")
            excel_manager.update_info(alias, f"get_endingSoonTask failed: {e}")
            return False

        try:
            response = self.get_lastWeekAbChipsSpendSILVER()
            response = self.get_lastWeekAbChipsSpendSILVERWOOD()
            #这不校验结果
        except Exception as e:
            pass   

        try:
            response = self.get_votedTask()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            votedTask_ids = [item['voteId'] for item in response['data']]
            log_and_print(f"{alias} get_votedTask successfully ")
        except Exception as e:
            log_and_print(f"{alias} get_votedTask failed: {e}")
            excel_manager.update_info(alias, f"get_votedTask failed: {e}")
            return False

        remaining_ids = list(set(endingSoonTask_ids) - set(votedTask_ids))

        # 检查remaining_ids是否不为空，然后随机选择一个
        run_or_not = random.randint(1, 3)
        if run_or_not <= 2 and remaining_ids:
            # 随机决定要选择的任务数量，范围从1到remaining_ids的长度
            num_to_select = random.randint(1, len(remaining_ids))

            # 随机选择num_to_select个任务
            selected_ids = random.sample(remaining_ids, num_to_select)
            for voteId in selected_ids:
                try:
                    response = self.get_detailVoteInfo(voteId)
                    if 'error' in response:
                        raise Exception(f"Error: {response}")
                    option_states = response['voteGameState']['optionStates']
                    voteTitle = response['voteTitle']
                    max_voted_option = max(option_states, key=lambda x: x['totalVoted'])
                    max_voted_option_id = max_voted_option['optionId']
                    minVoteAmount = response['mockGame']["gameState"]["minVoteAmount"]
                    mockGameId = response['mockGame']["mockGameId"]
                    votedOptionId = max_voted_option_id
                    userVoteAmount = str(int(int(minVoteAmount) * 1.1))
                    voteContractAddress = response['voteContractAddress']
                    log_and_print(f"{alias} get_detailVoteInfo successfully max_voted_option_id {max_voted_option_id} voteTitle {voteTitle}")
                except Exception as e:
                    log_and_print(f"{alias} get_detailVoteInfo failed: {e}")
                    excel_manager.update_info(alias, f"get_detailVoteInfo failed: {e}")
                    return False

                try:
                    response = self.get_daily()
                    if 'error' in response:
                        raise Exception(f"Error: {response}")
                    claimed_value = response['DAILY_CHECKIN']['claimed']
                    log_and_print(f"{alias} get_daily successfully claimed_value {claimed_value}")
                except Exception as e:
                    log_and_print(f"{alias} get_daily failed: {e}")
                    excel_manager.update_info(alias, f"get_daily failed: {e}")
                    return False

                if abCHIPS_value > int(userVoteAmount) /(10 ** decimal):
                    try:
                        response = self.post_authorize(voteId,userVoteAmount,mockGameId,votedOptionId)
                        if 'error' in response:
                            raise Exception(f"Error: {response}")
                        nonce = response["nonce"]
                        createdAt = response["createdAt"]
                        signature = response["signature"]
                        log_and_print(f"{alias} post_authorize successfully")
                    except Exception as e:
                        log_and_print(f"{alias} post_authorize failed: {e}")
                        excel_manager.update_info(alias, f"post_authorize failed: {e}")
                        return False
                    
                    result,hash = self.perform_voteForAbCHIPS(userVoteAmount,votedOptionId,voteContractAddress,createdAt,nonce,signature)
                    if  result == False:
                        return False

                    try:
                        response = self.get_lastWeekAbChipsSpendSILVER()
                        response = self.get_lastWeekAbChipsSpendSILVERWOOD()
                        #这不校验结果
                    except Exception as e:
                        pass   

                    try:
                        response = self.post_userVote(voteId,userVoteAmount,mockGameId,votedOptionId,hash)
                        if 'error' in response:
                            raise Exception(f"Error: {response}")
                        log_and_print(f"{alias} post_userVote successfully")
                    except Exception as e:
                        log_and_print(f"{alias} post_userVote failed: {e}")
                        excel_manager.update_info(alias, f"post_userVote failed: {e}")
                        return False

                try:
                    response = self.get_daily()
                    if 'error' in response:
                        raise Exception(f"Error: {response}")
                    claimed_value = response['DAILY_CHECKIN']['claimed']
                    log_and_print(f"{alias} get_daily successfully claimed_value {claimed_value}")
                except Exception as e:
                    log_and_print(f"{alias} get_daily failed: {e}")
                    excel_manager.update_info(alias, f"get_daily failed: {e}")
                    return False

                # 这边直接restake 一次随机的
                run_or_not = random.randint(0, 1)  # 生成 0 或 1
                if run_or_not == 1:        
                    log_and_print(f"{alias} so lucky need restake here")
                    try:
                        response = self.get_points()
                        if 'error' in response:
                            raise Exception(f"Error: {response}")
                        for balance in response:
                            total_balance = int(balance['totalBalance'])
                            decimal = balance['decimal']
                            if balance['point'] == 'abETH':
                                abETH_value = total_balance / (10 ** decimal)
                            elif balance['point'] == 'abCHIPS':
                                abCHIPS_value = total_balance / (10 ** decimal)
                        log_and_print(f"{alias} get_points successfully  abETH_value {abETH_value} abCHIPS_value {abCHIPS_value}")
                    except Exception as e:
                        log_and_print(f"{alias} get_points failed: {e}")
                        excel_manager.update_info(alias, f"get_points failed: {e}")
                        return False

                    try:
                        response = self.get_detailVoteInfo(voteId)
                        if 'error' in response:
                            raise Exception(f"Error: {response}")
                        option_states = response['voteGameState']['optionStates']
                        voteTitle = response['voteTitle']
                        max_voted_option = max(option_states, key=lambda x: x['totalVoted'])
                        max_voted_option_id = max_voted_option['optionId']
                        minVoteAmount = response['mockGame']["gameState"]["minVoteAmount"]
                        mockGameId = response['mockGame']["mockGameId"]
                        votedOptionId = max_voted_option_id
                        userVoteAmount = str(int(int(minVoteAmount) * 1.1))
                        voteContractAddress = response['voteContractAddress']
                        log_and_print(f"{alias} get_detailVoteInfo successfully max_voted_option_id {max_voted_option_id} voteTitle {voteTitle}")
                    except Exception as e:
                        log_and_print(f"{alias} get_detailVoteInfo failed: {e}")
                        excel_manager.update_info(alias, f"get_detailVoteInfo failed: {e}")
                        return False

                    if abCHIPS_value > int(userVoteAmount) /(10 ** decimal):
                        try:
                            response = self.post_authorize(voteId,userVoteAmount,mockGameId,votedOptionId)
                            if 'error' in response:
                                raise Exception(f"Error: {response}")
                            nonce = response["nonce"]
                            createdAt = response["createdAt"]
                            signature = response["signature"]
                            log_and_print(f"{alias} post_authorize successfully")
                        except Exception as e:
                            log_and_print(f"{alias} post_authorize failed: {e}")
                            excel_manager.update_info(alias, f"post_authorize failed: {e}")
                            return False
                        
                        result,hash = self.perform_voteForAbCHIPS(userVoteAmount,votedOptionId,voteContractAddress,createdAt,nonce,signature)
                        if  result == False:
                            return False

                        try:
                            response = self.post_userVote(voteId,userVoteAmount,mockGameId,votedOptionId,hash)
                            if 'error' in response:
                                raise Exception(f"Error: {response}")
                            log_and_print(f"{alias} post_userVote successfully")
                        except Exception as e:
                            log_and_print(f"{alias} post_userVote failed: {e}")
                            excel_manager.update_info(alias, f"post_userVote failed: {e}")
                            return False

        try:
            response = self.get_unclaimedVoteTask()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            log_and_print(f"{alias} get_unclaimedVoteTask successfully")
            unclaimedVoteTask_ids = [item['voteId'] for item in response['data']]
        except Exception as e:
            log_and_print(f"{alias} get_unclaimedVoteTask failed: {e}")
            excel_manager.update_info(alias, f"get_unclaimedVoteTask failed: {e}")
            return False

        try:
            response = self.get_lastWeekAbChipsSpendSILVER()
            response = self.get_lastWeekAbChipsSpendSILVERWOOD()
            #这不校验结果
        except Exception as e:
            pass   

        for unclaimedVoteTask in unclaimedVoteTask_ids:
            try:
                response = self.get_votedTaskInfo(unclaimedVoteTask)
                if 'error' in response:
                    raise Exception(f"Error: {response}")
                log_and_print(f"{alias} get_votedTaskInfo {unclaimedVoteTask} successfully")
                vote_contract_address = response['voteContractAddress']
            except Exception as e:
                log_and_print(f"{alias} get_votedTaskInfo {unclaimedVoteTask}  failed: {e}")
                excel_manager.update_info(alias, f"get_votedTaskInfo {unclaimedVoteTask}  failed: {e}")
                return False

            try:
                response = self.get_claimauthorize(unclaimedVoteTask)
                if 'error' in response:
                    raise Exception(f"Error: {response}")
                log_and_print(f"{alias} get_claimauthorize {unclaimedVoteTask} successfully")
                signature = response["signature"]
                createdAt = response["createdAt"]
                nonce = response["nonce"]
                amount = response["amount"]
            except Exception as e:
                log_and_print(f"{alias} get_claimauthorize {unclaimedVoteTask}  failed: {e}")
                excel_manager.update_info(alias, f"get_claimauthorize {unclaimedVoteTask}  failed: {e}")
                return False

            result,hash = self.perform_claim(amount,vote_contract_address,createdAt,nonce,signature)
            if  result == False:
                return False

            try:
                response = self.post_claim(unclaimedVoteTask)
                if 'error' in response:
                    raise Exception(f"Error: {response}")
                log_and_print(f"{alias} post_claim successfully")
            except Exception as e:
                log_and_print(f"{alias} post_claim failed: {e}")
                excel_manager.update_info(alias, f"post_claim failed: {e}")
                return False

        try:
            response = self.get_silverSbtCriteria()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            bnb_vote_5_times = response['BNB_VOTE_5_TIMES']['completed'] >= response['BNB_VOTE_5_TIMES']['total']
            bnb_add_vote_1_time = response['BNB_ADD_VOTE_1_TIME']['completed'] >= response['BNB_ADD_VOTE_1_TIME']['total']
            bnb_win_and_claim_1_time = response['BNB_WIN_AND_CLAIM_1_TIME']['completed'] >= response['BNB_WIN_AND_CLAIM_1_TIME']['total']
            bnb_silver_criteria_airdrop = response['BNB_SILVER_CRITERIA_AIRDROP']['completed']
            nft_sbt_silver = response['NFT_SBT_SILVER']['completed']
            bnb_silver_criteria_airdrop_canClaim = response['BNB_SILVER_CRITERIA_AIRDROP']['canClaim'] and response['BNB_SILVER_CRITERIA_AIRDROP']['completed'] == 0
            nft_sbt_silver_canClaim = response['NFT_SBT_SILVER']['canClaim'] and response['NFT_SBT_SILVER']['completed'] == 0

            excel_manager.update_info(alias, f" {bnb_vote_5_times} ", "bnb_vote_5_times")
            excel_manager.update_info(alias, f" {bnb_add_vote_1_time} ", "bnb_add_vote_1_time")
            excel_manager.update_info(alias, f" {bnb_win_and_claim_1_time} ", "bnb_win_and_claim_1_time")
            excel_manager.update_info(alias, f" {bnb_silver_criteria_airdrop} ", "bnb_silver_criteria_airdrop")
            excel_manager.update_info(alias, f" {nft_sbt_silver} ", "nft_sbt_silver")
            log_and_print(f"{alias} get_silverSbtCriteria successfully bnb_vote_5_times {bnb_vote_5_times} bnb_add_vote_1_time {bnb_add_vote_1_time} bnb_win_and_claim_1_time {bnb_win_and_claim_1_time} bnb_silver_criteria_airdrop {bnb_silver_criteria_airdrop} nft_sbt_silver {nft_sbt_silver}")
        except Exception as e:
            log_and_print(f"{alias} get_silverSbtCriteria failed: {e}")
            excel_manager.update_info(alias, f"get_silverSbtCriteria failed: {e}")
            return False

        if bnb_silver_criteria_airdrop_canClaim == 1:
            try:
                response = self.get_bnbSilverCriteriaAirdrop()
                if 'error' in response:
                    raise Exception(f"Error: {response}")
                log_and_print(f"{alias} get_bnbSilverCriteriaAirdrop successfully")
            except Exception as e:
                log_and_print(f"{alias} get_bnbSilverCriteriaAirdrop failed: {e}")
                excel_manager.update_info(alias, f"get_bnbSilverCriteriaAirdrop failed: {e}")
                return False       

        try:
            response = self.get_lastWeekAbChipsSpendSILVER()
            response = self.get_lastWeekAbChipsSpendSILVERWOOD()
            #这不校验结果
        except Exception as e:
            pass   

        try:
            response = self.get_profile()
            response = self.get_hasPoppedMembershipCard()
            #这不校验结果
        except Exception as e:
            pass

        if nft_sbt_silver_canClaim == 1:
            try:
                response = self.get_nftQuestauthorize()
                if 'error' in response:
                    raise Exception(f"Error: {response.text}")
                log_and_print(f"{alias} get_nftQuestauthorize successfully")
            except Exception as e:
                log_and_print(f"{alias} get_nftQuestauthorize failed: {e}")
                excel_manager.update_info(alias, f"get_nftQuestauthorize failed: {e}")
                return False  

            result,hash = self.perform_mintStellar(response.text)
            if  result == False:
                return False
        try:
            response = self.get_points()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            for balance in response:
                total_balance = int(balance['totalBalance'])
                decimal = balance['decimal']
                if balance['point'] == 'abETH':
                    abETH_value = total_balance / (10 ** decimal)
                elif balance['point'] == 'abCHIPS':
                    abCHIPS_value = total_balance / (10 ** decimal)
            log_and_print(f"{alias} get_points successfully  abETH_value {abETH_value} abCHIPS_value {abCHIPS_value}")
            excel_manager.update_info(alias, f"abETH_value {abETH_value} abCHIPS_value {abCHIPS_value} claimed_value {claimed_value}", "INFO")
        except Exception as e:
            log_and_print(f"{alias} get_points failed: {e}")
            excel_manager.update_info(alias, f"get_points failed: {e}")
            return False

        try:
            response = self.get_silverSbtCriteria()
            if 'error' in response:
                raise Exception(f"Error: {response}")
            bnb_vote_5_times = response['BNB_VOTE_5_TIMES']['completed'] >= response['BNB_VOTE_5_TIMES']['total']
            bnb_add_vote_1_time = response['BNB_ADD_VOTE_1_TIME']['completed'] >= response['BNB_ADD_VOTE_1_TIME']['total']
            bnb_win_and_claim_1_time = response['BNB_WIN_AND_CLAIM_1_TIME']['completed'] >= response['BNB_WIN_AND_CLAIM_1_TIME']['total']
            bnb_silver_criteria_airdrop = response['BNB_SILVER_CRITERIA_AIRDROP']['completed']
            nft_sbt_silver = response['NFT_SBT_SILVER']['completed']
            bnb_silver_criteria_airdrop_canClaim = response['BNB_SILVER_CRITERIA_AIRDROP']['canClaim']
            nft_sbt_silver_canClaim = response['NFT_SBT_SILVER']['canClaim']
            excel_manager.update_info(alias, f" {bnb_vote_5_times} ", "bnb_vote_5_times")
            excel_manager.update_info(alias, f" {bnb_add_vote_1_time} ", "bnb_add_vote_1_time")
            excel_manager.update_info(alias, f" {bnb_win_and_claim_1_time} ", "bnb_win_and_claim_1_time")
            excel_manager.update_info(alias, f" {bnb_silver_criteria_airdrop} ", "bnb_silver_criteria_airdrop")
            excel_manager.update_info(alias, f" {nft_sbt_silver} ", "nft_sbt_silver")
            log_and_print(f"{alias} get_silverSbtCriteria successfully bnb_vote_5_times {bnb_vote_5_times} bnb_add_vote_1_time {bnb_add_vote_1_time} bnb_win_and_claim_1_time {bnb_win_and_claim_1_time} bnb_silver_criteria_airdrop {bnb_silver_criteria_airdrop} nft_sbt_silver {nft_sbt_silver}")
        except Exception as e:
            log_and_print(f"{alias} get_silverSbtCriteria failed: {e}")
            excel_manager.update_info(alias, f"get_silverSbtCriteria failed: {e}")
            return False

if __name__ == '__main__':
    app = alphaorbeta()
    retry_list = []
    failed_list = []
    proxyApp = socket5SwitchProxy(logger = log_and_print)
    UserInfoApp = UserInfo(log_and_print)
    excel_manager = excelWorker("alphaorbeta", log_and_print)
    alais_list = UserInfoApp.find_alias_by_path()
    for alias in alais_list:
        log_and_print(f"statring running by alias {alias}")
        key = UserInfoApp.find_ethinfo_by_alias_in_file(alias)
        account = web3.Account.from_key(key)    
        proxyName = UserInfoApp.find_socket5proxy_by_alias_in_file(alias)
        if not proxyName:
            log_and_print(f"cannot find proxy username = {alias}")
            excel_manager.update_info(alias, f"cannot find proxy ")
            continue
        result, proxyinfo = proxyApp.change_proxy_until_success(proxyName)
        if result == False:
            log_and_print(f"change_proxy_until_success failed {alias}")
            excel_manager.update_info(alias, f"change_proxy_until_success failed")
            retry_list.append((alias, account))
            continue

        if(app.run(alias, account,proxyinfo) == False):
            retry_list.append((alias, account))

    if len(retry_list) != 0:
        log_and_print("start retry faile case")
        time.sleep(10)

    for alias, account in retry_list:
        proxyName = UserInfoApp.find_socket5proxy_by_alias_in_file(alias)
        if not proxyName:
            log_and_print(f"cannot find proxy username = {alias}")
            excel_manager.update_info(alias, f"cannot find proxy ")
            continue
        result, proxyinfo = proxyApp.change_proxy_until_success(proxyName)
        if result == False:
            log_and_print(f"change_proxy_until_success failed {alias}")
            excel_manager.update_info(alias, f"change_proxy_until_success failed")
            continue
        time.sleep(5)   
        if(app.run(alias, account,proxyinfo) == False):
            failed_list.append((alias, account))

    if len(failed_list) == 0:
        log_and_print(f"so lucky all is signed")

    for alias, account in failed_list:
        log_and_print(f"final failed username = {alias}")
    excel_manager.save_msg_and_stop_service()





