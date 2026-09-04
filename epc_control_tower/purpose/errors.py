"""Why a Purpose Pack or a Project Overlay was refused.

Every refusal carries a **code**, and each code names one row of ADR 0002 §3.7
or one of §3.8's eighteen structural invariants. That is deliberate and is the
whole reason this module exists rather than raising bare ``ValueError``: the
mapping from "what the design says must fail closed" to "what the loader
actually refuses" is otherwise an argument in prose, and prose drifts. With a
code per row, the mapping is a test.

There is exactly one failure mode. A Pack or an Overlay is either loaded whole
or refused, and the refusal is an exception — never a warning, never a default
substituted for a missing value, never a partially-composed object with a
"degraded" flag. `AGENTS.md` puts it plainly: a delivery requirement the
pipeline silently declines to evaluate is the worst outcome available.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["PurposeError", "PurposeCompositionError", "PurposePackError"]


class PurposeError(ValueError):
    """A Pack, an Overlay, or their composition was refused.

    ``code`` is stable and is what tests assert against; ``source`` is the file
    the reader was in when it refused, when there is one.
    """

    def __init__(self, code: str, message: str, *, source: Path | None = None) -> None:
        self.code = code
        self.source = source
        location = f"{source}: " if source is not None else ""
        super().__init__(f"[{code}] {location}{message}")


class PurposePackError(PurposeError):
    """A Pack could not be read, or failed a Pack-load structural invariant.

    Raised before any project is considered: a Pack is checked on its own
    terms, so an unsound tree is caught once rather than once per project that
    binds it.
    """


class PurposeCompositionError(PurposeError):
    """A Pack and an Overlay could not be composed for one project.

    Distinct from :class:`PurposePackError` because the blast radius differs.
    A malformed Pack is broken for everyone; a composition defect is broken for
    one project's request, and ADR 0002 §3.7 is careful that it never becomes a
    pipeline failure.
    """
