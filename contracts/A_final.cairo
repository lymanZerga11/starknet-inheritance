%lang starknet
%builtins pedersen ecdsa

from starkware.starknet.common.syscalls import get_contract_address,get_caller_address
from starkware.cairo.common.uint256 import Uint256,uint256_add,uint256_sub,uint256_le,uint256_lt,uint256_check


struct TestA:
    member a : felt
    member b : felt 
end

struct StructC:
    member a : felt
    member b : felt 
end

@storage_var
func tuple_map{a: felt, b: felt}() -> (res: felt):
end

@storage_var
func some_map(a: felt) -> (res: felt):
end

@storage_var
func map_of_B(key: felt) -> (res: felt):
end

@storage_var
func map_of_C(key: felt) -> (res: felt):
end

const some_constant = 100


@constructor
func constructor{
    syscall_ptr : felt*, 
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
    }():
    (val : felt,) = _private_of_B(2)
    some_map(0, val)
    return ()
end

@external
func external_test_function(boom: felt) -> (value: felt):
    value = boom
    return (value)
end

@view
func view_test_function(number: felt) -> (number_add_1: felt):
    number_add_1 = number + 1
    return (number_add_1)
end

@view
func _view_of_C(n: felt) -> (f: felt):
    f = n * 5
    return f
end

func some_internal_function(number: felt) -> (number_add_1: felt):
    let (val) = test_map.read(1)
    number_add_1 = val + 1
    return (number_add_1)
end

func _private_of_B(n: felt) -> (f: felt):
    f = n * 2
    return f
end

func _private_of_C(n: felt) -> (f: felt):
    f = n * 2
    return f
end
