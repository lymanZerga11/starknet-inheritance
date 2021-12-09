%lang starknet
%builtins pedersen range_check

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func balance(user_id : felt) -> (res : felt):
end

@view
func get_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(user_id : felt) -> (res : felt):
    let (current_balance) = balance.read(user_id=user_id)
    return (res=current_balance)
end

@external
func increase_balance{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(user_id : felt, amount : felt):
    let (current_balance,) = balance.read(user_id)
    balance.write(user_id=user_id, value=current_balance + amount)
    return ()
end
