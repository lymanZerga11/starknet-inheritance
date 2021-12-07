from recursive_inheritance import recursive_inheritance
from writer import write_contract

from commons import CONTRACTS_DIRECTORY

def main():
    child = dict()
    contract_data = recursive_inheritance(child, "A")
    write_contract(contract_data, "A_final")


if __name__ == "__main__":
    main()