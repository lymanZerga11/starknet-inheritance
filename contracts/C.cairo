%lang starknet

from test import b, d
from other import other_one, and_one
from wombat import battime, womtime

@storage_var
func store(x: felt) -> (y: felt):
end

@constructor
func constructor{}():
    ret
end
