# 
#   Muna
#   Copyright © 2025 NatML Inc. All Rights Reserved.
#

from muna import Muna

def test_retrieve_user():
    muna = Muna()
    user = muna.users.retrieve()
    assert user is not None