from web3 import Web3
from eth_abi import encode_abi

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
contract_data = "0x75278b5c0000000000000000000000000000000000000000000000000000000065de0a3f000000000000000000000000000000000000000000000000000000000004176800000000000000000000000000000000000000000000000000000000000000a08298f2d1aea281ee4079a7a37806614835dd8ab66b35c98bcca38d93ab4b7d6b00000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000041ff507c6ffdd242b0e9e214d88c8bdea757fc30837f65e0e2be9953cf05b2da575fc1bf277280b711ffd488a185242110c70fb7e2556cf664e452e1f119c30cde1b00000000000000000000000000000000000000000000000000000000000000"
split_contract_data(contract_data)

func_signature =  'transfer(address,uint256)'
function_id = Web3.keccak(text=func_signature)[:4].hex()
print(function_id)


# 定义你的参数和它们的类型
values = [
    1709039259,  # deadline, uint256
    208191,  # voyageId, uint256
    [4],  # destinations, uint16[]
    Web3.to_bytes(hexstr="0x33491cb0455f22734db05b9c1d99b7948901b0f6a5cc5fc5052f65b70d15ad8a"),  # data, bytes32
    Web3.to_bytes(hexstr="0x9dd71c69a94913753a875caa476bea016949c19f75fb7eac84c1ac3d6c43b93c75026e9ab3ca618396794bd25b9d396b3deac13994557ade0026a30e2b5a7c8a1b")  # signatureinfo, bytes
]

encoded_data = encode_abi(
    ['uint256', 'uint256', 'uint16[]', 'bytes32', 'bytes'],
    values
)

print(encoded_data.hex())
