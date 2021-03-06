cairo_contract_A_dict = {
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
    "external": [
        {
            "name": "external_test_function",
            "inputs": {"implicits": None, "args": [{"name": "boom", "type": " felt"}]},
            "outputs": [{"name": "value", "type": " felt"}],
            "raw_text": "@external\nfunc external_test_function(boom: felt) -> (value: felt):\n    value = boom\n    return (value)\nend",
        }
    ],
    "const": [{"name": "test", "raw_text": "const test = 100\n"}],
    "func": [
        {
            "name": "test_function",
            "inputs": {
                "implicits": None,
                "args": [{"name": "number", "type": " felt"}],
            },
            "outputs": [{"name": "number_add_1", "type": " felt"}],
            "raw_text": "func test_function(number: felt) -> (number_add_1: felt):\n    number_add_1 = number + 1\n    return (number_add_1)\nend",
        }
    ],
}

cairo_contract_inherited = {
    "lang": ["starknet"],
    "builtin": ["pedersen", "hashbuiltIn"],
    "inherits": ["B", "C"],
    "imports": [
        {
            "starkware.starknet.common.syscalls": [
                "get_caller_address",
                "get_contract_address",
            ]
        },
        {"test": ["b", "c", "d"]},
        {"other": ["other_one", "and_one"]},
        {"the_other": ["one_more"]},
        {"wombat": ["battime", "womtime"]},
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
        {
            "name": "store",
            "inputs": {"implicits": None, "args": [{"name": "x", "type": " felt"}]},
            "outputs": [{"name": "y", "type": " felt"}],
            "raw_text": "@storage_var\nfunc store(x: felt) -> (y: felt):\nend",
        },
    ],
    "constructor": {
        "name": "constructor",
        "inputs": None,
        "outputs": None,
        "raw_text": "@constructor\nfunc constructor{}():\n    test_var.write(0)\n    test_map.write(1,2)\n    ret\nend",
    },
    "external": [
        {
            "name": "external_test_function",
            "inputs": {"implicits": None, "args": [{"name": "boom", "type": " felt"}]},
            "outputs": [{"name": "value", "type": " felt"}],
            "raw_text": "@external\nfunc external_test_function(boom: felt) -> (value: felt):\n    value = boom\n    return (value)\nend",
        }
    ],
    "const": [{"name": "test", "raw_text": "const test = 100\n"}],
    "func": [
        {
            "name": "test_function",
            "inputs": {
                "implicits": None,
                "args": [{"name": "number", "type": " felt"}],
            },
            "outputs": [{"name": "number_add_1", "type": " felt"}],
            "raw_text": "func test_function(number: felt) -> (number_add_1: felt):\n    number_add_1 = number + 1\n    return (number_add_1)\nend",
        },
        {
            "name": "_das_private",
            "inputs": {"implicits": None, "args": [{"name": "n", "type": " felt"}]},
            "outputs": [{"name": "f", "type": " felt"}],
            "raw_text": "func _das_private(n: felt) -> (f: felt):\n    f = n * 2\n    return f\nend",
        },
    ],
}
