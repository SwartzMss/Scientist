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
contract_data = "0x7ff36ab500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000080000000000000000000000000cab666f5c024bb15f7f1f743e4c28423d2aaf3a20000000000000000000000000000000000000000000000000000000065a8c04300000000000000000000000000000000000000000000000000000000000000020000000000000000000000005f0b1a82749cb4e2278ec87f8bf6b618dc71a8bf00000000000000000000000078b3e25e43bbf6d87cf7f3445debd1a35230ce67"
split_contract_data(contract_data)
