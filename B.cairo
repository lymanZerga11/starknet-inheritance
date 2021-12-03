%lang starknet
%builtins pedersen hashbuiltIn

from starkware.starknet.common.syscalls import get_caller_address, get_contract_address
from test import b, c
from other import other_one, and_one
from wombat import battime

@storage_var
func test_map(test_input: felt) -> (res: felt, other_res: felt):
end

@constructor
func constructor{}():
    ret
end

func _das_private(n: felt) -> (f: felt):
    f = n * 2
    return f
end