from web3 import Web3
import requests
import urllib

INFURA_SECRET_KEY = 'a7f5d1deacc9493f9af85bcd625822f3'
'''
私钥:0xe9e850cecc5446d0912d42b99e7e9948290d34c66f336af388a0fac67c639a9c
地址:0x34E9A2170099F09426f86D54dDC41Eb0d0316d91

私钥:0xd6571033428011e456300faf60c73f3646bc7291e6d96beb3c3c3e415c4ceba0
地址:0x82fC4A0aEC04096Eb4ed85bd50cF3e3D2819D85D
'''


def generate_account():
    # 生成新的私钥和账户地址
    acct = Web3().eth.account.create()
    private_key = acct._private_key.hex()
    address = acct.address
    return private_key, address



# get w3 endpoint by network name
def get_w3_by_network(network='mainnet'):
    infura_url = f'https://{network}.infura.io/v3/{INFURA_SECRET_KEY}' # 接入 Infura 节点
    w3 = Web3(Web3.HTTPProvider(infura_url))
    return w3


def check_balance(web3Instance, address):
    if web3Instance.is_connected() == False:
        print(f'连接断开')
        return 0
    addr = Web3.to_checksum_address(address)
    balance = web3Instance.eth.get_balance(addr) / 1e18
    print(f'地址:{hex(address) },余额: {balance }')


def transfer_eth(w3,from_address,private_key,target_address,amount,gas_price=5,gas_limit=21000,chainId=4):
    from_address = Web3.to_checksum_address(from_address)
    target_address = Web3.to_checksum_address(target_address)
    nonce = w3.eth.get_transaction_count(from_address) # 获取 nonce 值
    params = {
        'from': from_address,
        'nonce': nonce,
        'to': target_address,
        'value': w3.to_wei(amount, 'ether'),
        'gas': gas_limit,
        'maxFeePerGas': w3.to_wei(gas_price, 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei(gas_price, 'gwei'),
        'chainId': chainId,
        
    }
    try:
        signed_tx = w3.eth.account.sign_transaction(params, private_key=private_key)
        txn = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return {'status': 'succeed', 'txn_hash': w3.toHex(txn), 'task': 'Transfer ETH'}
    except Exception as e:
        return {'status': 'failed', 'error': e, 'task': 'Transfer ETH'}


'''
合约交互比起普通转账，又要复杂了一些,会需要额外几个参数：
▪️ 合约地址
▪️ 合约ABI
▪️ 交互的函数名称及具体参数

一般情况下，我们可以拆解为以下三个步骤来完成：
先在Arbitrum官方跨链桥测试网页面手工交互
接着从交互记录，找到 Etherscan上合约地址
定位到合约 "Write Contract" 中的 "depositEth" 函数，获取函数名称及对应参数
'''
def bridge_arbitrum_eth(w3, from_address, private_key, contract_address, amount_in_ether, chainId):
    from_address = Web3.to_checksum_address(from_address)
    contract_address = Web3.to_checksum_address(contract_address)

    ABI = '[{"inputs":\
                [{"internalType":"uint256","name":"maxSubmissionCost","type":"uint256"}],\
                "name":"depositEth","outputs":\
                    [{"internalType":"uint256","name":"","type":"uint256"}],\
                "stateMutability":"payable","type":"function"}]'
    
    amount_in_wei = w3.to_wei(amount_in_ether, 'ether')
    maxSubmissionCost = int(amount_in_wei * 0.01) # 定义参数值
    nonce = w3.eth.get_transaction_count(from_address)

    params = {
        'chainId': chainId,
        'gas': 250000,
        'nonce': nonce,
        'from': from_address,
        'value': amount_in_wei,
        'maxFeePerGas': w3.to_wei(5, 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei(5, 'gwei'),
        'chainId': chainId,
    }
    contract = w3.eth.contract(address=contract_address, abi=ABI)

    # 调用合约的 depositEth 函数，参数为 maxSubmissionCost
    func = contract.functions.depositEth(maxSubmissionCost)
    try:
        tx = func.buildTransaction(params)
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
        txn = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return {'status': 'succeed', 'txn_hash': w3.toHex(txn), 'task': 'Bridge ETH'}
    except Exception as e:
        return {'status': 'failed', 'error': e, 'task': 'Bridge ETH'}

if __name__ == "__main__":
    #web3app = get_w3_by_network()
    #check_balance(web3app,0x220866b1a2219f40e72f5c628b65d54268ca3a9d)

    ''' 转账
    web3app = get_w3_by_network('goerli')
    private_key = 0xe9e850cecc5446d0912d42b99e7e9948290d34c66f336af388a0fac67c639a9c
    from_address = 0x34E9A2170099F09426f86D54dDC41Eb0d0316d91
    target_address = 0x82fC4A0aEC04096Eb4ed85bd50cF3e3D2819D85D
    check_balance(web3app,from_address)
    check_balance(web3app,target_address)
    amount = 0.01
    chainId = 0x5  // 可以在chainlist那边查看
    result = transfer_eth(web3app, from_address, private_key, target_address, amount, chainId=chainId)
    print(result)
    check_balance(web3app,from_address)
    check_balance(web3app,target_address)
    '''

    '''测试网跨链桥'''
    web3app = get_w3_by_network('goerli')
    from_address = 0x365a800a3c6a6B73B29E052fd4F7e68BFD45A086
    private_key = 'e2facfbd1f0736318382d87b81029b05b7650ba17467c844cea5998a40e5bbc2'
    contract_address = '0x578BAde599406A8fE3d24Fd7f7211c0911F5B29e'
    amount_in_ether = 0.088
    chainId = 5
    check_balance(web3app,from_address)

    result = bridge_arbitrum_eth(web3app, from_address, private_key, contract_address, amount_in_ether, chainId)
    print(result)
    