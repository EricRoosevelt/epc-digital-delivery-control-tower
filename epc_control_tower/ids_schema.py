"""Load IfcTester's IDS schema from disk, and only from disk.

IfcTester validates and decodes every IDS document against the ``ids.xsd`` it
installs beside itself, built once by ``ifctester.ids.get_schema``. That file
imports three W3C schemas by URL:

``http://www.w3.org/2001/xml.xsd``, ``http://www.w3.org/2001/XMLSchema.xsd``
and ``http://www.w3.org/2001/XMLSchema-instance``.

``xmlschema`` resolves an ``xs:import`` by its ``schemaLocation`` first, so
building that schema reached out three times — on every ``epc-ct check``, every
``epc-ct run``, and every test that parses a rule document. The correct schema
was still produced, but only afterwards: when the fetch *failed*, ``xmlschema``
fell back to ``xmlschema.locations.FALLBACK_LOCATIONS``, which points those
three namespaces at copies it ships. So the published bytes were right by way
of an error path, and the path had a second outcome — a reachable server whose
response is truncated raises ``http.client.IncompleteRead``, which is not a
failed fetch and does not trigger any fallback. It just kills the run.

The fix is to reach the copies ``xmlschema`` already installs without asking
the network first. ``allow="local"`` makes ``xmlschema`` refuse a remote
``schemaLocation`` before opening it, so the fallback becomes the only path
rather than the error path, and the resulting schema is the same one: the same
four namespaces, resolved to the same four files.

Nothing is vendored. The three W3C schemas are already on disk as part of
``xmlschema``; this module only changes which of ``xmlschema``'s own
resolutions is tried first, so ``AGENTS.md`` rule 3 has nothing to gate.

``ifctester.ids.get_schema`` memoises in a module global. Replacing it here
keeps that laziness — the schema is still built on first use, not on import —
and covers every entry point that reaches it (``ids.open``, ``ids.from_string``
and ``Ids.to_string``) rather than a list of call sites that a later one could
be forgotten from. ``tests/test_validation_path_egress.py`` measures the
result: zero attempted connections, not connections that were harmlessly
blocked.
"""

from __future__ import annotations

import os

__all__ = ["ensure_local_schema_resolution", "local_schema"]

#: ``xmlschema``'s security mode for schema location hints. ``"local"`` allows
#: any file on disk and refuses every other scheme without opening it, which is
#: what makes the W3C imports resolve from the installed copies instead of the
#: web. ``"sandbox"`` would be too narrow: the copies live under ``xmlschema``,
#: not under ``ids.xsd``'s own directory.
_ALLOW = "local"

_schema = None


def local_schema():
    """Build IfcTester's IDS schema from local files, once."""

    global _schema
    if _schema is None:
        from ifctester import ids
        from xmlschema import XMLSchema

        _schema = XMLSchema(os.path.join(ids.cwd, "ids.xsd"), allow=_ALLOW)
    return _schema


def ensure_local_schema_resolution() -> None:
    """Make IfcTester's schema loader resolve locally. Idempotent.

    Fails loudly rather than silently doing nothing: if a future IfcTester
    stops exposing the loader this replaces, the import path this module exists
    to close has moved, and that has to be seen rather than guessed at.
    """

    from ifctester import ids

    missing = [
        name
        for name in ("get_schema", "schema", "cwd")
        if not hasattr(ids, name)
    ]
    if missing or not callable(ids.get_schema):
        raise RuntimeError(
            "ifctester.ids no longer loads the IDS schema the way this module "
            f"expects (missing or not callable: {missing or ['get_schema']}); "
            "the import path this exists to close has moved, and whether "
            "loading the schema reaches the network is no longer controlled here"
        )
    if getattr(ids.get_schema, "_resolves_locally", False):
        return

    def get_schema():
        # Keep IfcTester's own memo in step: anything reading ``ids.schema``
        # directly must see the same object this returns.
        if ids.schema is None:
            ids.schema = local_schema()
        return ids.schema

    get_schema._resolves_locally = True
    ids.get_schema = get_schema


#: Importing this module is what installs the loader, so a module that reaches
#: IfcTester only has to import it rather than remember to call anything.
ensure_local_schema_resolution()
