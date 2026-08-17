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
CONTRACT_VERSION = "0.1"
