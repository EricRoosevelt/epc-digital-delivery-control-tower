# Product validation rules

Rule set `product-validation`, version `1.0`. One rule, `PV-001`.

## What this is, and what it is not

These rules were written to exercise this product's own path: check a model,
fix it at the source, export again, check again. That is the whole of their
authority.

They are **not** a requirement of any project, owner or statute, and not a
buildingSMART requirement. A model that fails `PV-001` has not been shown to be
defective by anyone's requirement but this one, and a check against this rule
set is not an IFC conformance check.

## PV-001

Every `IfcAirTerminal` in scope declares a predefined type that is one of
`DIFFUSER`, `GRILLE`, `LOUVRE`, `REGISTER`.

The four values are from IFC4's `IfcAirTerminalTypeEnum`
([IFC4 ADD2 TC1](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/schema/ifchvacdomain/lexical/ifcairterminaltypeenum.htm)).
That enumeration also admits `USERDEFINED` and `NOTDEFINED`. Leaving them out is
this rule's decision about what counts as an answer; a model using either is
still valid IFC4.

A pass says that the predefined type the checker read is one of the four. It
does not say:

- that the value is the right one for the object — any of the four passes;
- that an opening exists for the terminal, or that two models line up;
- that any work depending on the terminal may start.

### Where the value is read from

Measured with IfcTester 0.8.5 and pinned in
`tests/test_product_validation_ruleset.py`; this is the checker's behaviour, not
something the rule file chooses.

| Type object says | Occurrence says | Value compared |
|---|---|---|
| `DIFFUSER`, `GRILLE`, `LOUVRE` or `REGISTER` | anything | the type's |
| `USERDEFINED`, with an `ElementType` text | anything | that text |
| nothing: no type object, `NOTDEFINED`, or `USERDEFINED` with no text | a value | the occurrence's |
| nothing | `USERDEFINED` | the occurrence's `ObjectType` text |

Two consequences worth knowing before reading a result:

- A value set on the occurrence is ignored when the type object carries one.
  An occurrence declaring `LOUVRE` under a type that is `USERDEFINED` with some
  other text fails.
- `USERDEFINED` is replaced by its free text before the comparison, so a
  user-defined type whose text happens to be spelled `LOUVRE` passes. The rule
  does not accept `USERDEFINED` as a value, but it cannot tell that case apart.

## Why it is not in `rules/epc-delivery`

Because of what that was measured to cost. The validation identity digests the
rule set, so one rule added to the shipped rule set re-keys every canonical
finding and every issue this repository publishes. A rule that exists to
exercise the product does not get to move the shipped project's published
results.

So this rule set has its own identifier and version, the shipped
`control-tower.toml` does not name it, and a run of the shipped configuration
writes the same bytes whether this directory exists or not. The test module
above runs it both ways and compares.

## Using it from a workspace outside the repository

A workspace is a directory with its own `control-tower.toml` and its own
`projects/`. Name this directory as the rule set, by absolute path:

```toml
[run]
ruleset_path = "<checkout>/rules/product-validation"
exporters = ["csv", "json"]
```

Each project in the workspace needs the rule's stage in its programme —
`[[milestones]]` with `stage = "Coordination"`; `due` may be empty.

```bash
python -m epc_control_tower.cli --repository-root <workspace> run
```

Everything the run publishes goes under `<workspace>`; its internal coverage
record goes to the user's state directory, as for any run. `run.json` records the rule
set's identifier, version and normalized digest; compare them with
`docs/contracts/ruleset-product-validation.json` to confirm which rules a
result was produced by.

The one file the run writes in the checkout is `ids/product-validation_v1.0.ids`
— the IDS document the rules compile to, which is committed, and which the run
rewrites with the same bytes.

`bcf` is left out of `exporters` above because that exporter reads the vendored
BCF schemas from `<workspace>/third_party/`; copy them there to enable it.

## Changing a rule

A `(ruleset_id, version)` pair names one set of rules. Edit a rule and the test
refuses until `version` in `ruleset.toml` is raised and the new version is added
to `docs/contracts/ruleset-product-validation.json`, beside the old one. Raise
the major part when the rule set can reject something it used to accept.
