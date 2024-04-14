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
contract_data = "0x94aeecd50000000000000000000000000000000000000000000000000000000000000440f2918a1de9983239ad0e0f7189de3a86ab559e7d2920e7d723b5a62b83a11dc8c5993a784ff807137d5488a9538825dff7ed987d71ea6fb9eab2c3ac773b589ddf42302e8489216b3571a8c3bc3be5ff1f16e186c7d7671ecd9977328884d1acf0aafa2e7ba71c314bf15457fcd49be7d34159b25b979635c1bbdcc07126400334de87587de784132db6e98411f666ee48187247d76b16f217a925f642d58b18c416450e4ab3a276db6c69e289c06ce75a1ad85991aa261f96f65133ab548f03887c22bd8750d34016ac3c66b5ff102dacdd73f6b014e710b51e8022af9a1968279c9314b2fc0aa6ffd0e67c68f23ef019f6bbc717144a73d2bbcdee2cd764855f22e9ec54a65c928c22773bb80133f52597985ccec2fe75365d81735deab0d6cefad4e508c098b9a7e1d8feb19955fb02ba9675585078710969d3440f5054e0f9dc3e7fe016e050eff260334f18a5d4fe391d82092319f5964f2e2eb7c1c3a5a7f2e2fb216b95bbba6a8ccf6f9e7e24e0875297821d0c2781b6e3f2746e91543490c6ceeb450aecdc82e28293031d10c7d73bf85e57bf041a97360aa2c5d99cc146a3388fa5756f739f9d54779fbc00cd0a68ce2f1b835831c156f7cad99b695c67add7c6caf302256adedf7ab114da0acfe870d449a3a489f781d659e8becc8adc6045adeea7859454951fd3ad9e82b0b31349d287c5911633bce3a686b9612684e2584c73e02c8cdcef8546617e88fe02094db1caae40789920ae53027df3e1d3b5c807b281e4683cc6d6315cf95b9ade8641defcb32372f1c126e398ef7a5a2dce0a8a7f68bb74560f8f71837c2c2ebbcbf7fffb42ae1896f13f7c7479a0b46a28b6f55540f89444f63de0378e3d121be09e06cc9ded1c20e65876d36aa0c65e9645644786b620e2dd2ad648ddfcbf4a7e5b1a3a4ecfe7f64667a3f0b7e2f4418588ed35a2458cffeb39b93d26f18d2ab13bdce6aee58e7b99359ec2dfd95a9c16dc00d6ef18b7933a6f8dc65ccb55667138776f7dea101070dc8796e3774df84f40ae0c8229d0d6069e5c8f39a7c299677a09d367fc7b05e3bc380ee652cdc72595f74c7b1043d0e1ffbab734648c838dfb0527d971b602bc216c9619ef0abf5ac974a1ed57f4050aa510dd9c74f508277b39d7973bb2dfccc5eeb0618db8cd74046ff337f0a7bf2c8e03e10f642c1886798d71806ab1e888d9e5ee87d0838c5655cb21c6cb83313b5a631175dff4963772cce9108188b34ac87c81c41e662ee4dd2dd7b2bc707961b1e646c4047669dcb6584f0d8d770daf5d7e7deb2e388ab20e2573d171a88108e79d820e98f26c0b84aa8b2f4aa4968dbb818ea32293237c50ba75ee485f4c22adf2f741400bdf8d6a9cc7df7ecae576221665d7358448818bb4ae4562849e949e17ac16e0be16688e156b5cf15e098c627c0056a9b67702d5a1f94b6d3dfad29960fdc239963eafd68fd2ba7043d38cd0ebeccf90000100000000000000000000000000000000000000000000000000000001a99d0000000000000000000000004200000000000000000000000000000000000007000000000000000000000000fe26613a717a793560df394928bcc22ed0d8542e000000000000000000000000000000000000000000000000002386f26fc10000000000000000000000000000000000000000000000000000000000000004638800000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000001a4d764ad0b000100000000000000000000000000000000000000000000000000000001a99d0000000000000000000000004200000000000000000000000000000000000010000000000000000000000000cb95f07b1f60868618752ceabbe4e52a1f564336000000000000000000000000000000000000000000000000002386f26fc10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000a41635f5fd0000000000000000000000003c2e676a4d864f94a87986d8d91a487ca2ff1b6f0000000000000000000000003c2e676a4d864f94a87986d8d91a487ca2ff1b6f000000000000000000000000000000000000000000000000002386f26fc10000000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
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
