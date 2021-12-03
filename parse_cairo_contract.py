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


def parse_cairo_contract(contract_path):
    with open(contract_path) as contract:
        contract_as_string = contract.read()

        # compile important keywords
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
                "const": {
                    "compiled": re.compile("\nconst "),
                    "parse_function": "parse_const",
                },
                "func": {
                    "compiled": re.compile("\nfunc "),
                    "parse_function": "parse_func",
                },
            }
        )

        dict_of_matches = create_dict_of_matches(contract_as_string, dict_of_keywords)

        dict_of_contract = create_dict_of_contract(
            contract_as_string, dict_of_keywords, dict_of_matches
        )

        # print(dict_of_contract)


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

    for keyword in dict_of_matches.keys():
        dict_of_contract[keyword] = eval(
            f'{dict_of_keywords[keyword]["parse_function"]}'
            + "(contract, dict_of_matches[keyword])"
        )

        print(dict_of_contract)

    return dict_of_contract


###################
# PERCENT HEADER PARSING
###################


def parse_percent_header(contract: str, percent_match: re.Match) -> list():
    percent_list = list()

    for occurance in percent_match:
        list_of_words, _ = parse_block(occurance, contract, "\n")
        percent_list.extend(list_of_words[1:])

    return percent_list


###################
# INHERITANCE PARSING
###################


def parse_inherit(contract: str, starting_match: re.Match) -> list():
    inherit_list = list()

    for occurance in starting_match:
        list_of_words, _ = parse_block(occurance, contract, "end")
        inherit_list.extend(list_of_words[1:-1])

    return inherit_list


###################
# IMPORT STATEMENT PARSING
###################


def parse_imports(contract: str, starting_match: re.Match) -> list():
    imports_list = list()

    if len(starting_match) > 1:
        for (occurance, next_occurance) in pairwise(starting_match):
            i = parse_single_import(occurance, next_occurance, contract)
            imports_list.append(i)

    imports_list.append(parse_last_import(starting_match[-1], contract))

    return imports_list


def parse_single_import(occurance: dict, next_occurance: dict, contract: str) -> dict:
    block = contract[occurance["start"] : next_occurance["start"]]
    return import_parse(block)


def parse_last_import(occurance: dict, contract: str) -> dict:
    # determine if next block after last import starts with @ or func
    at_symbol = re.compile("@")
    func_symbol = re.compile("\nfunc")
    const_symbol = re.compile("\nconst")

    slice_to_start = contract[occurance["start"] :]

    next_at = at_symbol.search(slice_to_start)
    next_func = func_symbol.search(slice_to_start)
    next_const = const_symbol.search(slice_to_start)

    if not next_at:
        next_at = -1
    if not next_func:
        next_func = -1
    if not next_const:
        next_const = -1

    ending_index = min(next_at.start(), next_func.start(), next_const.start())

    if ending_index == -1:
        block = slice_to_start
    else:
        block = slice_to_start[:ending_index]

    return import_parse(block)


def import_parse(block: str) -> dict:
    word = re.compile("[\S]+")
    list_of_words = word.findall(block)

    clean_list_of_words = [replace_import_chars(word) for word in list_of_words]

    package_name = clean_list_of_words[1]
    list_of_imports = (
        [x for x in clean_list_of_words[3:]] if len(clean_list_of_words) > 3 else None
    )
    return dict({package_name: list_of_imports})


###################
# STORAGE PARSING
###################
"""
storage_vars: List[Dict{
        name: str
        inputs: List[str]
        outputs: List[str]
        raw_text: str
        file_of_origin: str <- name of file of origin
    }
    """


def parse_storage(contract: str, storage_match: re.Match) -> list():
    storage_list = list()

    for occurance in storage_match:
        list_of_words, raw_text = parse_block(occurance, contract, "end")
        name = parse_name(list_of_words[2])
        inputs, outputs = parse_inputs_and_outputs(list_of_words)

        dict_of_storage = dict(
            {"name": name, "inputs": inputs, "outputs": outputs, "raw_text": raw_text}
        )
        storage_list.append(dict_of_storage)

    return storage_list


def parse_name(word: str) -> str:
    word = word.split("{")[0]
    word = word.split("(")[0]
    return word


def parse_inputs_and_outputs(list_of_words: str) -> list:
    list_of_inputs = list()

    open_bracket = re.compile("{[^\)]+}")
    parenth = re.compile("\(([^\)]+)\)")
    aarow = re.compile("->")

    full_string = " ".join(list_of_words)

    ob = open_bracket.search(full_string)
    p = parenth.finditer(full_string)
    a = aarow.search(full_string)

    list_p = list(p)

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

    list_of_implicits = None
    list_of_args = None
    list_of_outputs = None

    if ob:
        b_start = ob.start()
        b_end = ob.end()

        bracket_slice = full_string[b_start:b_end]
        list_of_implicits = parse_args(bracket_slice)

    if len(list_p) > 1:
        parenth_slice = full_string[p_start[0] : p_finish[0]]
        list_of_args = parse_args(parenth_slice)

        parenth = re.compile("\(([^\)]+)\)")

        output_parenth_slice = full_string[p_start[1] : p_finish[1]]
        list_of_outputs = parse_args(output_parenth_slice)

    elif p_start < a_start:
        parenth_slice = full_string[p_start:p_finish]
        list_of_args = parse_args(parenth_slice)

    else:
        parenth_slice = full_string[p_start:p_finish]
        list_of_outputs = parse_args(parenth_slice)

    return dict({"implicits": list_of_implicits, "args": list_of_args}), list_of_outputs


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


def get_block(occurance: dict(), contract: str, ending_str: str) -> str:
    end = re.compile(ending_str)
    string_starting_with_keyword = contract[occurance["start"] :]
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


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


parse_cairo_contract("A.cairo")
