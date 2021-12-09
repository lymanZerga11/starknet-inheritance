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
from typing import Tuple
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
                "compiled": re.compile(r"%inherits"),
                "parse_function": "parse_percent_header",
            },
            "imports": {
                "compiled": re.compile(r"(?<=from)(.*)(?=\n)"),
                "parse_function": "parse_imports",
            },
            "storage": {
                "compiled": re.compile("@storage_var"),
                "parse_function": "parse_at_decorator",
            },
            "constructor": {
                "compiled": re.compile("@constructor"),
                "parse_function": "parse_constructor",
            },
            "external": {
                "compiled": re.compile("@external"),
                "parse_function": "parse_at_decorator",
            },
            "view": {
                "compiled": re.compile("@view"),
                "parse_function": "parse_at_decorator",
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
                "compiled": re.compile(r"(?=\bstruct\b)(.|\n)+?(?<=end)"),
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
def parse_percent_header(current_dict: dict, contract: str, percent_match: re.Match) -> list:
    percent_list = list()

    # each time we have a % appearing in the given match object we parse the block ending in \n
    for occurance in percent_match:
        list_of_words, _ = parse_block(occurance, contract, "\n")
        percent_list.extend(list_of_words[1:])

    return percent_list


###################
# INHERITANCE PARSING
###################
def parse_inherit(current_dict: dict, contract: str, starting_match: re.Match) -> list:
    inherit_list = list()

    for occurance in starting_match:
        list_of_words, _ = parse_block(occurance, contract, "end")
        inherit_list.extend(list_of_words[1:-1])
    return inherit_list


###################
# IMPORT STATEMENT PARSING
###################
def parse_imports(current_dict: dict, contract: str, starting_match: re.Match) -> list:
    imports_list = list()

    for occurance in starting_match:
        list_words, _ = parse_block(occurance, contract, "\n")
        #first "word" is the module
        dict_of_module = {list_words[0]: [repl_imp_chars(imp) for imp in list_words[2:]]}
        imports_list.append(dict_of_module)

    return imports_list


###################
# STORAGE+EXTERNAL+VIEW PARSING
###################
def parse_at_decorator(current_dict: dict, contract: str, match: re.Match) -> list:
    """
    Parses the pieces of code with the "@" decorator prefix
    """
    lst = list()
    for occurance in match:
        list_of_words, raw_text = parse_block(occurance, contract, "end")
        # name is the third word, also strip extra chars from name
        name = parse_name(list_of_words[2])
        implicits = get_implicits(raw_text)
        args = get_args(raw_text)
        outputs = get_outputs(raw_text)
        # TODO: add file of origin
        data_dict = dict(
            {"name": name, "inputs": {"implicits":implicits, "args":args}, "outputs": outputs, "raw_text": raw_text}
        )
        lst.append(data_dict)

    return lst


###################
# CONSTRUCTOR PARSING
###################
def parse_constructor(current_dict: dict, contract: str, constructor_match: re.Match) -> dict():
    # will only ever be one but will be packaged in a list
    for occurance in constructor_match:
        list_of_words, raw_text = parse_block(occurance, contract, "end")
        # name should always be constructor
        name = parse_name(list_of_words[2])
        # should always have no outputs
        inputs, outputs = parse_inputs_and_outputs(list_of_words)
        # TODO: add file of origin
        return {"name": name, "inputs": inputs, "outputs": outputs, "raw_text": raw_text}

    return None


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


def parse_block(occurance: dict, contract: str, ending_word: str) -> Tuple[list, str]:
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

def get_implicits(raw_text : str) -> list:
    """
    Retrieve the implicits of a function.
    """
    reg = re.compile("(?<={)(.|\n)*?(?=})")
    implicits = []
    try:
        x = next(reg.finditer(raw_text))
        raw_implicits = raw_text[x.start():x.end()].split(",")
        cleaned_implicits = list(map(lambda x : x.replace("\n", "").replace(" ", ""), raw_implicits))
        for implicit in cleaned_implicits:
            name, type = implicit.split(":") if len(implicit.split(":")) > 1 else [implicit, None]
            implicits.append({"name":name, "type":type})
    except StopIteration:
        pass
    return implicits

def get_args(raw_text : str) -> list:
    """
    Retrieve the arguments of a function.
    """
    reg = re.compile("(?<=}\()(.|\n)*?(?=\):|\)\s-)")
    args = []
    try:
        x = next(reg.finditer(raw_text))
        raw_args = raw_text[x.start():x.end()].split(",")
        cleaned_args = list(map(lambda x : x.replace("\n", "").replace(" ", ""), raw_args))
        for arg in cleaned_args:
            name, type = arg.split(":") if len(arg.split(":")) > 1 else [arg, None]
            args.append({"name":name, "type":type})
    except StopIteration:
        pass
    return args

def get_outputs(raw_text : str) -> list:
    """
    Retrieves the outputs of a function.
    """
    reg = re.compile("(?<=}\()(.|\n)*?(?=\):)")
    outputs = []
    try:
        x = next(reg.finditer(raw_text))
        raw_outputs = raw_text[x.start():x.end()].split("->")
        if len(raw_outputs) == 1: # no outputs
            return outputs
        raw_outputs = raw_outputs[1].replace("(", "")
        cleaned_outputs = list(map(lambda x : x.replace("\n", "").replace(" ", ""), raw_outputs))
        for output in cleaned_outputs:
            name, type = output.split(":") if len(output.split(":")) > 1 else [output, None]
            outputs.append({"name":name, "type":type})
    except StopIteration:
        pass
    return outputs

#return block of text to be parsed
def get_block(occurance: dict(), contract: str, ending_str: str) -> str:
    end = re.compile(ending_str)
    string_starting_with_keyword = contract[occurance["start"] :].lstrip("\n")
    match = end.search(string_starting_with_keyword)

    if match:
        return string_starting_with_keyword[: match.end()]
    else:
        return string_starting_with_keyword


def repl_imp_chars(word: str) -> str:
    to_remove = (",", "{", "}", "(", ")")
    return word.translate({ord(ch):'' for ch in to_remove})


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
        new_arg = repl_imp_chars(implicit_arg)

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