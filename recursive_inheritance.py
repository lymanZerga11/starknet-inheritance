"""
Read in main.cairo

data_structure

def recursively_inherit(child_data_structure, main_contract):
    
    if parse_cairo_contract(main_contract):
        for file in parse_cairo_contract(main_contract)[inherits]:
            try:
                parent_contract = search surrounding directory for files to inherit
                parent_data = recursively_inherit(child_data_structure, parent_contract)
                

            except:
                file not found for inheritance

    else:
        new_data_structure = combine_parsed_child_and_parent(child_data_structure, parse_cairo_contract(main_contract))
        return new_data_structure

def combine_parsed_child_and_parent(parsed_data_of_child, parsed_data_of_parent):
    logic to check for functions/other that are redefined in main and not to be inherited
    logic to merge constructors
    data_structure.merge(new_data)
    return data_structure
"""

from parse_cairo_contract import parse_cairo_contract


def recursive_inheritance(child_data_structure: dict, parent_contract_path: str):
    cairo_contract_dict = parse_cairo_contract(parent_contract_path)
    cairo_contract_dict = merge_child_and_parent(
        child_data_structure, cairo_contract_dict
    )

    if cairo_contract_dict["inherits"]:
        for parent in cairo_contract_dict["inherits"]:
            cairo_contract_dict = recursive_inheritance(
                cairo_contract_dict, (parent + ".cairo")
            )

    return cairo_contract_dict


child = dict()
_ = recursive_inheritance(child, "A.cairo")
