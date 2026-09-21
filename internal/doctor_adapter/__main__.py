"""Print the scenario index, or one envelope, as JSON on standard output.

``python -m internal.doctor_adapter --index`` lists ``[{"name", "mode"}]``;
``python -m internal.doctor_adapter <scenario>`` prints that scenario's envelope.
No file is written, and nothing listens on a port.
"""

from __future__ import annotations

import sys
from typing import BinaryIO

from .envelope import envelope_bytes
from .scenarios import SCENARIOS, scenario_envelope, scenario_index

INDEX = "--index"


def main(argv: list[str] | None = None, stdout: BinaryIO | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else list(argv)
    if len(arguments) != 1 or (arguments[0] != INDEX and arguments[0] not in SCENARIOS):
        sys.stderr.write(
            f"usage: python -m internal.doctor_adapter {INDEX} | "
            "{" + ",".join(sorted(SCENARIOS)) + "}\n"
        )
        return 2
    stream = sys.stdout.buffer if stdout is None else stdout
    if arguments[0] == INDEX:
        stream.write(envelope_bytes(scenario_index()))
    else:
        stream.write(envelope_bytes(scenario_envelope(arguments[0])))
    stream.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
