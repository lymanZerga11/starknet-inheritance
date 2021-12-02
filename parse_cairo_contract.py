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
                    "parse_function": "parse_ending_block",
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


def parse_block(occurance: str, contract: str, ending_word: str) -> list():
    word = re.compile("[\S]+")
    block = get_block(occurance, contract, "end")
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
    return string_starting_with_keyword[: match.end()]


parse_cairo_contract("A.cairo")
