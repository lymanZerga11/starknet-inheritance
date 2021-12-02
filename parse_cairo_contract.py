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

        # final data structure
        dict_of_contract = dict()

        # compile important keywords
        dict_of_keywords = dict(
            {
                "lang": {
                    "compiled": re.compile(r"%lang"),
                    "parse_function": "parse_lang",
                },
                "builtin": {
                    "compiled": re.compile(r"%builtins"),
                    "parse_function": "parse_builtin",
                },
                "inherits": {
                    "compiled": re.compile("@inherits"),
                    "parse_function": "parse_inherit",
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
                "end": {"compiled": re.compile("end"), "parse_function": "parse_end"},
            }
        )

        dict_of_matches = dict()

        for keyword in dict_of_keywords.keys():
            dict_of_matches[keyword] = [
                {"start": x.start(), "finish": x.end()}
                for x in dict_of_keywords[keyword]["compiled"].finditer(
                    contract_as_string
                )
            ]

        for keyword in dict_of_matches.keys():
            dict_of_contract[keyword] = eval(
                f'{dict_of_keywords[keyword]["parse_function"]}'
                + '(contract_as_string, dict_of_matches["lang"])'
            )

            print(dict_of_contract)


def parse_lang(contract: str, lang_match: re.Match):
    lang_list = list()

    newline = re.compile("\n")

    for occurance in lang_match:
        string_starting_with_lang = contract[occurance["start"] :]
        match = newline.search(string_starting_with_lang)

        lang_block = string_starting_with_lang[: match.start()]

        lang_types = list(["starknet"])
        compiled_langs = compile_list_of_strings(lang_types)

        for lang in compiled_langs:
            if lang.search(lang_block):
                lang_list.append(lang.pattern)

    return lang_list


def compile_list_of_strings(list_of_strings: list()) -> list():
    compiled_strings = list()
    for string in list_of_strings:
        compiled_strings.append(re.compile(string))

    return compiled_strings


parse_cairo_contract("A.cairo")
