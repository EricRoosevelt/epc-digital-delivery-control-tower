"""Give the whole suite the same schema loader the pipeline uses.

Several tests reach IfcTester directly rather than through the package — the
conformance tests compare our behaviour against IfcTester's own, so importing
it bare is the point. Without this they would each build ``ids.xsd`` the way
IfcTester does by default, which is over the network; see
``epc_control_tower.ids_schema`` for what that cost and
``test_validation_path_egress.py`` for the measurement.

Importing the module installs the loader. It is the one import here, and it is
not unused.

It also points the coverage record somewhere disposable. ``epc-ct run`` keeps
one per run in the user's state directory, and several tests drive ``run``
through the command line; without this the suite would leave records in the
home directory of whoever ran it. Set in the environment rather than patched,
so the tests that start a subprocess inherit it too.
"""

from __future__ import annotations

import atexit
import os
import shutil
import tempfile
import uuid
from pathlib import Path

from epc_control_tower import ids_schema as _ids_schema  # noqa: F401
from epc_control_tower.coverage import COVERAGE_DIR_VARIABLE

_coverage_root = Path(tempfile.gettempdir()) / f"epc-ct-suite-coverage-{uuid.uuid4().hex}"
_coverage_root.mkdir(mode=0o777)
atexit.register(shutil.rmtree, _coverage_root, True)
os.environ[COVERAGE_DIR_VARIABLE] = str(_coverage_root)
