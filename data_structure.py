big_dict = {
    "lang": ["starknet"],
    "builtin": ["pedersen"],
    "inherits": ["B", "C"],
    "imports": [
        {
            "starkware.starknet.common.syscalls": [
                "get_caller_address",
                "get_contract_address",
            ]
        },
        {"test": ["b"]},
        {"other": ["other_one", "and_one"]},
        {"the_other": ["one_more"]},
    ],
    "storage": [
        {
            "name": "test_var",
            "inputs": {
                "implicits": [
                    {"name": "test", "type": " felt"},
                    {"name": "other_test", "type": " b"},
                    {"name": "das_final", "type": None},
                ],
                "args": None,
            },
            "outputs": [{"name": "res", "type": " felt"}],
            "raw_text": "@storage_var\nfunc test_var{test: felt, other_test: b, das_final}() -> (res: felt):\nend",
        },
        {
            "name": "test_map",
            "inputs": {
                "implicits": None,
                "args": [{"name": "test_input", "type": " felt"}],
            },
            "outputs": [{"name": "res", "type": " felt"}],
            "raw_text": "@storage_var\nfunc test_map(test_input: felt) -> (res: felt):\nend",
        },
    ],
    "constructor": {
        "name": "constructor",
        "inputs": None,
        "outputs": None,
        "raw_text": "@constructor\nfunc constructor{}():\n    test_var.write(0)\n    test_map.write(1,2)\n    ret\nend",
    },
    "const": [{"name": "test", "raw_text": "const test = 100\n"}],
    "func": [
        {
            "name": "felt,",
            "inputs": {
                "implicits": [
                    {"name": "test", "type": " felt"},
                    {"name": "other_test", "type": " b"},
                    {"name": "das_final", "type": None},
                ],
                "args": None,
            },
            "outputs": [{"name": "res", "type": " felt"}],
            "raw_text": "func test_var{test: felt, other_test: b, das_final}() -> (res: felt):\nend",
        },
        {
            "name": "felt)",
            "inputs": {
                "implicits": None,
                "args": [{"name": "test_input", "type": " felt"}],
            },
            "outputs": [{"name": "res", "type": " felt"}],
            "raw_text": "func test_map(test_input: felt) -> (res: felt):\nend",
        },
        {
            "name": "test_var.write",
            "inputs": None,
            "outputs": None,
            "raw_text": "func constructor{}():\n    test_var.write(0)\n    test_map.write(1,2)\n    ret\nend",
        },
        {
            "name": "felt)",
            "inputs": {
                "implicits": None,
                "args": [{"name": "number", "type": " felt"}],
            },
            "outputs": [{"name": "number_add_1", "type": " felt"}],
            "raw_text": "func test_function(number: felt) -> (number_add_1: felt):\n    number_add_1 = number + 1\n    return (number_add_1)\nend",
        },
    ],
}
