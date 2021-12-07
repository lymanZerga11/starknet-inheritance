%inherits C
%lang starknet
%builtins pedersen ecdsa

from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.uint256 import (Uint256, uint256_add, uint256_sub, uint256_le, uint256_lt, uint256_check)

@storage_var
func map_of_B(key: felt) -> (res: felt):
end

@constructor
func constructor{
    syscall_ptr : felt*, 
    pedersen_ptr : HashBuiltin*,
    range_check_ptr
    }():
    map_of_B.write(key=0, value=100)
    return ()
end

func _private_of_B(n: felt) -> (f: felt):
    f = n * 2
    return f
end