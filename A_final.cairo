%lang starknet
%builtins pedersen hashbuiltIn

from starkware.starknet.common.syscalls import get_caller_address,get_contract_address
from test import b,c,d
from other import other_one,and_one
from the_other import one_more
from wombat import battime,womtime


@storage_var
func test_var{test: felt, other_test: b, das_final}() -> (res: felt):
end

@storage_var
func test_map(test_input: felt) -> (res: felt):
end

@storage_var
func store(x: felt) -> (y: felt):
end

const test = 100


@constructor
func constructor{
    syscall_ptr : felt*, 
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
    }():
    test_var.write(0)
    test_map.write(1,2)
    return ()
end

@external
func external_test_function(boom: felt) -> (value: felt):
    value = boom
    return (value)
end

func test_function(number: felt) -> (number_add_1: felt):
    number_add_1 = number + 1
    return (number_add_1)
end

func _das_private(n: felt) -> (f: felt):
    f = n * 2
    return f
end
