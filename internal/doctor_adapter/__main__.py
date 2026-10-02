"""Print the scenario index, or one envelope, as JSON on standard output.

``python -m internal.doctor_adapter --index`` lists ``[{"name", "mode"}]``;
``python -m internal.doctor_adapter <scenario>`` prints that scenario's envelope;
``python -m internal.doctor_adapter --workspace <dir> [--prior <dir>]`` prints the
envelope of the finished run in a workspace outside this checkout, compared with
an earlier run when one is named. No file is written, and nothing listens on a
port.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import BinaryIO

from .envelope import envelope_bytes
from .scenarios import SCENARIOS, scenario_envelope, scenario_index
from .workspace import workspace_envelope

INDEX = "--index"
WORKSPACE = "--workspace"
PRIOR = "--prior"


def _workspace_arguments(arguments: list[str]) -> tuple[str, str | None] | None:
    """``(workspace, prior)`` if that is what was asked for, exactly; else ``None``."""

    if len(arguments) == 2 and arguments[0] == WORKSPACE:
        return arguments[1], None
    if len(arguments) == 4 and arguments[0] == WORKSPACE and arguments[2] == PRIOR:
        return arguments[1], arguments[3]
    return None


def main(argv: list[str] | None = None, stdout: BinaryIO | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else list(argv)
    stream = sys.stdout.buffer if stdout is None else stdout
    named = _workspace_arguments(arguments)
    if named is not None:
        workspace, prior = named
        envelope = workspace_envelope(Path(workspace), Path(prior) if prior else None)
        stream.write(envelope_bytes(envelope))
        stream.flush()
        return 0
    if len(arguments) != 1 or (arguments[0] != INDEX and arguments[0] not in SCENARIOS):
        sys.stderr.write(
            f"usage: python -m internal.doctor_adapter {INDEX} | "
            "{" + ",".join(sorted(SCENARIOS)) + "} | "
            f"{WORKSPACE} <dir> [{PRIOR} <dir>]\n"
        )
        return 2
    if arguments[0] == INDEX:
        stream.write(envelope_bytes(scenario_index()))
    else:
        stream.write(envelope_bytes(scenario_envelope(arguments[0])))
    stream.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
