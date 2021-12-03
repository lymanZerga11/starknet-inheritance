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
    parent_contract_dict = parse_cairo_contract(parent_contract_path)
    cairo_contract_dict = merge_child_and_parent(
        child_data_structure, parent_contract_dict
    )

    if parent_contract_dict["inherits"]:
        for parent in parent_contract_dict["inherits"]:
            cairo_contract_dict = recursive_inheritance(
                cairo_contract_dict, (parent + ".cairo")
            )

    return cairo_contract_dict


def merge_child_and_parent(
    child_data_structure: dict, parent_data_structure: dict
) -> dict:

    if not child_data_structure:
        return parent_data_structure

    merged_data_structure = child_data_structure

    # check if lang is equal
    if not merged_data_structure["lang"] == parent_data_structure["lang"]:
        merged_data_structure["lang"].extend(parent_data_structure["lang"])

    # check if all builtins from parent are in merge
    for builtin in parent_data_structure["builtin"]:
        if builtin and not builtin in merged_data_structure["builtin"]:
            merged_data_structure["builtin"].append(builtin)

    # inherits already handled by recursion
    # check if any imports must be added
    list_of_merged_package_names = [
        list(x.keys())[0] for x in merged_data_structure["imports"]
    ]
    for import_ele in parent_data_structure["imports"]:
        # there will only ever be one key in this dict by definition
        package_name = list(import_ele.keys())[0]
        list_of_imports = import_ele[package_name]

        if not package_name in list_of_merged_package_names:
            merged_data_structure["imports"].append(import_ele)
        else:
            for imports in merged_data_structure["imports"]:
                if imports.get(package_name):
                    for i in list_of_imports:
                        if not i in imports[package_name]:
                            imports[package_name].append(i)

    # check if storage_vars need to be inherited
    # CHILD IMPLEMENTATION WILL OVERRIDE PARENT
    # NOTE: HERE WE COULD ALLOW SUPER KEYWORD TO MERGE
    for storage_var in parent_data_structure["storage"]:
        name = storage_var["name"]
        if not name in [x.get("name") for x in merged_data_structure["storage"]]:
            merged_data_structure["storage"].append(storage_var)

    for func in parent_data_structure["func"]:
        name = func["name"]
        if not name in [x.get("name") for x in merged_data_structure["func"]]:
            merged_data_structure["func"].append(func)

    for const in parent_data_structure["const"]:
        name = const["name"]
        if not name in [x.get("name") for x in merged_data_structure["const"]]:
            merged_data_structure["const"].append(const)

    return merged_data_structure


child = dict()
x = recursive_inheritance(child, "A.cairo")

print(x)
