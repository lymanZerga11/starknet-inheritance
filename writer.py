from json import dump
from commons import CONTRACTS_DIRECTORY, ARTIFACTS_DIRECTORY
from pathlib import Path

def write_artifact(contract_dict : dict, contract_name : str):
    Path(f"{ARTIFACTS_DIRECTORY}").mkdir(parents=True, exist_ok=True)
    with open(f"{ARTIFACTS_DIRECTORY}/{contract_name}.json", 'w') as file:
        dump(contract_dict, file)

def write_contract(contract_dict : dict, contract_name : str) -> None:
    """
    Write the final contract to a file.
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
    for struct in contract_dict['structs']:
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
    with open(f"{CONTRACTS_DIRECTORY}/{contract_name}.cairo", 'w') as f:
        f.writelines("\n".join(contract))
