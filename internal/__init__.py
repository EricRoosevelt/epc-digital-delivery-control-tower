"""Internal tooling that is not part of the distributed package.

Nothing under this directory is packaged (``pyproject.toml`` lists its packages
explicitly), nothing in ``epc_control_tower`` imports it, and ``epc-ct`` cannot
reach it. It makes no compatibility promise: a name here can change or vanish in
any commit.
"""
