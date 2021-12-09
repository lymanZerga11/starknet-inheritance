%inherits B
%lang starknet
%builtins pedersen range_check

from starkware.starknet.common.syscalls import get_contract_address

const some_constant = 100

struct TestA:
    member a : felt
    member b : felt 
end

@storage_var
func tuple_map{a: felt, b: felt}() -> (res: felt):
end

@storage_var
func some_map(a: felt) -> (res: felt):
end

@constructor
func constructor{
    syscall_ptr : felt*, 
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
    }():
    (val : felt,) = _private_of_B(2)
    some_map.write(0, val)
    return ()
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

func some_internal_function{
    syscall_ptr : felt*, 
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
    }(number: felt) -> (number_add_1: felt):
    let (val) = test_map.read(1)
    let number_add_1 = val + 1
    return (number_add_1)
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