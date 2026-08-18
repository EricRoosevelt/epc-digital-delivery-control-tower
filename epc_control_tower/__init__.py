"""EPC Digital Delivery Control Tower.

Turns IFC model data and project-authored information requirements into
traceable digital-delivery findings.

The package is organised around one pivot type: :class:`~.domain.Finding`.
Everything upstream of it produces findings; everything downstream consumes
them. Checkers plug in above, exporters plug in below, and neither needs to
know about the other.
"""

__all__ = ["CONTRACT_VERSION", "__version__"]

__version__ = "1.0.0"

# Version of the published data contract (CSV/JSON column shapes and their
# semantics). Bumping this is a deliberate, reviewable act: it requires a
# CHANGELOG entry and an explicit characterization-snapshot refresh.
#
# 1.2 is the first bump caused by the rule library being used rather than built.
# Four rules were added — no package code, no test, four TOML files — and with
# them the last three IDS facet kinds this project had never evaluated. Every
# canonical table grew rows; the legacy contract did not move, for the same
# reason it has not moved since 1.0.
#
# 1.1 moves the canonical contract again: the rules are declarative now, so the
# rule set has a new id and version and the validation identity follows. The
# legacy contract is unaffected, because it is scoped to the frozen rule set.
#
# 1.0 is the first bump, and the mechanism's first real use. What moved is the
# canonical contract: it now carries more than one project, so the validation
# identity covers six models rather than three and every canonical table grew
# rows. The legacy contract did not move at all — the eight published CSV files
# and the BCF archive are byte-identical, because the legacy writers publish
# one named project.
CONTRACT_VERSION = "1.2"
