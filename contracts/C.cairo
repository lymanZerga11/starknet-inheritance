%lang starknet
%builtins pedersen ecdsa

from starkware.starknet.common.syscalls import get_caller_address

struct StructC:
    member a : felt
    member b : felt 
end

@storage_var
func map_of_C(key: felt) -> (res: felt):
end

@constructor
func constructor{
    syscall_ptr : felt*, 
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
    }():
    map_of_C.write(key=0, value=200)
    return ()
end

@view
func _view_of_C(n: felt) -> (f: felt):
    f = n * 5
    return f
end

func _private_of_C(n: felt) -> (f: felt):
    f = n * 2
    return f
end