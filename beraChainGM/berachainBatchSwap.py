import time
import os
from eth_account.messages import encode_defunct
from web3 import Web3
import web3
import random
import sys
import datetime
import requests
from requests.exceptions import Timeout, RequestException
from requests.exceptions import SSLError
# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取当前脚本的父目录
parent_dir = os.path.dirname(script_dir)
sys.path.append(parent_dir)

# 现在可以从tools目录导入UserInfo
from tools.UserInfo import UserInfo
from tools.YesCaptchaClient import YesCaptchaClient
# 现在可以从tools目录导入excelWorker
from tools.excelWorker import excelWorker
from tools.switchProxy import ClashAPIManager
# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
# 构建新的日志文件路径，包含当前时间
log_file_path = rf'\\192.168.3.142\SuperWind\Study\bearGM_{current_time}.log'


def log_message(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{timestamp} - {text}"

def log_and_print(text):
    message = log_message(text)
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        print(message)
        log_file.write(message + '\n')

web3App = Web3(Web3.HTTPProvider('https://artio.rpc.berachain.com/'))

erc20_dex_contract = '0x0d5862FDbdd12490f9b4De54c236cff63B038074'
erc20_dex_abi = [
    {
        "type": "function",
        "name": "addLiquidity",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "receiver",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "assetsIn",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amountsIn",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "outputs": [
            {
                "name": "shares",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "shareAmounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            },
            {
                "name": "liquidity",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "liquidityAmounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "batchSwap",
        "inputs": [
            {
                "name": "kind",
                "type": "uint8",
                "internalType": "enum IERC20DexModule.SwapKind"
            },
            {
                "name": "swaps",
                "type": "tuple[]",
                "internalType": "struct IERC20DexModule.BatchSwapStep[]",
                "components": [
                    {
                        "name": "poolId",
                        "type": "address",
                        "internalType": "address"
                    },
                    {
                        "name": "assetIn",
                        "type": "address",
                        "internalType": "address"
                    },
                    {
                        "name": "amountIn",
                        "type": "uint256",
                        "internalType": "uint256"
                    },
                    {
                        "name": "assetOut",
                        "type": "address",
                        "internalType": "address"
                    },
                    {
                        "name": "amountOut",
                        "type": "uint256",
                        "internalType": "uint256"
                    },
                    {
                        "name": "userData",
                        "type": "bytes",
                        "internalType": "bytes"
                    }
                ]
            },
            {
                "name": "deadline",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "assets",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "createPool",
        "inputs": [
            {
                "name": "name",
                "type": "string",
                "internalType": "string"
            },
            {
                "name": "assetsIn",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amountsIn",
                "type": "uint256[]",
                "internalType": "uint256[]"
            },
            {
                "name": "poolType",
                "type": "string",
                "internalType": "string"
            },
            {
                "name": "options",
                "type": "tuple",
                "internalType": "struct IERC20DexModule.PoolOptions",
                "components": [
                    {
                        "name": "weights",
                        "type": "tuple[]",
                        "internalType": "struct IERC20DexModule.AssetWeight[]",
                        "components": [
                            {
                                "name": "asset",
                                "type": "address",
                                "internalType": "address"
                            },
                            {
                                "name": "weight",
                                "type": "uint256",
                                "internalType": "uint256"
                            }
                        ]
                    },
                    {
                        "name": "swapFee",
                        "type": "uint256",
                        "internalType": "uint256"
                    }
                ]
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "address",
                "internalType": "address"
            }
        ],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "getExchangeRate",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "baseAsset",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "quoteAsset",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getLiquidity",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "asset",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPoolName",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "string",
                "internalType": "string"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPoolOptions",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "tuple",
                "internalType": "struct IERC20DexModule.PoolOptions",
                "components": [
                    {
                        "name": "weights",
                        "type": "tuple[]",
                        "internalType": "struct IERC20DexModule.AssetWeight[]",
                        "components": [
                            {
                                "name": "asset",
                                "type": "address",
                                "internalType": "address"
                            },
                            {
                                "name": "weight",
                                "type": "uint256",
                                "internalType": "uint256"
                            }
                        ]
                    },
                    {
                        "name": "swapFee",
                        "type": "uint256",
                        "internalType": "uint256"
                    }
                ]
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPreviewAddLiquidityNoSwap",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "assets",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "outputs": [
            {
                "name": "shares",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "shareAmounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            },
            {
                "name": "liqOut",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "liquidityAmounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPreviewAddLiquidityStaticPrice",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "liquidity",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "outputs": [
            {
                "name": "shares",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "shareAmounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            },
            {
                "name": "liqOut",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "liquidityAmounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPreviewBatchSwap",
        "inputs": [
            {
                "name": "kind",
                "type": "uint8",
                "internalType": "enum IERC20DexModule.SwapKind"
            },
            {
                "name": "swaps",
                "type": "tuple[]",
                "internalType": "struct IERC20DexModule.BatchSwapStep[]",
                "components": [
                    {
                        "name": "poolId",
                        "type": "address",
                        "internalType": "address"
                    },
                    {
                        "name": "assetIn",
                        "type": "address",
                        "internalType": "address"
                    },
                    {
                        "name": "amountIn",
                        "type": "uint256",
                        "internalType": "uint256"
                    },
                    {
                        "name": "assetOut",
                        "type": "address",
                        "internalType": "address"
                    },
                    {
                        "name": "amountOut",
                        "type": "uint256",
                        "internalType": "uint256"
                    },
                    {
                        "name": "userData",
                        "type": "bytes",
                        "internalType": "bytes"
                    }
                ]
            }
        ],
        "outputs": [
            {
                "name": "asset",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPreviewBurnShares",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "asset",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "assets",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPreviewSharesForLiquidity",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "assets",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "outputs": [
            {
                "name": "shares",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "shareAmounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            },
            {
                "name": "liquidity",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "liquidityAmounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPreviewSharesForSingleSidedLiquidityRequest",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "asset",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "assets",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPreviewSwapExact",
        "inputs": [
            {
                "name": "kind",
                "type": "uint8",
                "internalType": "enum IERC20DexModule.SwapKind"
            },
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "baseAsset",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "baseAssetAmount",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "quoteAsset",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "asset",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getRemoveLiquidityExactAmountOut",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "assetIn",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "assetAmount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "assets",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getRemoveLiquidityOneSideOut",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "assetOut",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "sharesIn",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "assets",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getTotalShares",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "assets",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "removeLiquidityBurningShares",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "withdrawAddress",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "assetIn",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amountIn",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "liquidity",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "liquidityAmounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "removeLiquidityExactAmount",
        "inputs": [
            {
                "name": "pool",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "withdrawAddress",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "assetOut",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amountOut",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "sharesIn",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "maxSharesIn",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "shares",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "shareAmounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            },
            {
                "name": "liquidity",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "liquidityAmounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "swap",
        "inputs": [
            {
                "name": "kind",
                "type": "uint8",
                "internalType": "enum IERC20DexModule.SwapKind"
            },
            {
                "name": "poolId",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "assetIn",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amountIn",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "assetOut",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amountOut",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "deadline",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "assets",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "amounts",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "payable"
    }
]

honey_contract_address = '0x7EeCA4205fF31f947EdBd49195a7A88E6A91161B'
honey_abi = [
    {
        "type": "function",
        "name": "DOMAIN_SEPARATOR",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "bytes32",
                "internalType": "bytes32"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "allowance",
        "inputs": [
            {
                "name": "",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "approve",
        "inputs": [
            {
                "name": "spender",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "bool",
                "internalType": "bool"
            }
        ],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "balanceOf",
        "inputs": [
            {
                "name": "user",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "decimals",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "uint8",
                "internalType": "uint8"
            }
        ],
        "stateMutability": "pure"
    },
    {
        "type": "function",
        "name": "name",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "string",
                "internalType": "string"
            }
        ],
        "stateMutability": "pure"
    },
    {
        "type": "function",
        "name": "nonces",
        "inputs": [
            {
                "name": "",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "permit",
        "inputs": [
            {
                "name": "owner",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "spender",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "value",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "deadline",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "v",
                "type": "uint8",
                "internalType": "uint8"
            },
            {
                "name": "r",
                "type": "bytes32",
                "internalType": "bytes32"
            },
            {
                "name": "s",
                "type": "bytes32",
                "internalType": "bytes32"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "symbol",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "string",
                "internalType": "string"
            }
        ],
        "stateMutability": "pure"
    },
    {
        "type": "function",
        "name": "totalSupply",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "transfer",
        "inputs": [
            {
                "name": "to",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "bool",
                "internalType": "bool"
            }
        ],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "transferFrom",
        "inputs": [
            {
                "name": "from",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "to",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "bool",
                "internalType": "bool"
            }
        ],
        "stateMutability": "nonpayable"
    },
    {
        "type": "event",
        "name": "Approval",
        "inputs": [
            {
                "name": "owner",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "spender",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "value",
                "type": "uint256",
                "indexed": False,
                "internalType": "uint256"
            }
        ],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Transfer",
        "inputs": [
            {
                "name": "from",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "to",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "value",
                "type": "uint256",
                "indexed": False,
                "internalType": "uint256"
            }
        ],
        "anonymous": False
    }
]

wbera_contract = '0x5806E416dA447b267cEA759358cF22Cc41FAE80F'
wbera_abi = [
    {
        "type": "constructor",
        "inputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "receive",
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "allowance",
        "inputs": [
            {
                "name": "owner",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "spender",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "approve",
        "inputs": [
            {
                "name": "spender",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "value",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "bool",
                "internalType": "bool"
            }
        ],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "balanceOf",
        "inputs": [
            {
                "name": "account",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "decimals",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "uint8",
                "internalType": "uint8"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "deposit",
        "inputs": [],
        "outputs": [],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "name",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "string",
                "internalType": "string"
            }
        ],
        "stateMutability": "pure"
    },
    {
        "type": "function",
        "name": "symbol",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "string",
                "internalType": "string"
            }
        ],
        "stateMutability": "pure"
    },
    {
        "type": "function",
        "name": "totalSupply",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "transfer",
        "inputs": [
            {
                "name": "to",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "value",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "bool",
                "internalType": "bool"
            }
        ],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "transferFrom",
        "inputs": [
            {
                "name": "from",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "to",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "value",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "bool",
                "internalType": "bool"
            }
        ],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "withdraw",
        "inputs": [
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "event",
        "name": "Approval",
        "inputs": [
            {
                "name": "owner",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "spender",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "value",
                "type": "uint256",
                "indexed": False,
                "internalType": "uint256"
            }
        ],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Deposit",
        "inputs": [
            {
                "name": "from",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "indexed": False,
                "internalType": "uint256"
            }
        ],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Transfer",
        "inputs": [
            {
                "name": "from",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "to",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "value",
                "type": "uint256",
                "indexed": False,
                "internalType": "uint256"
            }
        ],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Withdrawal",
        "inputs": [
            {
                "name": "to",
                "type": "address",
                "indexed": True,
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "indexed": False,
                "internalType": "uint256"
            }
        ],
        "anonymous": False
    },
    {
        "type": "error",
        "name": "ERC20InsufficientAllowance",
        "inputs": [
            {
                "name": "spender",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "allowance",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "needed",
                "type": "uint256",
                "internalType": "uint256"
            }
        ]
    },
    {
        "type": "error",
        "name": "ERC20InsufficientBalance",
        "inputs": [
            {
                "name": "sender",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "balance",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "needed",
                "type": "uint256",
                "internalType": "uint256"
            }
        ]
    },
    {
        "type": "error",
        "name": "ERC20InvalidApprover",
        "inputs": [
            {
                "name": "approver",
                "type": "address",
                "internalType": "address"
            }
        ]
    },
    {
        "type": "error",
        "name": "ERC20InvalidReceiver",
        "inputs": [
            {
                "name": "receiver",
                "type": "address",
                "internalType": "address"
            }
        ]
    },
    {
        "type": "error",
        "name": "ERC20InvalidSender",
        "inputs": [
            {
                "name": "sender",
                "type": "address",
                "internalType": "address"
            }
        ]
    },
    {
        "type": "error",
        "name": "ERC20InvalidSpender",
        "inputs": [
            {
                "name": "spender",
                "type": "address",
                "internalType": "address"
            }
        ]
    }
]

erc20honey_contract = '0x09ec711b81cD27A6466EC40960F2f8D85BB129D9'
erc20honey_abi = [
    {
        "type": "function",
        "name": "erc20Module",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "address",
                "internalType": "contract IERC20BankModule"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getAMOCurrentLimit",
        "inputs": [
            {
                "name": "amoType",
                "type": "string",
                "internalType": "string"
            },
            {
                "name": "amoAddr",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getExchangable",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "tuple[]",
                "internalType": "struct ERC20HoneyModule.ERC20Exchangable[]",
                "components": [
                    {
                        "name": "collateral",
                        "type": "address",
                        "internalType": "contract IERC20"
                    },
                    {
                        "name": "enabled",
                        "type": "bool",
                        "internalType": "bool"
                    },
                    {
                        "name": "mintRate",
                        "type": "uint256",
                        "internalType": "uint256"
                    },
                    {
                        "name": "redemptionRate",
                        "type": "uint256",
                        "internalType": "uint256"
                    }
                ]
            }
        ],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "getTotalCollateral",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "address[]",
                "internalType": "address[]"
            },
            {
                "name": "",
                "type": "uint256[]",
                "internalType": "uint256[]"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getTotalSupply",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "honey",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "address",
                "internalType": "contract IERC20"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "honeyModule",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "address",
                "internalType": "contract IHoneyModule"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "mint",
        "inputs": [
            {
                "name": "to",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "collateral",
                "type": "address",
                "internalType": "contract IERC20"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "previewExactOutCollateral",
        "inputs": [
            {
                "name": "amountOut",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "assetOut",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "previewMint",
        "inputs": [
            {
                "name": "collateral",
                "type": "address",
                "internalType": "contract IERC20"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "previewRedeem",
        "inputs": [
            {
                "name": "collateral",
                "type": "address",
                "internalType": "contract IERC20"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "previewRequiredCollateral",
        "inputs": [
            {
                "name": "honeyOut",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "assetIn",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "redeem",
        "inputs": [
            {
                "name": "to",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "collateral",
                "type": "address",
                "internalType": "contract IERC20"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "updateParams",
        "inputs": [
            {
                "name": "params",
                "type": "tuple[]",
                "internalType": "struct ERC20HoneyModule.ERC20Exchangable[]",
                "components": [
                    {
                        "name": "collateral",
                        "type": "address",
                        "internalType": "contract IERC20"
                    },
                    {
                        "name": "enabled",
                        "type": "bool",
                        "internalType": "bool"
                    },
                    {
                        "name": "mintRate",
                        "type": "uint256",
                        "internalType": "uint256"
                    },
                    {
                        "name": "redemptionRate",
                        "type": "uint256",
                        "internalType": "uint256"
                    }
                ]
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "bool",
                "internalType": "bool"
            }
        ],
        "stateMutability": "nonpayable"
    }
]

nft0x_abi = [
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "allowlist_",
                "type": "bytes32"
            },
            {
                "internalType": "string",
                "name": "name_",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "symbol_",
                "type": "string"
            },
            {
                "internalType": "contract IERC20",
                "name": "paymentToken_",
                "type": "address"
            },
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "native",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "erc20",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct Ticket.MintCost",
                "name": "mintCost_",
                "type": "tuple"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [],
        "name": "AccountBalanceOverflow",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "AlreadyClaimed",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "BalanceQueryForZeroAddress",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "InvalidProof",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "NotOwnerNorApproved",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            }
        ],
        "name": "OwnableInvalidOwner",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            }
        ],
        "name": "OwnableUnauthorizedAccount",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "TokenAlreadyExists",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "TokenDoesNotExist",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "TransferFromIncorrectOwner",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "TransferToNonERC721ReceiverImplementer",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "TransferToZeroAddress",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "URIQueryForNonexistentToken",
        "type": "error"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "account",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "operator",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "bool",
                "name": "isApproved",
                "type": "bool"
            }
        ],
        "name": "ApprovalForAll",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "string",
                "name": "uri",
                "type": "string"
            }
        ],
        "name": "BaseURISet",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "user",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "root",
                "type": "bytes32"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "index",
                "type": "uint256"
            }
        ],
        "name": "Claimed",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "previousOwner",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "newOwner",
                "type": "address"
            }
        ],
        "name": "OwnershipTransferred",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "bool",
                "name": "generated",
                "type": "bool"
            }
        ],
        "name": "SetGenerated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "allowlist",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "",
                "type": "bytes32"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "result",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "buy",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "index_",
                "type": "uint256"
            },
            {
                "internalType": "bytes32[]",
                "name": "proof_",
                "type": "bytes32[]"
            }
        ],
        "name": "claim",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "claimAmount",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "index_",
                "type": "uint256"
            }
        ],
        "name": "claimed",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            }
        ],
        "name": "getApproved",
        "outputs": [
            {
                "internalType": "address",
                "name": "result",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "name": "hasMinted",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "operator",
                "type": "address"
            }
        ],
        "name": "isApprovedForAll",
        "outputs": [
            {
                "internalType": "bool",
                "name": "result",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "isGenerated",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "mintCost",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "native",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "erc20",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            }
        ],
        "name": "ownerOf",
        "outputs": [
            {
                "internalType": "address",
                "name": "result",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "paymentToken",
        "outputs": [
            {
                "internalType": "contract IERC20",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "realOwner",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "renounceOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            }
        ],
        "name": "safeTransferFrom",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            },
            {
                "internalType": "bytes",
                "name": "data",
                "type": "bytes"
            }
        ],
        "name": "safeTransferFrom",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "allowlist_",
                "type": "bytes32"
            }
        ],
        "name": "setAllowList",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "operator",
                "type": "address"
            },
            {
                "internalType": "bool",
                "name": "isApproved",
                "type": "bool"
            }
        ],
        "name": "setApprovalForAll",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "baseURI_",
                "type": "string"
            }
        ],
        "name": "setBaseURI",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "claimAmount_",
                "type": "uint256"
            }
        ],
        "name": "setClaimAmount",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bool",
                "name": "generated_",
                "type": "bool"
            }
        ],
        "name": "setGenerated",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "uint256",
                        "name": "native",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "erc20",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct Ticket.MintCost",
                "name": "mintCost_",
                "type": "tuple"
            }
        ],
        "name": "setMintCost",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "contract IERC20",
                "name": "paymentToken_",
                "type": "address"
            }
        ],
        "name": "setPaymentToken",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes4",
                "name": "interfaceId",
                "type": "bytes4"
            }
        ],
        "name": "supportsInterface",
        "outputs": [
            {
                "internalType": "bool",
                "name": "result",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            }
        ],
        "name": "tokenURI",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "from",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "id",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "newOwner",
                "type": "address"
            }
        ],
        "name": "transferLowerOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "newOwner",
                "type": "address"
            }
        ],
        "name": "transferOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "newRealOwner",
                "type": "address"
            }
        ],
        "name": "transferRealOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "stateMutability": "payable",
        "type": "receive"
    }
]

bend_contract = '0x9261b5891d3556e829579964B38fe706D0A2D04a'
bend_abi = [
    {
        "type": "function",
        "name": "supply",
        "inputs": [
            {
                "name": "asset",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "amount",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "onBehalfOf",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "referralCode",
                "type": "uint16",
                "internalType": "uint16"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "admin",
                "type": "address"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "implementation",
                "type": "address"
            }
        ],
        "name": "Upgraded",
        "type": "event"
    },
    {
        "stateMutability": "payable",
        "type": "fallback"
    },
    {
        "inputs": [],
        "name": "admin",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "implementation",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_logic",
                "type": "address"
            },
            {
                "internalType": "bytes",
                "name": "_data",
                "type": "bytes"
            }
        ],
        "name": "initialize",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "newImplementation",
                "type": "address"
            }
        ],
        "name": "upgradeTo",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "newImplementation",
                "type": "address"
            },
            {
                "internalType": "bytes",
                "name": "data",
                "type": "bytes"
            }
        ],
        "name": "upgradeToAndCall",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]


def get_gasprice():
    return web3App.to_wei('50', 'gwei')


def get_preview(contract_address, your_contract_abi, kind, pool_id, asset_in, amount_in, asset_out):
    # 构建预览交易参数
    get_preview_swap_function = web3App.eth.contract(
        address=contract_address,
        abi=your_contract_abi  # 替换为合约 ABI
    ).functions.getPreviewSwapExact

    # 替换以下参数为实际参数
    get_preview_swap_input_data = get_preview_swap_function(
        kind,  # uint8 类型参数
        pool_id,  # address 类型参数
        asset_in,  # address 类型参数
        amount_in,  # uint256 类型参数
        asset_out,  # address 类型参数
    ).call()

    # 获取预览交易返回的 amount 参数
    amount = get_preview_swap_input_data[1]

    log_and_print(f'兑换数量为：{amount / 1000000000000000000}')
    return amount


def do_swap(address,
            private_key,
            contract_address,
            contract_abi,
            kind,
            pool_id,
            asset_in,
            amount_in,
            asset_out,
            amount):
    # 截止时间设置
    current_timestamp = int(time.time())
    deadline_timestamp = current_timestamp + 300  # 300 秒后

    swap_input_data = web3App.eth.contract(
        address=contract_address,
        abi=contract_abi  # 替换为合约 ABI
    ).functions.batchSwap(
        kind,
        [
            {
                "poolId": pool_id,
                "assetIn": asset_in,
                "amountIn": int(amount_in),
                "assetOut": asset_out,
                "amountOut": int(amount),
                "userData": b"0x"
            }
        ],
        deadline_timestamp
    ).build_transaction({
        'from': address,
        # 'to': contract_address,
        'gas': 50000,

        'gasPrice': get_gasprice(),
        'nonce': web3App.eth.get_transaction_count(address),

    })

    # 使用私钥签名交易
    signed_transaction = web3App.eth.account.sign_transaction(swap_input_data, private_key)

    log_and_print(f'入金额：{amount_in}')
    log_and_print(f'出金额：{amount}')
    log_and_print(f'签名参数：{signed_transaction}')

    # 发送交易
    transaction_hash = web3App.eth.send_raw_transaction(signed_transaction.rawTransaction).hex()
    #
    log_and_print(f'发送兑换交易哈希：{transaction_hash},等待240s获取交易结果')
    time.sleep(240)
    receipt = web3App.eth.get_transaction_receipt(transaction_hash)
    if receipt['status'] == 1:
        log_and_print('交易成功')
    else:
        log_and_print(f'交易失败，原因：{receipt}')


def do_approve(address,
               private_key,
               contract_address,
               contract_abi,
               amount,
               to_address):
    swap_input_data = web3App.eth.contract(
        address=contract_address,
        abi=contract_abi  # 替换为合约 ABI
    ).functions.approve(
        to_address,
        amount
    ).build_transaction({
        'from': address,
        # 'to': to_address,
        'gas': 50000,
        'gasPrice': get_gasprice(),
        'nonce': web3App.eth.get_transaction_count(address),

    })

    # 使用私钥签名交易
    signed_transaction = web3App.eth.account.sign_transaction(swap_input_data, private_key)

    log_and_print(f'签名参数：{signed_transaction}')
    try:

        # 发送交易
        transaction_hash = web3App.eth.send_raw_transaction(signed_transaction.rawTransaction).hex()

        log_and_print(f'发送兑换交易哈希：{transaction_hash},等待240s获取交易结果')
        time.sleep(240)
        receipt = web3App.eth.get_transaction_receipt(transaction_hash)
        if receipt['status'] == 1:
            log_and_print('交易成功')
        else:
            log_and_print(f'交易失败，原因：{receipt}')
            exit('失败，停止操作')
    except Exception as e:
        log_and_print(f"出现错误: {e}")


def get_allowance(address,
                  sender_address,
                  contract_address,
                  contract_abi):
    try:
        swap_input_data = web3App.eth.contract(
            address=contract_address,
            abi=contract_abi  # 替换为合约 ABI
        ).functions.allowance(
            address,
            sender_address
        ).call()

        log_and_print(f'允许的信息：{swap_input_data / 1000000000000000000}')
        return swap_input_data
    except Exception as e:
        log_and_print(f"出现错误: {e}")
        return 0


def deposit_bera(address, address_key):
    log_and_print(f'地址{address}转换wbera')
    # 创建代币合约实例
    address = web3App.to_checksum_address(address)
    nonce = web3App.eth.get_transaction_count(address)

    # 以太坊转 WETH 的数量（以最小单位表示）
    eth_amount = Web3.to_wei(0.001, 'ether')

    transaction = web3App.eth.contract(
        address=wbera_contract,
        abi=wbera_abi
    ).functions.deposit(
    ).build_transaction({
        'value': eth_amount,
        'gas': 250000,
        'gasPrice': web3App.to_wei('100', 'gwei'),
        'nonce': nonce,
    })

    # 使用私钥签名交易
    signed_transaction = web3App.eth.account.sign_transaction(transaction, address_key)

    # 发送交易
    transaction_hash = web3App.eth.send_raw_transaction(signed_transaction.rawTransaction).hex()

    log_and_print(f'转换wbera发送哈希：{transaction_hash}')
    return transaction_hash


def mint_honey(address,
               address_key,
               contract_address,
               contract_abi,
               amount):
    mint_input_data = web3App.eth.contract(
        address=contract_address,
        abi=contract_abi  # 替换为合约 ABI
    ).functions.mint(
        address,
        '0x6581e59A1C8dA66eD0D313a0d4029DcE2F746Cc5',  # 固定用这个erc20代币去mint honey
        amount
    ).build_transaction({
        'from': address,
        # 'to': to_address,
        'gas': 200000,
        'gasPrice': get_gasprice(),
        'nonce': web3App.eth.get_transaction_count(address),

    })

    # 使用私钥签名交易
    signed_transaction = web3App.eth.account.sign_transaction(mint_input_data, address_key)

    log_and_print(f'签名参数：{signed_transaction}')

    # 发送交易
    transaction_hash = web3App.eth.send_raw_transaction(signed_transaction.rawTransaction).hex()
    #
    log_and_print(f'发送兑换交易哈希：{transaction_hash},等待200s获取交易结果')
    time.sleep(200)
    receipt = web3App.eth.get_transaction_receipt(transaction_hash)
    if receipt['status'] == 1:
        log_and_print('交易成功')
    else:
        log_and_print(f'交易失败，原因：{receipt}')
        exit('失败，停止操作')


def up_log(address, status):
    requests.get(f'http://38.54.119.53:47387/api/index/update_bera_address?address={address}&status={status}')


def buy_nft(address,
            address_key,
            contract_address,
            contract_abi):
    mint_input_data = web3App.eth.contract(
        address=contract_address,
        abi=contract_abi  # 替换为合约 ABI
    ).functions.buy(
    ).build_transaction({
        'from': address,
        # 'to': to_address,
        'gas': 50000,
        'gasPrice': get_gasprice(),
        'nonce': web3App.eth.get_transaction_count(address),

    })

    # 使用私钥签名交易
    signed_transaction = web3App.eth.account.sign_transaction(mint_input_data, address_key)

    log_and_print(f'签名参数：{signed_transaction}')

    # 发送交易
    transaction_hash = web3App.eth.send_raw_transaction(signed_transaction.rawTransaction).hex()
    #
    log_and_print(f'发送兑换交易哈希：{transaction_hash},等待200s获取交易结果')
    time.sleep(200)
    receipt = web3App.eth.get_transaction_receipt(transaction_hash)
    if receipt['status'] == 1:
        log_and_print('交易成功')
    else:
        log_and_print(f'交易失败，原因：{receipt}')
        exit('失败，停止操作')


def balanceof_nft(address,
                  contract_address,
                  contract_abi):
    data = web3App.eth.contract(
        address=contract_address,
        abi=contract_abi  # 替换为合约 ABI
    ).functions.balanceOf(
        address
    ).call()
    # 输出nft余额数量
    log_and_print(f'OG卡数量：{data}')
    return data


def do_supply(address,
              address_key,
              contract_address,
              contract_abi,
              amount):

    mint_input_data = {
        'chainId': 80085,
        'from': address,
        'to': contract_address,
        'gas': 50000,
        'gasPrice': get_gasprice(),
        'value': 0,
        'data': '0x617ba0370000000000000000000000007eeca4205ff31f947edbd49195a7a88e6a91161b0000000000000000000000000000000000000000000000000de0b6b3a76400000000000000000000000000003904a82A3Faf22E93eb98DB1DBd330f581633E9b0000000000000000000000000000000000000000000000000000000000000000',
        # 数据字段通常为空，因为调用的是合约的 fallback 函数
        'nonce': web3App.eth.get_transaction_count(address),
    }

    # 使用私钥签名交易
    signed_transaction = web3App.eth.account.sign_transaction(mint_input_data, address_key)

    log_and_print(f'签名参数：{signed_transaction}')

    # 发送交易
    transaction_hash = web3App.eth.send_raw_transaction(signed_transaction.rawTransaction).hex()
    #
    log_and_print(f'发送兑换交易哈希：{transaction_hash},等待200s获取交易结果')
    time.sleep(200)
    receipt = web3App.eth.get_transaction_receipt(transaction_hash)
    if receipt['status'] == 1:
        log_and_print('交易成功')
    else:
        log_and_print(f'交易失败，原因：{receipt}')
        exit('失败，停止操作')


if __name__ == '__main__':
    UserInfoApp = UserInfo(log_and_print)
    credentials_list = UserInfoApp.find_user_credentials_for_eth("bearSwap")
    for credentials in credentials_list:
        alias = credentials["alias"]
        address_key = credentials["key"]
        address =  web3.Account.from_key(address_key).address

        stg_allowance = get_allowance(address, '0x09ec711b81cD27A6466EC40960F2f8D85BB129D9',
                                    '0x6581e59A1C8dA66eD0D313a0d4029DcE2F746Cc5', honey_abi)
        # 授权金额
        num = random.randint(100000, 159999) / 10000
        log_and_print(f'金额：{num}')
        if stg_allowance < 10:
            log_and_print('未授权，执行授权stgusdc合约给honey')
            ##授权stgusdc转换成为honey
            do_approve(address, address_key, '0x6581e59A1C8dA66eD0D313a0d4029DcE2F746Cc5', honey_abi,
                    int(web3App.to_wei(100000, 'ether')), '0x09ec711b81cD27A6466EC40960F2f8D85BB129D9')

            log_and_print('授权stgusdc合约给honey成功')
            up_log(address, 1)

            # 授权完成后 mint honey
            mint_honey(address, address_key, erc20honey_contract, erc20honey_abi, int(web3App.to_wei(num, 'ether')))
            log_and_print('mint honey 成功')
            up_log(address, 2)
        else:
            # 授权完成后 mint honey
            mint_honey(address, address_key, erc20honey_contract, erc20honey_abi, int(web3App.to_wei(num, 'ether')))
            log_and_print('mint honey 成功')
            up_log(address, 2)
        # 查询ognft是否有存在
        balanceof_og = balanceof_nft(address, '0x6553444CaA1d4FA329aa9872008ca70AE6131925', nft0x_abi)
        if balanceof_og == 0:
            og_allowance = get_allowance(address, '0x6553444CaA1d4FA329aa9872008ca70AE6131925',
                                        '0x7EeCA4205fF31f947EdBd49195a7A88E6A91161B', honey_abi)
            if og_allowance < 10:
                log_and_print('未授权，执行授权honey合约给og')
                # 授权honey给0x og合约
                do_approve(address, address_key, '0x7EeCA4205fF31f947EdBd49195a7A88E6A91161B', honey_abi,
                        int(web3App.to_wei(10, 'ether')), '0x6553444CaA1d4FA329aa9872008ca70AE6131925')
                log_and_print('授权honey合约给 0xOGnft成功')
                up_log(address, 3)
                ##购买ognft
                buy_nft(address, address_key, '0x6553444CaA1d4FA329aa9872008ca70AE6131925', nft0x_abi)
                up_log(address, 4)
                log_and_print('购买 0xOGnft成功')
            else:
                ##购买ognft
                buy_nft(address, address_key, '0x6553444CaA1d4FA329aa9872008ca70AE6131925', nft0x_abi)
                up_log(address, 4)
                log_and_print('购买 0xOGnft成功')
        # love的nft是否持有
        balanceof_love = balanceof_nft(address, '0x6553444CaA1d4FA329aa9872008ca70AE6131925', nft0x_abi)
        if balanceof_love == 0:
            glove_allowance = get_allowance(address, '0xAd8fD889c77Ba37cECc0A4148C6917a4582c15DB',
                                            '0x7EeCA4205fF31f947EdBd49195a7A88E6A91161B', honey_abi)
            if glove_allowance < 10:
                log_and_print('未授权，执行授权honey合约给情人节合约')
                # 授权honey给0x 情人节合约
                do_approve(address, address_key, '0x7EeCA4205fF31f947EdBd49195a7A88E6A91161B', honey_abi,
                        int(web3App.to_wei(10, 'ether')), '0xAd8fD889c77Ba37cECc0A4148C6917a4582c15DB')
                log_and_print('授权honey合约给 0x情人节nft成功')
                up_log(address, 5)
                # 购买情人节nft
                buy_nft(address, address_key, '0xAd8fD889c77Ba37cECc0A4148C6917a4582c15DB', nft0x_abi)
                up_log(address, 6)
                log_and_print('购买 0x情人节nft成功')
            else:
                # 购买情人节nft
                buy_nft(address, address_key, '0xAd8fD889c77Ba37cECc0A4148C6917a4582c15DB', nft0x_abi)
                up_log(address, 6)
                log_and_print('购买 0x情人节nft成功')

        bend_allowance = get_allowance(address, bend_contract,
                                    '0x7EeCA4205fF31f947EdBd49195a7A88E6A91161B', honey_abi)
        if bend_allowance < 0:
            log_and_print('未授权，执行授权honey合约给honey合约')
            # # 授权honey给bend合约
            do_approve(address, address_key, '0x7EeCA4205fF31f947EdBd49195a7A88E6A91161B', honey_abi,
                    int(web3App.to_wei(100000, 'ether')), bend_contract)

