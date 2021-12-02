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
'''
