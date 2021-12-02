"""
Parse a .cairo contract into the following data structure:

{
    inherits: List[str]
    lang: str
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
                "lang": re.compile(r"%lang"),
                "builtin": re.compile(r"%builtins"),
                "inherits": re.compile("@inherits"),
                "storage": re.compile("@storage_var"),
                "constructor": re.compile("@constructor"),
                "const": re.compile("\nconst "),
                "func": re.compile("\nfunc "),
                "end": re.compile("end"),
            }
        )

        dict_of_matches = dict()

        for keyword in dict_of_keywords.keys():
            dict_of_matches[keyword] = [
                {"start": x.start(), "finish": x.end()}
                for x in dict_of_keywords[keyword].finditer(contract_as_string)
            ]

        print(dict_of_matches)


parse_cairo_contract("A.cairo")
