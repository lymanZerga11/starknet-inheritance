@inherits
B
C
end

%lang starknet
%builtins pedersen

from starkware.starknet.common.syscalls import get_caller_address, get_contract_address
from test import b
from other import other_one, and_one
from the_other import {one_more}

const test = 100

@storage_var
func test_var{test: felt, other_test: b, das_final}() -> (res: felt)
end

@storage_var
func test_map(test_input: felt) -> (res: felt)
end

@constructor
func constructor{}():
    test_var.write(0)
    test_map.write(1,2)
    ret
end

func test_function(number: felt) -> (number_add_1: felt):
    number_add_1 = number + 1
    return (number_add_1)
end