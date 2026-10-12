"""Create an explicitly synthetic external PASS/long-field browser test input.

Derived for tests only from the existing buildingSMART CC BY 4.0 public sample;
Copyright buildingSMART International Ltd. Source/attribution are recorded in
docs/open_source_adoption.md and THIRD_PARTY_NOTICES.md. The repository sample
is never changed, and this synthetic input is not a delivered project model.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import ifcopenshell


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Scratch .ifc path outside the checkout")
    output = parser.parse_args().output.resolve()
    root = Path(__file__).resolve().parents[1]
    if output.is_relative_to(root):
        parser.error("Synthetic inputs belong outside the checkout, not in source/artifacts")
    model = ifcopenshell.open(root / "data/raw/Building-Hvac.ifc")
    for terminal_type in model.by_type("IfcAirTerminalType"):
        terminal_type.PredefinedType = "DIFFUSER"
    for terminal in model.by_type("IfcAirTerminal"):
        terminal.PredefinedType = "DIFFUSER"
        terminal.Name = (
            "SYNTHETIC layout verification only — long exported object name " * 4
        ).strip()
        terminal.Tag = "SYNTHETIC-TAG-" + "1234567890-" * 12
    output.parent.mkdir(parents=True, exist_ok=True)
    model.write(output)
    print("External derived synthetic test input:", output.name)


if __name__ == "__main__":
    main()
