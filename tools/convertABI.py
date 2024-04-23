from web3 import Web3
from eth_abi import encode

def split_contract_data(data):
    method_id = data[:10]
    print(f"MethodID=\"{method_id}\"")

    # Remaining data are parameters, each 64 characters long
    params = data[10:]
    param_length = 64
    param_list = [params[i:i+param_length] for i in range(0, len(params), param_length)]

    # Print each parameter
    for idx, param in enumerate(param_list, start=1):
        print(f"param_{idx}=\"{param}\"")

# Example usage
contract_data = "0x32b7006d000000000000000000000000deaddeaddeaddeaddeaddeaddeaddeaddead0000000000000000000000000000000000000000000000000000000e35fa931a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000"
split_contract_data(contract_data)

func_signature =  'transfer(address,uint256)'
function_id = Web3.keccak(text=func_signature)[:4].hex()
print(function_id)


# 定义你的参数和它们的类型
values = [
    1709036636,  # deadline, uint256
    203314,  # voyageId, uint256
    [2,3,4],  # destinations, uint16[]
    Web3.to_bytes(hexstr="0x9f83f1bdc4255f9a81401c66eeac7004972f75e517c4552738b0e0d9cb2872b4"),  # data, bytes32
    Web3.to_bytes(hexstr="0x2c744dd258d055e9aad4814247cdf79aefdeab3bc949f04a08c13ef394b2e6bb3b3a8ff76762691ee59c4d3a8475cd5113079e0bcdf3c21b7ef14d5f4822fa171c")  # signatureinfo, bytes
]

encoded_data = encode(
    ['uint256', 'uint256', 'uint16[]', 'bytes32', 'bytes'],
    values
)

print(encoded_data.hex())
