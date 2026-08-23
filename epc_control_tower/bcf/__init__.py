"""BCF machinery: deterministic archives, safe reads, geometry, schema checks.

Kept apart from the exporter that uses it so the determinism and archive-safety
rules stay reviewable on their own, and so a future non-legacy BCF exporter can
reuse them unchanged.
"""
