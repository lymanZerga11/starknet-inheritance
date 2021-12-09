%lang starknet
%builtins pedersen range_check ecdsa

from starkware.starknet.common.syscalls import get_contract_address,get_caller_address
from starkware.cairo.common.uint256 import Uint256,uint256_add,uint256_sub,uint256_le,uint256_lt,uint256_check
from starkware.cairo.common.cairo_builtins import HashBuiltin


struct TestA:
    member a : felt
    member b : felt 
end

@storage_var
func tuple_map(a: felt, b: felt) -> (res: felt):
end

@storage_var
func some_map(a: felt) -> (res: felt):
end

@storage_var
func map_of_B(key: felt) -> (res: felt):
end

@storage_var
func balance(user_id : felt) -> (res : felt):
end

const some_constant = 100


@constructor
func constructor{
    syscall_ptr : felt*, 
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
    }():
    let (val,) = _private_of_B(2)
    some_map.write(0, val)
    return ()
end

@external
func external_test_function{
    syscall_ptr : felt*, 
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
    }(boom: felt) -> (value: felt):
    let value = boom
    return (value)
end

@view
func view_test_function{
    syscall_ptr : felt*, 
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
    }(number: felt) -> (number_add_1: felt):
    let number_add_1 = number + 1
    return (number_add_1)
end

@view
func get_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(user_id : felt) -> (res : felt):
    let (current_balance) = balance.read(user_id=user_id)
    return (res=current_balance)
end

func some_internal_function{
    syscall_ptr : felt*, 
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
    }(number: felt) -> (number_add_1: felt):
    let (val) = some_map.read(1)
    let number_add_1 = val + 1
    return (number_add_1)
end

func _private_of_B{
    syscall_ptr : felt*, 
    pedersen_ptr : HashBuiltin*,
    range_check_ptr}(n: felt) -> (f: felt):
    let f = n * 2
    return (f)
end
