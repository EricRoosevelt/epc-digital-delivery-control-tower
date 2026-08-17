"""Pipeline stages.

Each stage is a pure function over domain types with a thin IO shell around it.
They are separate modules rather than one script per step because the previous
layout coupled steps through files on disk: a script wrote a CSV, the next
script read it back, and the only record of the ordering was a list of commands
in the README. Two of those scripts also ran their work at import time, so
importing one to reuse a helper executed the whole thing.
"""
