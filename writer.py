def write(contract_dict : dict, output_name : str) -> None:
    """
    Write the contract to a file.
    """
    contract = []
    #start with lang
    contract.append(f"%lang {contract_dict['lang'][0]}") #starknet lang is always first anyways
    #follow with builtins
    contract.append(f"%builtins {' '.join(contract_dict['builtin'])}\n")
    #follow with imports
    for import_ in contract_dict['imports']:
        module = list(import_.keys())[0] #should only be one key
        contract.append(f"from {module} import {','.join(import_[module])}")
    contract.append("\n") #separate imports from rest of code
    #follow with structs
    for struct in contract_dict['struct']:
        contract.append(f"{struct['raw_text']}\n")
    #follow with storage
    for storage in contract_dict['storage']:
        contract.append(f"{storage['raw_text']}\n")
    #follow with const
    for const in contract_dict['const']:
        contract.append(f"{const['raw_text']}\n")
    #follow with constructor
    contract.append(f"{contract_dict['constructor']['raw_text']}\n")
    #follow with external functions
    for external in contract_dict['external']:
        contract.append(f"{external['raw_text']}\n")
    #follow with view functions
    for external in contract_dict['view']:
        contract.append(f"{external['raw_text']}\n")
    #follow with internal functions
    for internal in contract_dict['func']:
        contract.append(f"{internal['raw_text']}\n")
    #write final file
    with open(output_name, 'w') as f:
        f.writelines("\n".join(contract))