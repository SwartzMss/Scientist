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
contract_data = "0x30e0789e000000000000000000000000cab666f5c024bb15f7f1f743e4c28423d2aaf3a20000000000000000000000008942af89ebfd1813bad89deb956ea69f2328dca70000000000000000000000000000000000000000000000000000000000000001"
split_contract_data(contract_data)


from web3 import Web3

func_signature =  'transfer(address,uint256)'
function_id = Web3.keccak(text=func_signature)[:4].hex()
print(function_id)
