# 
#   Function
#   Copyright © 2024 NatML Inc. All Rights Reserved.
#

from fxn import Function

def test_retrieve_user ():
    fxn = Function()
    user = fxn.users.retrieve()
    assert user is not None