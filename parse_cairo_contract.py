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
        print(contract_as_string)

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

        print(dict_of_contract)


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


def parse_percent_header(contract: str, percent_match: re.Match) -> list():
    percent_list = list()

    for occurance in percent_match:
        list_of_words = parse_block(occurance, contract, "\n")
        percent_list.extend(list_of_words[1:])

    return percent_list


def parse_inherit(contract: str, starting_match: re.Match) -> list():
    inherit_list = list()

    for occurance in starting_match:
        list_of_words = parse_block(occurance, contract, "end")
        inherit_list.extend(list_of_words[1:-1])

    return inherit_list


def parse_imports(contract: str, starting_match: re.Match) -> list():
    imports_list = list()

    print(starting_match)
    print(next(pairwise(starting_match)))

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


def parse_block(occurance: dict, contract: str, ending_word: str) -> list():
    word = re.compile("[\S]+")
    block = get_block(occurance, contract, ending_word)
    print(block)
    return word.findall(block)


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
        word.replace(char, "")

    return word


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


parse_cairo_contract("A.cairo")
