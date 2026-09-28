"""Give the whole suite the same schema loader the pipeline uses.

Several tests reach IfcTester directly rather than through the package — the
conformance tests compare our behaviour against IfcTester's own, so importing
it bare is the point. Without this they would each build ``ids.xsd`` the way
IfcTester does by default, which is over the network; see
``epc_control_tower.ids_schema`` for what that cost and
``test_validation_path_egress.py`` for the measurement.

Importing the module installs the loader. It is the one import here, and it is
not unused.
"""

from __future__ import annotations

from epc_control_tower import ids_schema as _ids_schema  # noqa: F401
