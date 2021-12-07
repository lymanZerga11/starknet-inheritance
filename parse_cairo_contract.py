"""
Parse a .cairo contract into the following data structure:

{
    inherits: List[str]
    lang: List[str]
    builtins: List[str]
    imports: List[Dict{
        package_name: List[str] <- imports
    }]
    storage_vars: List[Dict{
        name: str
        inputs: List[str]
        outputs: List[str]
        raw_text: str
        file_of_origin: str <- name of file of origin
    }
    constructor: Dict{
        inputs: List[str]
        raw_text: str
    }
    const: List[Dict{
        inputs: List
        raw_text: str
    }]
    external: List[Dict{
        name: str
        inputs: List[str]
        outputs: List[str]
        raw_text: str
        file_of_origin: str <- name of file of origin
    }
    functions: List[Dict{
        name: str
        inputs: List[str]
        outputs: List[str]
        raw_text: str
        file_of_origin: str <- name of file of origin
    }

}
"""

import re
from itertools import tee
from writer import write_artifact
from commons import CONTRACTS_DIRECTORY

def parse_cairo_contract(contract_name):
    contract_path = f"{CONTRACTS_DIRECTORY}/{contract_name}.cairo"
    with open(contract_path) as contract:
        contract_as_string = contract.read()

    # compile important keywords
    # important that func is last
    dict_of_keywords = dict(
        {
            "lang": {
                "compiled": re.compile(r"%lang"),
                "parse_function": "parse_percent_header",
            },
            "builtin": {
                "compiled": re.compile(r"%builtins"),
                "parse_function": "parse_percent_header",
            },
            "inherits": {
                "compiled": re.compile("@inherits"),
                "parse_function": "parse_inherit",
            },
            "imports": {
                "compiled": re.compile("\nfrom"),
                "parse_function": "parse_imports",
            },
            "storage": {
                "compiled": re.compile("@storage_var"),
                "parse_function": "parse_storage",
            },
            "constructor": {
                "compiled": re.compile("@constructor"),
                "parse_function": "parse_constructor",
            },
            "external": {
                "compiled": re.compile("@external"),
                "parse_function": "parse_external",
            },
            "view": {
                "compiled": re.compile("@view"),
                "parse_function": "parse_view",
            },
            "const": {
                "compiled": re.compile("\nconst "),
                "parse_function": "parse_const",
            },
            "func": {
                "compiled": re.compile("\nfunc "),
                "parse_function": "parse_func",
            },
            "structs": {
                "compiled": re.compile("\nstruct "),
                "parse_function": "parse_structs",
            },
        }
    )

    dict_of_matches = create_dict_of_matches(contract_as_string, dict_of_keywords)

    dict_of_contract = create_dict_of_contract(
        contract_as_string, dict_of_keywords, dict_of_matches
    )
    #Allows to distinguish between different artifacts
    dict_of_contract["contract"] = contract_path
    write_artifact(dict_of_contract, contract_name)
    return dict_of_contract

def create_dict_of_matches(contract: str, dict_of_keywords: dict()) -> dict():
    dict_of_matches = dict()

    for keyword in dict_of_keywords.keys():
        dict_of_matches[keyword] = [
            {"start": x.start(), "finish": x.end()}
            for x in dict_of_keywords[keyword]["compiled"].finditer(contract)
        ]

    return dict_of_matches


def create_dict_of_contract(
    contract: str, dict_of_keywords: dict(), dict_of_matches: dict()
) -> dict():
    # final data structure
    dict_of_contract = dict()

    # we call each parse function by name to parse different blocks of the contract
    # all parsing is done from the absolute contract
    for keyword in dict_of_matches.keys():
        dict_of_contract[keyword] = eval(
            f'{dict_of_keywords[keyword]["parse_function"]}'
            + "(dict_of_contract, contract, dict_of_matches[keyword])"
        )

    return dict_of_contract


###################
# PERCENT HEADER PARSING
###################


def parse_percent_header(
    current_dict: dict, contract: str, percent_match: re.Match
) -> list():
    percent_list = list()

    # each time we have a % appearing in the given match object we parse the block ending in \n
    for occurance in percent_match:
        list_of_words, _ = parse_block(occurance, contract, "\n")
        percent_list.extend(list_of_words[1:])

    return percent_list


###################
# INHERITANCE PARSING
###################


def parse_inherit(
    current_dict: dict, contract: str, starting_match: re.Match
) -> list():
    inherit_list = list()

    for occurance in starting_match:
        list_of_words, _ = parse_block(occurance, contract, "end")
        inherit_list.extend(list_of_words[1:-1])
    return inherit_list


###################
# IMPORT STATEMENT PARSING
###################


def parse_imports(
    current_dict: dict, contract: str, starting_match: re.Match
) -> list():
    imports_list = list()

    # check that there are more than one import statement so we can use the start of the next import as the stop for the previous
    if len(starting_match) > 1:
        for (occurance, next_occurance) in pairwise(starting_match):
            i = parse_single_import(occurance, next_occurance, contract)
            imports_list.append(i)

    imports_list.append(parse_last_import(starting_match[-1], contract))

    return imports_list


def parse_single_import(occurance: dict, next_occurance: dict, contract: str) -> dict:
    block = contract[occurance["start"] : next_occurance["start"]]

    # parse the import block
    return import_parse(block)


def parse_last_import(occurance: dict, contract: str) -> dict:
    # determine if next block after last import starts with @ or func or const
    at_symbol = re.compile("@")
    func_symbol = re.compile("\nfunc")
    const_symbol = re.compile("\nconst")

    # cut contract to start at the beginning of the occurance
    slice_to_start = contract[occurance["start"] :]

    # search for position of @ symbol, func, or const
    next_at = at_symbol.search(slice_to_start)
    next_func = func_symbol.search(slice_to_start)
    next_const = const_symbol.search(slice_to_start)

    # create list of start indices, assign negative one if one doesnt exist
    list_of_values = list()
    list_of_values.append(next_at.start() if next_at else -1)
    list_of_values.append(next_func.start() if next_func else -1)
    list_of_values.append(next_const.start() if next_const else -1)

    # drop the -1 values
    new_list = [x for x in list_of_values if x != -1]

    # if there are values left select the minimum
    if new_list:
        ending_index = min(new_list)
    else:
        ending_index = -1

    if ending_index == -1:
        block = slice_to_start
    else:
        # end the slice at the beginning of the next symbol
        block = slice_to_start[:ending_index]

    # parse the import block
    return import_parse(block)


def import_parse(block: str) -> dict:
    word = re.compile("[\S]+")
    list_of_words = word.findall(block)

    # strip extra characters
    clean_list_of_words = [replace_import_chars(word) for word in list_of_words]

    # package name is first word after from
    package_name = clean_list_of_words[1]
    # import names are 3rd word after from and on
    list_of_imports = (
        [x for x in clean_list_of_words[3:]] if len(clean_list_of_words) > 3 else None
    )
    return dict({package_name: list_of_imports})


###################
# STORAGE PARSING
###################


def parse_storage(current_dict: dict, contract: str, storage_match: re.Match) -> list():
    storage_list = list()

    for occurance in storage_match:
        list_of_words, raw_text = parse_block(occurance, contract, "end")
        # name is the third word, also strip extra chars from name
        name = parse_name(list_of_words[2])
        inputs, outputs = parse_inputs_and_outputs(list_of_words)
        # TODO: add file of origin

        dict_of_storage = dict(
            {"name": name, "inputs": inputs, "outputs": outputs, "raw_text": raw_text}
        )
        storage_list.append(dict_of_storage)

    return storage_list


###################
# EXTERNAL PARSING
###################


def parse_external(
    current_dict: dict, contract: str, external_match: re.Match
) -> list():
    external_list = list()

    for occurance in external_match:
        list_of_words, raw_text = parse_block(occurance, contract, "end")
        name = parse_name(list_of_words[2])
        inputs, outputs = parse_inputs_and_outputs(list_of_words)
        # TODO: add file of origin

        dict_of_storage = dict(
            {"name": name, "inputs": inputs, "outputs": outputs, "raw_text": raw_text}
        )
        external_list.append(dict_of_storage)

    return external_list

###################
# VIEW PARSING
###################


def parse_view(
    current_dict: dict, contract: str, view_match: re.Match
) -> list():
    view_list = list()

    for occurance in view_match:
        list_of_words, raw_text = parse_block(occurance, contract, "end")
        name = parse_name(list_of_words[2])
        inputs, outputs = parse_inputs_and_outputs(list_of_words)
        # TODO: add file of origin

        dict_of_storage = dict(
            {"name": name, "inputs": inputs, "outputs": outputs, "raw_text": raw_text}
        )
        view_list.append(dict_of_storage)

    return view_list


###################
# CONSTRUCTOR PARSING
###################


def parse_constructor(
    current_dict: dict, contract: str, constructor_match: re.Match
) -> dict():

    # will only ever be one but will be packaged in a list
    for occurance in constructor_match:
        list_of_words, raw_text = parse_block(occurance, contract, "end")

        # name should always be constructor
        name = parse_name(list_of_words[2])

        # should always have no outputs
        inputs, outputs = parse_inputs_and_outputs(list_of_words)
        # TODO: add file of origin

        constructor_dict = dict(
            {"name": name, "inputs": inputs, "outputs": outputs, "raw_text": raw_text}
        )

    return constructor_dict


###################
# CONST PARSING
###################


def parse_const(current_dict: dict, contract: str, const_match: re.Match) -> list():
    const_list = list()

    for occurance in const_match:
        const_dict = dict()
        list_of_words, raw_text = parse_block(occurance, contract, "\n")
        const_dict["name"] = parse_name(list_of_words[1])
        const_dict["raw_text"] = raw_text
        const_list.append(const_dict)

    return const_list


###################
# FUNC PARSING
###################


def parse_func(current_dict: dict, contract: str, func_match: re.Match) -> list():
    func_list = list()

    for occurance in func_match:
        list_of_words, raw_text = parse_block(occurance, contract, "end")
        name = parse_name(list_of_words[1])
        ext_and_int_funcs = [x.get("name") for x in current_dict["external"]] + [x.get("name") for x in current_dict["view"]]
        if not name in [x.get("name") for x in current_dict["storage"]]:
            if not name in ext_and_int_funcs:
                if not name == "constructor":
                    inputs, outputs = parse_inputs_and_outputs(list_of_words)
                    # TODO: add file of origin

                    dict_of_func = dict(
                        {
                            "name": name,
                            "inputs": inputs,
                            "outputs": outputs,
                            "raw_text": raw_text,
                        }
                    )
                    func_list.append(dict_of_func)

    return func_list


###################
# STRUCT PARSING
###################


def parse_structs(current_dict: dict, contract: str, struct_match: re.Match) -> list():
    struct_list = list()

    for occurance in struct_match:
        list_of_words, raw_text = parse_block(occurance, contract, "end")
        name = list_of_words[1].replace(":","")
        members_to_parse = filter(lambda x: x != ":" and x != "member", list_of_words[2:len(list_of_words)-1])

        members = [] #{name, type}
        for member in [*zip(members_to_parse, members_to_parse)]:
            members.append({"name":member[0], "type":member[1]})

        dict_of_struct = dict(
            {"name":name, "members":members, "raw_text": raw_text}
        )
        struct_list.append(dict_of_struct)

    return struct_list


###################
# GENERAL PARSING UTILS
###################


def parse_block(occurance: dict, contract: str, ending_word: str) -> (list(), str):
    word = re.compile("[\S]+")
    block = get_block(occurance, contract, ending_word)
    return word.findall(block), block


def compile_list_of_strings(list_of_strings: list()) -> list():
    compiled_strings = list()
    for string in list_of_strings:
        compiled_strings.append(re.compile(string))

    return compiled_strings


def parse_name(word: str) -> str:
    word = word.split("{")[0]
    word = word.split("(")[0]
    return word


def parse_inputs_and_outputs(list_of_words: str) -> list:
    list_of_implicits = None
    list_of_args = None
    list_of_outputs = None

    # compile the regex patters we are searching for
    open_bracket = re.compile("{[^\)]+}")
    parenth = re.compile("\(([^\)]+)\)")
    aarow = re.compile("->")

    # join the words around spaced and then find the index of the colon just after the function statement
    # slice the string to just the function statement
    raw_full_string = " ".join(list_of_words)
    index = find_colon_after_func_statement(raw_full_string)
    full_string = raw_full_string[:index]

    ob = open_bracket.search(full_string)
    p = parenth.finditer(full_string)
    a = aarow.search(full_string)

    list_p = list(p)

    # if there are {} then parse implicit arguments
    if ob:
        b_start = ob.start()
        b_end = ob.end()

        bracket_slice = full_string[b_start:b_end]
        list_of_implicits = parse_args(bracket_slice)

    # if list_p is empty then there are no non implicit inputs or outputs
    if not list_p:
        return dict({"implicits": list_of_implicits, "args": list_of_args}), list_of_outputs

    # if there are more than one instance of parentheses we need to initialize lists
    if len(list_p) > 1:
        p_start = list()
        p_finish = list()

        for pr in list_p:
            p_start.append(pr.start())
            p_finish.append(pr.end())
    else:
        p_start = list_p[0].start()
        p_finish = list_p[0].end()

    a_start = a.start()

    # if there are more than on parentheses and the first set starts before the arrows 
    # then parse a list of non implicit arguments and then parse outputs
    #NOTE: could be a problem with nested parentheses of tuples here
    if len(list_p) > 1 and p_start[0] < a_start:
        parenth_slice = full_string[p_start[0] : p_finish[0]]
        list_of_args = parse_args(parenth_slice)

        parenth = re.compile("\(([^\)]+)\)")

        output_parenth_slice = full_string[p_start[1] : p_finish[1]]
        list_of_outputs = parse_args(output_parenth_slice)

    #if only one set of parentheses and they are before the arrow then they are args
    elif p_start < a_start:
        parenth_slice = full_string[p_start:p_finish]
        list_of_args = parse_args(parenth_slice)

    #if only one set of parentheses and they are after the arrow they are outputs
    else:
        parenth_slice = full_string[p_start:p_finish]
        list_of_outputs = parse_args(parenth_slice)

    return dict({"implicits": list_of_implicits, "args": list_of_args}), list_of_outputs

#return block of text to be parsed
def get_block(occurance: dict(), contract: str, ending_str: str) -> str:
    end = re.compile(ending_str)
    string_starting_with_keyword = contract[occurance["start"] :].lstrip("\n")
    match = end.search(string_starting_with_keyword)

    if match:
        return string_starting_with_keyword[: match.end()]
    else:
        return string_starting_with_keyword


def replace_import_chars(word: str) -> str:
    list_of_chars = [",", "{", "}", "(", ")"]

    for char in list_of_chars:
        word = word.replace(char, "").strip(" ")

    return word


def find_colon_after_func_statement(raw_full_string: str) -> int:
    # find poisition of colon after func name() -> ():
    index = 0
    for char in raw_full_string:
        if char == ")" and raw_full_string[index + 1] == ":":
            return index + 1
        index = index + 1

# turn arguments or outputs into data structure List({'name': name, 'type': type})
def parse_args(the_slice: str) -> list:
    new_list = list()

    the_list = the_slice.split(",")
    for implicit_arg in the_list:
        new_arg = replace_import_chars(implicit_arg)

        if ":" in new_arg:
            split_arg = new_arg.split(":")
            new_list.append(dict({"name": split_arg[0], "type": split_arg[1]}))

        else:
            new_list.append(dict({"name": new_arg, "type": None}))

    return new_list

#itertools pairwise recipe used for import statement parsing
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)