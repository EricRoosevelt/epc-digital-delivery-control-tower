# Evidence — project applicability and run isolation (2026-09-28)

Supporting evidence for
[ADR 0004](../../decisions/0004-project-applicability-and-run-isolation.md).
Everything below is reproducible from files tracked at `a438f5d`; nothing here
reads or names a private model.

## What this is, and what it is not

- **Measurement, not implementation.** Three of the scripts (`apply_B.py`,
  `apply_R.py`, `apply_D.py`) patch a *disposable checkout* by exact string
  replacement so that an option can be run instead of argued. They are
  prototypes of the options ADR 0004 compares. None of them is proposed as the
  implementation, none is committed as code, and the checkout is restored with
  `git checkout -- . && git clean -fd` between scenarios.
- **The counterexample project is synthetic.** `make_n.py` assembles
  `probe-applicability` from tracked buildingSMART samples only: a *merged MEP*
  model (the PCERT HVAC file plus the ISO basin's `IfcSanitaryTerminal`, placed
  in the HVAC file's storey, declared `discipline = "MEP"`), the ISO wall file
  declared `discipline = "Facade"` (a value no rule's `discipline_scope` uses),
  and the PCERT structural file declared `"Structural"`. Its bytes are
  deterministic (`mep-combined.ifc` =
  `e24c1b0f69d188312c8b860d047fb6772bee7f877af77cab6f862a98d67f73c3` on every
  run). `N1` is the facade model alone.
- **Adoption decisions in these files are nobody's decisions.** Every
  `not-adopted` reason reads "Counterexample only".
- `apply_D.py` adds a throwaway rule `R-P01` (Plumbing) so that a merged model
  has a rule from each of two disciplines to lose. It is never committed.

## Reproduce

```bash
git worktree add --detach <throwaway> a438f5d
CT=<throwaway> PY=<repo>/.venv/Scripts/python.exe M=<dir with the files below> bash run_all.sh
git worktree remove --force <throwaway>
```

`run_all.sh` starts from a pristine checkout, runs every scenario, restores the
checkout, and ends by printing `dirty/untracked: 0`. `cygpath` is used once
(F6), so it expects Git Bash on Windows; elsewhere replace it with the path.

## Scenario index

| Id | Question | Transcript section |
|---|---|---|
| S0 | Does a plain run reproduce the published bytes? | `### S0` |
| DIAG | Current state, from the published CSVs alone | `### DIAG` |
| S1, S1b | Status quo + one new project in `projects/` | `### S1`, `### S1b` |
| SA | Option A — the new project in its own run | `### SA` |
| SB | Option B — per-project validation identity (prototype) | `### SB` |
| SR | Recommended — A + adoption + coverage record (prototype) | `### SR` |
| SD | Option D — naive `discipline_scope` enforcement (prototype) | `### SD` |
| SX | A *published* project declares adoption in the shared run | `### SX` |
| C | What `check` writes | `### C` |
| F2–F7 | What each failure leaves behind | `### F` |

## Transcript

The complete output of one `run_all.sh` execution on 2026-09-28 (Windows 11,
the project's `.venv`, Python 3.14, ifcopenshell/IfcTester as pinned in
`requirements.txt`). Trailing whitespace has been stripped from each line;
nothing else is edited.

```text

### HEAD a438f5d5195af2186266b7d8bcf1904f0f153d10
dirty/untracked: 0

### S0 baseline: run on the published tree
run exit=0
generated files changed: 0

### DIAG current state, read from the published canonical CSVs only
pairs = 6 models x 14 requirements = 84
discipline vocabulary used by discipline_scope: ['Architecture', 'HVAC', 'Plumbing', 'Structural']
   N/A only    inside                    5
   N/A only    outside                   52
   PASS/FAIL   inside                    25
   PASS/FAIL   outside                   2
evaluated although the rule's own discipline_scope does not name the model's discipline:
   structural (Structural) R-001 Name scope=Architecture pass=4 fail=0
   structural (Structural) R-002 Pset_WallCommon.IsExternal scope=Architecture pass=4 fail=0
elements: 44; reached by >=1 finding: 22; reached by none: 22
   unreached architecture                       IfcBuildingElementProxy    4
   unreached architecture                       IfcChimney                 1
   unreached architecture                       IfcFurniture               1
   unreached architecture                       IfcRoof                    1
   unreached architecture                       IfcSlab                    3
   unreached hvac                               IfcBuildingElementProxy    1
   unreached hvac                               IfcChimney                 1
   unreached iso-reference-view.architecture    IfcOpeningElement          1
   unreached iso-reference-view.architecture    IfcWindow                  1
   unreached iso-reference-view.plumbing        IfcSanitaryTerminal        1
   unreached structural                         IfcBuildingElementProxy    2
   unreached structural                         IfcChimney                 1
   unreached structural                         IfcDiscreteAccessory       2
   unreached structural                         IfcFooting                 1
   unreached structural                         IfcRoof                    1

### N the synthetic counterexample project (tracked sample files only)
probe-applicability.mep         MEP         mep-combined.ifc   e24c1b0f69d188312c8b860d047fb6772bee7f877af77cab6f862a98d67f73c3
probe-applicability.facade      Facade      facade.ifc         73b0e45d931d5dc13bfee5fdc7bd80f796526445458b2de74c4168d209097832
probe-applicability.structural  Structural  structural.ifc     68be722391e7aaa53bb9278645a02aa4b6382f13cc07548a1612e9b1dc3def67

### S1 status quo + N dropped into projects/
   validation run   epc-delivery-v2.2-bc8256f54db4763a
     FAIL 42
     N/A  80
     PASS 66
     108 of 188 applicable
     36 issue(s)
   check exit=0
   error: BCF archive exceeds safe generation limits
   run exit=1
   left behind by the failed run:
     ?? reports/ids/probe-applicability.facade.html
     ?? reports/ids/probe-applicability.facade.json
     ?? reports/ids/probe-applicability.mep.html
     ?? reports/ids/probe-applicability.mep.json
     ?? reports/ids/probe-applicability.structural.html
     ?? reports/ids/probe-applicability.structural.json
   run without the general BCF exporter: exit=0
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7  ->  epc-delivery-v2.2-bc8256f54db4763a  (CHANGED)
artifact_bundle_id bundle-a1fd9360e12c71fa  ->  bundle-60dbf083be5417ee  (CHANGED)
files: 40 -> 46; changed 10, added 6, removed 0
   changed  data/processed/canonical/elements.csv
   changed  data/processed/canonical/findings.csv
   changed  data/processed/canonical/issue_events.csv
   changed  data/processed/canonical/issue_findings.csv
   changed  data/processed/canonical/issues.csv
   changed  data/processed/canonical/models.csv
   changed  data/processed/canonical/project_milestones.csv
   changed  data/processed/canonical/projects.csv
   changed  data/processed/canonical/run.json
   changed  reports/artifact_manifest.json
   added    reports/ids/probe-applicability.facade.html
   added    reports/ids/probe-applicability.facade.json
   added    reports/ids/probe-applicability.mep.html
   added    reports/ids/probe-applicability.mep.json
   added    reports/ids/probe-applicability.structural.html
   added    reports/ids/probe-applicability.structural.json
findings of ['iso-reference-view', 'pcert-sample']: 121 -> 121; keys survived 0/121; keyless content identical: True (only-before 0, only-after 0)
findings, whole run: 121 -> 188; keys survived 0
issues of ['iso-reference-view', 'pcert-sample']: 21 -> 21; keys survived 0/21
   keyless issue content (incl. keyless member findings) identical: True
bcf reports/bcf/ids_failures.bcf: topics 3 -> 3, survived 3; entries 9 -> 9, changed bytes 0
bcf reports/bcf/issues.bcf: topics 21 -> 21, survived 21; entries 42 -> 42, changed bytes 0
   F5 --format subset: the on-disk issues.bcf is a previous run's
   issues.bcf ReferenceLinks: 24; resolving in findings.csv: 0; dangling: 24

### S1b status quo + N1 (one model; the general BCF archive fits)
run exit=0
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7  ->  epc-delivery-v2.2-c7f217dfae5e7c42  (CHANGED)
artifact_bundle_id bundle-a1fd9360e12c71fa  ->  bundle-2919da0463a5d221  (CHANGED)
files: 40 -> 42; changed 11, added 2, removed 0
   changed  data/processed/canonical/elements.csv
   changed  data/processed/canonical/findings.csv
   changed  data/processed/canonical/issue_events.csv
   changed  data/processed/canonical/issue_findings.csv
   changed  data/processed/canonical/issues.csv
   changed  data/processed/canonical/models.csv
   changed  data/processed/canonical/project_milestones.csv
   changed  data/processed/canonical/projects.csv
   changed  data/processed/canonical/run.json
   changed  reports/artifact_manifest.json
   changed  reports/bcf/issues.bcf
   added    reports/ids/probe-applicability.facade.html
   added    reports/ids/probe-applicability.facade.json
findings of ['iso-reference-view', 'pcert-sample']: 121 -> 121; keys survived 0/121; keyless content identical: True (only-before 0, only-after 0)
findings, whole run: 121 -> 135; keys survived 0
issues of ['iso-reference-view', 'pcert-sample']: 21 -> 21; keys survived 0/21
   keyless issue content (incl. keyless member findings) identical: True
bcf reports/bcf/ids_failures.bcf: topics 3 -> 3, survived 3; entries 9 -> 9, changed bytes 0
bcf reports/bcf/issues.bcf: topics 21 -> 22, survived 21; entries 42 -> 44, changed bytes 21

### SA Option A: N outside projects/, its own run configuration
default run exit=0
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7  ->  epc-delivery-v2.2-71d28a7c8bddb4e7  (same)
artifact_bundle_id bundle-a1fd9360e12c71fa  ->  bundle-a1fd9360e12c71fa  (same)
files: 40 -> 40; changed 0, added 0, removed 0
findings of ['iso-reference-view', 'pcert-sample']: 121 -> 121; keys survived 121/121; keyless content identical: True (only-before 0, only-after 0)
findings, whole run: 121 -> 121; keys survived 121
issues of ['iso-reference-view', 'pcert-sample']: 21 -> 21; keys survived 21/21
   keyless issue content (incl. keyless member findings) identical: True
bcf reports/bcf/ids_failures.bcf: topics 3 -> 3, survived 3; entries 9 -> 9, changed bytes 0
bcf reports/bcf/issues.bcf: topics 21 -> 21, survived 21; entries 42 -> 42, changed bytes 0
validation run   epc-delivery-v2.2-fa0763db08ab645f
artifact bundle  bundle-5754fe005fd9c235
as of            2026-08-13T00:00:00Z
3 model(s), 28 element(s), 67 finding(s), 15 issue(s)
isolated run exit=0
published tree after both runs: 0

### SB Option B prototype: per-project validation identity inside one run
Option B prototype applied
B, published projects only: run exit=0
-- B vs S0 (the one-time migration)
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7  ->  epc-delivery-v2.2-71d28a7c8bddb4e7  (same)
artifact_bundle_id bundle-a1fd9360e12c71fa  ->  bundle-a1fd9360e12c71fa  (same)
files: 40 -> 40; changed 7, added 0, removed 0
   changed  data/processed/canonical/findings.csv
   changed  data/processed/canonical/issue_events.csv
   changed  data/processed/canonical/issue_findings.csv
   changed  data/processed/canonical/issues.csv
   changed  data/processed/canonical/run.json
   changed  reports/artifact_manifest.json
   changed  reports/bcf/issues.bcf
findings of ['iso-reference-view', 'pcert-sample']: 121 -> 121; keys survived 0/121; keyless content identical: True (only-before 0, only-after 0)
findings, whole run: 121 -> 121; keys survived 0
issues of ['iso-reference-view', 'pcert-sample']: 21 -> 21; keys survived 0/21
   keyless issue content (incl. keyless member findings) identical: True
bcf reports/bcf/ids_failures.bcf: topics 3 -> 3, survived 3; entries 9 -> 9, changed bytes 0
bcf reports/bcf/issues.bcf: topics 21 -> 21, survived 21; entries 42 -> 42, changed bytes 21
-- B + N vs B
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7  ->  epc-delivery-v2.2-bc8256f54db4763a  (CHANGED)
artifact_bundle_id bundle-a1fd9360e12c71fa  ->  bundle-60dbf083be5417ee  (CHANGED)
files: 40 -> 46; changed 10, added 6, removed 0
findings of ['iso-reference-view', 'pcert-sample']: 121 -> 121; keys survived 121/121; keyless content identical: True (only-before 0, only-after 0)
findings, whole run: 121 -> 188; keys survived 121
issues of ['iso-reference-view', 'pcert-sample']: 21 -> 21; keys survived 21/21
   keyless issue content (incl. keyless member findings) identical: True
bcf reports/bcf/ids_failures.bcf: topics 3 -> 3, survived 3; entries 9 -> 9, changed bytes 0
bcf reports/bcf/issues.bcf: topics 21 -> 21, survived 21; entries 42 -> 42, changed bytes 0
B + N1 run exit=0
-- B + N1 vs B
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7  ->  epc-delivery-v2.2-c7f217dfae5e7c42  (CHANGED)
artifact_bundle_id bundle-a1fd9360e12c71fa  ->  bundle-2919da0463a5d221  (CHANGED)
files: 40 -> 42; changed 11, added 2, removed 0
findings of ['iso-reference-view', 'pcert-sample']: 121 -> 121; keys survived 121/121; keyless content identical: True (only-before 0, only-after 0)
findings, whole run: 121 -> 135; keys survived 121
issues of ['iso-reference-view', 'pcert-sample']: 21 -> 21; keys survived 21/21
   keyless issue content (incl. keyless member findings) identical: True
bcf reports/bcf/ids_failures.bcf: topics 3 -> 3, survived 3; entries 9 -> 9, changed bytes 0
bcf reports/bcf/issues.bcf: topics 21 -> 22, survived 21; entries 42 -> 44, changed bytes 0

### SR recommended-scheme prototype: Option A + [adoption] + coverage record
recommended-scheme prototype applied
default run exit=0
-- SR default run vs S0
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7  ->  epc-delivery-v2.2-71d28a7c8bddb4e7  (same)
artifact_bundle_id bundle-a1fd9360e12c71fa  ->  bundle-a1fd9360e12c71fa  (same)
files: 40 -> 40; changed 0, added 0, removed 0
findings of ['iso-reference-view', 'pcert-sample']: 121 -> 121; keys survived 121/121; keyless content identical: True (only-before 0, only-after 0)
findings, whole run: 121 -> 121; keys survived 121
issues of ['iso-reference-view', 'pcert-sample']: 21 -> 21; keys survived 21/21
   keyless issue content (incl. keyless member findings) identical: True
bcf reports/bcf/ids_failures.bcf: topics 3 -> 3, survived 3; entries 9 -> 9, changed bytes 0
bcf reports/bcf/issues.bcf: topics 21 -> 21, survived 21; entries 42 -> 42, changed bytes 0
-- coverage record of the published run (cross-check of DIAG)
pairs: 84  (every row carries exactly one state: True)
   iso-reference-view     c:no-applicable-entity     34
   iso-reference-view     e:evaluated                8
   pcert-sample           c:no-applicable-entity     23
   pcert-sample           e:evaluated                19
state x scope_relation:
   c:no-applicable-entity     inside                     5
   c:no-applicable-entity     outside                    52
   e:evaluated                inside                     25
   e:evaluated                outside                    2
evaluated although the rule's own discipline_scope does not name the model's discipline:
validation run   epc-delivery-v2.2-fa0763db08ab645f
artifact bundle  bundle-5754fe005fd9c235
as of            2026-08-13T00:00:00Z
3 model(s), 28 element(s), 67 finding(s), 15 issue(s)
-- N isolated, no adoption declared
pairs: 42  (every row carries exactly one state: True)
   probe-applicability    c:no-applicable-entity     23
   probe-applicability    e:evaluated                19
state x scope_relation:
   c:no-applicable-entity     inside                     1
   c:no-applicable-entity     model-discipline-unknown   16
   c:no-applicable-entity     outside                    6
   e:evaluated                inside                     5
   e:evaluated                model-discipline-unknown   12
   e:evaluated                outside                    2
evaluated although the rule's own discipline_scope does not name the model's discipline:
   probe-applicability.facade         Facade      R-001   Name                               scope=Architecture           model-discipline-unknown  pass=1 fail=0
   probe-applicability.facade         Facade      R-002   Pset_WallCommon.IsExternal         scope=Architecture           model-discipline-unknown  pass=1 fail=0
   probe-applicability.facade         Facade      R-006   Name / Category                    scope=Architecture;Structural model-discipline-unknown  pass=1 fail=0
   probe-applicability.facade         Facade      R-009   System / Reference                 scope=Architecture;Structural model-discipline-unknown  pass=0 fail=1
   probe-applicability.facade         Facade      R-010   shared-across-models               scope=Architecture;Structural;HVAC;Plumbing model-discipline-unknown  pass=0 fail=1
   probe-applicability.mep            MEP         R-004A  IFCRELCONTAINEDINSPATIALSTRUCTURE  scope=HVAC                   model-discipline-unknown  pass=1 fail=0
   probe-applicability.mep            MEP         R-004B  IFCRELCONTAINEDINSPATIALSTRUCTURE  scope=HVAC                   model-discipline-unknown  pass=2 fail=0
   probe-applicability.mep            MEP         R-005A  EPC_Delivery.AssetTag              scope=HVAC                   model-discipline-unknown  pass=0 fail=1
   probe-applicability.mep            MEP         R-005A  EPC_Delivery.SystemCode            scope=HVAC                   model-discipline-unknown  pass=0 fail=1
   probe-applicability.mep            MEP         R-005B  EPC_Delivery.AssetTag              scope=HVAC                   model-discipline-unknown  pass=0 fail=2
   probe-applicability.mep            MEP         R-005B  EPC_Delivery.SystemCode            scope=HVAC                   model-discipline-unknown  pass=0 fail=2
   probe-applicability.mep            MEP         R-010   shared-across-models               scope=Architecture;Structural;HVAC;Plumbing model-discipline-unknown  pass=1 fail=0
   probe-applicability.structural     Structural  R-001   Name                               scope=Architecture           outside                   pass=4 fail=0
   probe-applicability.structural     Structural  R-002   Pset_WallCommon.IsExternal         scope=Architecture           outside                   pass=4 fail=0
not adopted:
elements:
   probe-applicability    d:unreached  12
   probe-applicability    reached      16
unreached by class: {('probe-applicability.facade', 'IfcOpeningElement'): 1, ('probe-applicability.facade', 'IfcWindow'): 1, ('probe-applicability.mep', 'IfcBuildingElementProxy'): 1, ('probe-applicability.mep', 'IfcChimney'): 1, ('probe-applicability.mep', 'IfcSanitaryTerminal'): 1, ('probe-applicability.structural', 'IfcBuildingElementProxy'): 2, ('probe-applicability.structural', 'IfcChimney'): 1, ('probe-applicability.structural', 'IfcDiscreteAccessory'): 2, ('probe-applicability.structural', 'IfcFooting'): 1, ('probe-applicability.structural', 'IfcRoof'): 1}
validation run   epc-delivery-v2.2-0a9511df25285672
artifact bundle  bundle-305fc9d7058e746e
as of            2026-08-13T00:00:00Z
3 model(s), 28 element(s), 47 finding(s), 7 issue(s)
exit=0
-- N isolated, adoption declared
pairs: 42  (every row carries exactly one state: True)
   probe-applicability    a:not-adopted              15
   probe-applicability    c:no-applicable-entity     14
   probe-applicability    e:evaluated                13
state x scope_relation:
   a:not-adopted              inside                     1
   a:not-adopted              model-discipline-unknown   10
   a:not-adopted              outside                    4
   c:no-applicable-entity     inside                     1
   c:no-applicable-entity     model-discipline-unknown   11
   c:no-applicable-entity     outside                    2
   e:evaluated                inside                     4
   e:evaluated                model-discipline-unknown   7
   e:evaluated                outside                    2
evaluated although the rule's own discipline_scope does not name the model's discipline:
   probe-applicability.facade         Facade      R-001   Name                               scope=Architecture           model-discipline-unknown  pass=1 fail=0
   probe-applicability.facade         Facade      R-002   Pset_WallCommon.IsExternal         scope=Architecture           model-discipline-unknown  pass=1 fail=0
   probe-applicability.facade         Facade      R-006   Name / Category                    scope=Architecture;Structural model-discipline-unknown  pass=1 fail=0
   probe-applicability.facade         Facade      R-010   shared-across-models               scope=Architecture;Structural;HVAC;Plumbing model-discipline-unknown  pass=0 fail=1
   probe-applicability.mep            MEP         R-004A  IFCRELCONTAINEDINSPATIALSTRUCTURE  scope=HVAC                   model-discipline-unknown  pass=1 fail=0
   probe-applicability.mep            MEP         R-004B  IFCRELCONTAINEDINSPATIALSTRUCTURE  scope=HVAC                   model-discipline-unknown  pass=2 fail=0
   probe-applicability.mep            MEP         R-010   shared-across-models               scope=Architecture;Structural;HVAC;Plumbing model-discipline-unknown  pass=1 fail=0
   probe-applicability.structural     Structural  R-001   Name                               scope=Architecture           outside                   pass=4 fail=0
   probe-applicability.structural     Structural  R-002   Pset_WallCommon.IsExternal         scope=Architecture           outside                   pass=4 fail=0
not adopted:
   probe-applicability.facade         R-005A  EPC_Delivery.AssetTag          reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.facade         R-005A  EPC_Delivery.SystemCode        reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.facade         R-005B  EPC_Delivery.AssetTag          reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.facade         R-005B  EPC_Delivery.SystemCode        reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.facade         R-009   System / Reference             reason=Counterexample only: CCI Construction classification is not
   probe-applicability.mep            R-005A  EPC_Delivery.AssetTag          reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.mep            R-005A  EPC_Delivery.SystemCode        reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.mep            R-005B  EPC_Delivery.AssetTag          reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.mep            R-005B  EPC_Delivery.SystemCode        reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.mep            R-009   System / Reference             reason=Counterexample only: CCI Construction classification is not
   probe-applicability.structural     R-005A  EPC_Delivery.AssetTag          reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.structural     R-005A  EPC_Delivery.SystemCode        reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.structural     R-005B  EPC_Delivery.AssetTag          reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.structural     R-005B  EPC_Delivery.SystemCode        reason=Counterexample only: a project-assumed EPC property set this
   probe-applicability.structural     R-009   System / Reference             reason=Counterexample only: CCI Construction classification is not
elements:
   probe-applicability    d:unreached  12
   probe-applicability    reached      16
unreached by class: {('probe-applicability.facade', 'IfcOpeningElement'): 1, ('probe-applicability.facade', 'IfcWindow'): 1, ('probe-applicability.mep', 'IfcBuildingElementProxy'): 1, ('probe-applicability.mep', 'IfcChimney'): 1, ('probe-applicability.mep', 'IfcSanitaryTerminal'): 1, ('probe-applicability.structural', 'IfcBuildingElementProxy'): 2, ('probe-applicability.structural', 'IfcChimney'): 1, ('probe-applicability.structural', 'IfcDiscreteAccessory'): 2, ('probe-applicability.structural', 'IfcFooting'): 1, ('probe-applicability.structural', 'IfcRoof'): 1}
-- adoption declared vs not
validation_run_id  epc-delivery-v2.2-fa0763db08ab645f  ->  epc-delivery-v2.2-0a9511df25285672  (CHANGED)
artifact_bundle_id bundle-5754fe005fd9c235  ->  bundle-305fc9d7058e746e  (CHANGED)
files: 22 -> 22; changed 7, added 0, removed 0
findings of ['probe-applicability']: 67 -> 47; keys survived 0/67; keyless content identical: False (only-before 20, only-after 0)
findings, whole run: 67 -> 47; keys survived 0
issues of ['probe-applicability']: 15 -> 7; keys survived 0/15
bcf isolated/probe-applicability/out/reports/bcf/issues.bcf: topics 15 -> 7, survived 7; entries 32 -> 16, changed bytes 8
second run: outputs byte-identical
second run: coverage record byte-identical
error: project 'probe-applicability' adoption is not a decision per rule: missing ['R-010'], unknown [], duplicated []
adoption missing R-010: exit=1; outputs written: 0
published tree after SR: 0

### SD Option D prototype: enforce discipline_scope naively (with a throwaway Plumbing rule)
Option D prototype applied (rule only)
   merged model declared MEP: 3 model(s), 28 element(s), 70 finding(s), 15 issue(s)
   merged model declared HVAC: 3 model(s), 28 element(s), 70 finding(s), 15 issue(s)
   merged model declared Plumbing: 3 model(s), 28 element(s), 70 finding(s), 15 issue(s)
Option D prototype applied (rule + naive filter)
   merged model declared MEP: 3 model(s), 28 element(s), 22 finding(s), 10 issue(s)
   merged model declared HVAC: 3 model(s), 28 element(s), 32 finding(s), 13 issue(s)
   merged model declared Plumbing: 3 model(s), 28 element(s), 24 finding(s), 10 issue(s)
declared 'MEP': findings 70 -> 22, issues 15 -> 10
   gone from the merged model: R-001{'N/A': 1} R-002{'N/A': 1} R-003{'N/A': 1} R-004A{'PASS': 1} R-004B{'PASS': 2} R-005A{'FAIL': 2} R-005B{'FAIL': 4} R-006{'N/A': 1} R-007{'N/A': 1} R-008{'N/A': 1} R-009{'N/A': 1} R-010{'PASS': 1} R-P01{'PASS': 1}
   gone from the other two models: 20 (model, rule) groups
declared 'HVAC': findings 70 -> 32, issues 15 -> 13
   gone from the merged model: R-001{'N/A': 1} R-002{'N/A': 1} R-003{'N/A': 1} R-006{'N/A': 1} R-007{'N/A': 1} R-008{'N/A': 1} R-009{'N/A': 1} R-P01{'PASS': 1}
   gone from the other two models: 20 (model, rule) groups
declared 'Plumbing': findings 70 -> 24, issues 15 -> 10
   gone from the merged model: R-001{'N/A': 1} R-002{'N/A': 1} R-003{'N/A': 1} R-004A{'PASS': 1} R-004B{'PASS': 2} R-005A{'FAIL': 2} R-005B{'FAIL': 4} R-006{'N/A': 1} R-007{'N/A': 1} R-008{'N/A': 1} R-009{'N/A': 1}
   gone from the other two models: 20 (model, rule) groups
-- the same naive filter with the prototype coverage record present (merged model declared Plumbing)
pairs: 45  (every row carries exactly one state: True)
   probe-applicability    c:no-applicable-entity     1
   probe-applicability    d:evaluated-no-outcome     37
   probe-applicability    e:evaluated                7
state x scope_relation:
   c:no-applicable-entity     inside                     1
   d:evaluated-no-outcome     model-discipline-unknown   15
   d:evaluated-no-outcome     outside                    22
   e:evaluated                inside                     7

### SX adoption declared by a PUBLISHED project, inside the shared published run
-- pcert declares every rule adopted; identity rule: every decision enters validation_run_id
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7  ->  epc-delivery-v2.2-97c2a029fea47c52  (CHANGED)
files: 40 -> 40; changed 7, added 0, removed 0
findings of ['iso-reference-view', 'pcert-sample']: 121 -> 121; keys survived 0/121; keyless content identical: True (only-before 0, only-after 0)
issues of ['iso-reference-view', 'pcert-sample']: 21 -> 21; keys survived 0/21
findings of ['iso-reference-view']: 42 -> 42; keys survived 0/42; keyless content identical: True (only-before 0, only-after 0)
issues of ['iso-reference-view']: 4 -> 4; keys survived 0/4
-- pcert declares every rule adopted; identity rule: --identity-not-adopted-only
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7  ->  epc-delivery-v2.2-71d28a7c8bddb4e7  (same)
files: 40 -> 40; changed 0, added 0, removed 0
findings of ['iso-reference-view', 'pcert-sample']: 121 -> 121; keys survived 121/121; keyless content identical: True (only-before 0, only-after 0)
issues of ['iso-reference-view', 'pcert-sample']: 21 -> 21; keys survived 21/21
findings of ['iso-reference-view']: 42 -> 42; keys survived 42/42; keyless content identical: True (only-before 0, only-after 0)
issues of ['iso-reference-view']: 4 -> 4; keys survived 4/4
-- pcert declares R-009 not adopted (R-009 is not in the frozen legacy rule set 0.1)
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7  ->  epc-delivery-v2.2-7b1625e1552ff52a  (CHANGED)
artifact_bundle_id bundle-a1fd9360e12c71fa  ->  bundle-31f6aef42250df0f  (CHANGED)
files: 40 -> 40; changed 7, added 0, removed 0
   changed  data/processed/canonical/findings.csv
   changed  data/processed/canonical/issue_events.csv
   changed  data/processed/canonical/issue_findings.csv
   changed  data/processed/canonical/issues.csv
   changed  data/processed/canonical/run.json
   changed  reports/artifact_manifest.json
   changed  reports/bcf/issues.bcf
findings of ['iso-reference-view', 'pcert-sample']: 121 -> 112; keys survived 0/121; keyless content identical: False (only-before 9, only-after 0)
findings, whole run: 121 -> 112; keys survived 0
issues of ['iso-reference-view', 'pcert-sample']: 21 -> 13; keys survived 0/21
bcf reports/bcf/ids_failures.bcf: topics 3 -> 3, survived 3; entries 9 -> 9, changed bytes 0
bcf reports/bcf/issues.bcf: topics 21 -> 13, survived 13; entries 42 -> 26, changed bytes 13
findings of ['iso-reference-view']: 42 -> 42; keys survived 0/42; keyless content identical: True (only-before 0, only-after 0)
issues of ['iso-reference-view']: 4 -> 4; keys survived 0/4
-- pcert declares R-005A/R-005B not adopted (both are in the frozen legacy rule set 0.1)
    M data/processed/bcf_topic_events.csv
    M data/processed/bcf_topic_findings.csv
    M data/processed/bcf_topics.csv
    M data/processed/bcf_viewpoint_components.csv
    M data/processed/bcf_viewpoints.csv
    M data/processed/canonical/findings.csv
    M data/processed/canonical/issue_events.csv
    M data/processed/canonical/issue_findings.csv
    M data/processed/canonical/issues.csv
    M data/processed/canonical/run.json
    M data/processed/ids_findings.csv
    M reports/artifact_manifest.json
    M reports/bcf/ids_failures.bcf
    M reports/bcf/issues.bcf
    M reports/bcf/run_manifest.json
   The published contract no longer matches contract-1.6.json:
     - validation_run_id: recorded 'epc-delivery-v2.2-71d28a7c8bddb4e7', now 'epc-delivery-v2.2-0f72edcce8f3f0b1'
     - artifact_bundle_id: recorded 'bundle-a1fd9360e12c71fa', now 'bundle-5d17f5d29b0aacef'

### C what check writes
check exit=0
   rewritten, same bytes ids/epc-delivery_v2.2.ids
   rewritten, same bytes reports/ids/architecture.html
   rewritten, same bytes reports/ids/architecture.json
   rewritten, same bytes reports/ids/hvac.html
   rewritten, same bytes reports/ids/hvac.json
   rewritten, same bytes reports/ids/iso-reference-view.architecture.html
   rewritten, same bytes reports/ids/iso-reference-view.architecture.json
   rewritten, same bytes reports/ids/iso-reference-view.plumbing.html
   rewritten, same bytes reports/ids/iso-reference-view.plumbing.json
   rewritten, same bytes reports/ids/iso-reference-view.structural.html
   rewritten, same bytes reports/ids/iso-reference-view.structural.json
   rewritten, same bytes reports/ids/structural.html
   rewritten, same bytes reports/ids/structural.json
check --reports-dir <outside> exit=0; reports written there: 12
   rewritten, same bytes ids/epc-delivery_v2.2.ids
tracked files under reports/ids and ids/ listed in artifact_manifest.json: 0

### F failure residue
-- F2 a checker raises on one model (check)
exit=1
Traceback (most recent call last):
epc_control_tower.stages.check.CheckStageError: 1 checker failure(s):
  - [ids] pcert-sample/hvac: injected: model could not be read
files rewritten: 11; hvac report rewritten: 0
-- F4 the last exporter raises after the others wrote (run, N1 present)
error: injected: legacy-pbip could not write
exit=1
   rewritten, changed data/processed/canonical/elements.csv
   rewritten, changed data/processed/canonical/findings.csv
   rewritten, changed data/processed/canonical/issue_events.csv
   rewritten, changed data/processed/canonical/issue_findings.csv
   rewritten, changed data/processed/canonical/issues.csv
   rewritten, changed data/processed/canonical/models.csv
   rewritten, changed data/processed/canonical/project_milestones.csv
   rewritten, changed data/processed/canonical/projects.csv
   rewritten, changed data/processed/canonical/run.json
   rewritten, changed reports/bcf/issues.bcf
   created            reports/ids/probe-applicability.facade.html
   created            reports/ids/probe-applicability.facade.json
artifact_manifest.json: run epc-delivery-v2.2-71d28a7c8bddb4e7, 10/20 listed hashes do not match disk; canonical run.json: run epc-delivery-v2.2-c7f217dfae5e7c42
-- F6 outputs configured outside the repository root
error: <outside>\processed\canonical\projects.csv
exit=1; files written outside before the refusal: 12
-- F7 a workspace (--repository-root) without the vendored BCF schemas
error: <ws>\third_party\buildingsmart\bcf-xml\3.0\Schemas\documents.xsd
exit=1; files written in the workspace: 3
1 model(s), 3 element(s), 14 finding(s), 1 issue(s)
with third_party/ copied in: exit=0

### cleanup
dirty/untracked: 0
```

## Files

### `run_all.sh`

Every scenario, in order.

```bash
#!/usr/bin/env bash
# Every synthetic measurement behind ADR 0004, from a pristine throwaway checkout.
#   CT = a disposable checkout of a438f5d (git worktree add --detach <dir> a438f5d)
#   PY = the project's .venv python;  M = the directory holding these scripts
# Nothing here reads anything outside the checkout except these scripts.
set -u
: "${CT:?}" "${PY:?}" "${M:?}"
cd "$CT"
W="$M/work"; rm -rf "$W"; mkdir -p "$W"
cli() { "$PY" -m epc_control_tower.cli "$@"; }
pristine() { git checkout -q -- . ; git clean -fdq ; rm -rf isolated; }
snap() { "$PY" "$M/snap.py" . "$W/$1.json" "${@:2}" >/dev/null; }
cmp_() { "$PY" "$M/compare.py" "$W/$1.json" "$W/$2.json" "${@:3}"; }
SN="--processed isolated/probe-applicability/out/processed --reports isolated/probe-applicability/out/reports"
isolate() {  # move the synthetic project out of projects/ and give it its own run configuration
  rm -rf isolated; mkdir -p isolated; mv projects/probe-applicability isolated/
  printf '[run]\nruleset_path = "rules/epc-delivery"\nproject_manifests = ["isolated/probe-applicability/project.toml"]\nprocessed_data_dir = "isolated/probe-applicability/out/processed"\nreports_dir = "isolated/probe-applicability/out/reports"\nexporters = ["bcf", "csv", "json"]\n' > isolated/probe.toml
}

echo "### HEAD $(git rev-parse HEAD)"; pristine
echo "dirty/untracked: $(git status --porcelain --untracked-files=all | wc -l)"

echo; echo "### S0 baseline: run on the published tree"
cli run >/dev/null; echo "run exit=$?"; echo "generated files changed: $(git status --porcelain --untracked-files=all | wc -l)"
snap S0

echo; echo "### DIAG current state, read from the published canonical CSVs only"
"$PY" "$M/diag.py" .

echo; echo "### N the synthetic counterexample project (tracked sample files only)"
"$PY" "$M/make_n.py" . N

echo; echo "### S1 status quo + N dropped into projects/"
cli check | sed 's/^/   /'; echo "   check exit=${PIPESTATUS[0]}"
cli run 2>&1 | sed 's/^/   /'; echo "   run exit=${PIPESTATUS[0]}"
echo "   left behind by the failed run:"; git status --porcelain --untracked-files=all -- data reports ids | sed 's/^/     /'
cli run --format csv --format json --format legacy-bcf --format legacy-pbip >/dev/null; echo "   run without the general BCF exporter: exit=$?"
snap S1; cmp_ S0 S1
echo "   F5 --format subset: the on-disk issues.bcf is a previous run's"; "$PY" "$M/dangling.py"

echo; echo "### S1b status quo + N1 (one model; the general BCF archive fits)"
pristine; "$PY" "$M/make_n.py" . N1 >/dev/null
cli run >/dev/null; echo "run exit=$?"; snap S1b; cmp_ S0 S1b

echo; echo "### SA Option A: N outside projects/, its own run configuration"
pristine; "$PY" "$M/make_n.py" . N >/dev/null; isolate
cli run >/dev/null; echo "default run exit=$?"; snap SA; cmp_ S0 SA
cli --config isolated/probe.toml run | sed -n 1,4p; echo "isolated run exit=${PIPESTATUS[0]}"
snap SA-N $SN
echo "published tree after both runs: $(git status --porcelain --untracked-files=all | grep -vc '^?? isolated/')"

echo; echo "### SB Option B prototype: per-project validation identity inside one run"
pristine; "$PY" "$M/apply_B.py" .
cli run >/dev/null; echo "B, published projects only: run exit=$?"; snap SB0
echo "-- B vs S0 (the one-time migration)"; cmp_ S0 SB0
"$PY" "$M/make_n.py" . N >/dev/null
cli run --format csv --format json --format legacy-bcf --format legacy-pbip >/dev/null; snap SB1
echo "-- B + N vs B"; cmp_ SB0 SB1 | grep -v '^   added\|^   changed'
"$PY" "$M/make_n.py" . N1 >/dev/null; rm -f reports/ids/probe-applicability.*
cli run >/dev/null; echo "B + N1 run exit=$?"; snap SB1b
echo "-- B + N1 vs B"; cmp_ SB0 SB1b | grep -v '^   added\|^   changed'

echo; echo "### SR recommended-scheme prototype: Option A + [adoption] + coverage record"
pristine; "$PY" "$M/apply_R.py" .
EPC_PROTO_COVERAGE_OUT="$W/cov-SR0" cli run >/dev/null; echo "default run exit=$?"; snap SR0
echo "-- SR default run vs S0"; cmp_ S0 SR0
echo "-- coverage record of the published run (cross-check of DIAG)"; "$PY" "$M/covsum.py" "$W/cov-SR0" | sed -n 1,11p
"$PY" "$M/make_n.py" . N >/dev/null; isolate
EPC_PROTO_COVERAGE_OUT="$W/cov-SRN0" cli --config isolated/probe.toml run | sed -n 1,4p; snap SRN0 $SN
echo "-- N isolated, no adoption declared"; "$PY" "$M/covsum.py" "$W/cov-SRN0"
"$PY" "$M/make_n.py" . N --adoption "$M/adoption_N.toml" >/dev/null; isolate
EPC_PROTO_COVERAGE_OUT="$W/cov-SRN1" cli --config isolated/probe.toml run | sed -n 1,4p; echo "exit=${PIPESTATUS[0]}"; snap SRN1 $SN
cp -r isolated/probe-applicability/out "$W/SRN1-out"
echo "-- N isolated, adoption declared"; "$PY" "$M/covsum.py" "$W/cov-SRN1"
echo "-- adoption declared vs not"; cmp_ SRN0 SRN1 --projects probe-applicability | grep -v '^   '
"$PY" "$M/make_n.py" . N --adoption "$M/adoption_N.toml" >/dev/null; isolate
EPC_PROTO_COVERAGE_OUT="$W/cov-SRN1b" cli --config isolated/probe.toml run >/dev/null
diff -r "$W/SRN1-out" isolated/probe-applicability/out >/dev/null && echo "second run: outputs byte-identical"
diff -r "$W/cov-SRN1" "$W/cov-SRN1b" >/dev/null && echo "second run: coverage record byte-identical"
"$PY" "$M/make_n.py" . N --adoption "$M/adoption_N_missing_R010.toml" >/dev/null; isolate
cli --config isolated/probe.toml run; echo "adoption missing R-010: exit=$?; outputs written: $(find isolated/probe-applicability -path '*out*' -type f | wc -l)"
echo "published tree after SR: $(git status --porcelain --untracked-files=all | grep -v '^?? isolated/\|epc_control_tower' | wc -l)"

echo; echo "### SD Option D prototype: enforce discipline_scope naively (with a throwaway Plumbing rule)"
for FILTER in --no-filter ""; do
  pristine; "$PY" "$M/apply_D.py" . $FILTER
  for D in MEP HVAC Plumbing; do
    "$PY" "$M/make_n.py" . N --mep-discipline $D >/dev/null; isolate
    cli --config isolated/probe.toml run | sed -n 4p | sed "s/^/   merged model declared $D: /"; snap "SD${FILTER:+0}-$D" $SN
  done
done
"$PY" - "$W" <<'EOF'
import json, sys
w = sys.argv[1]
for d in ("MEP", "HVAC", "Plumbing"):
    a = json.load(open(f"{w}/SD0-{d}.json")); b = json.load(open(f"{w}/SD-{d}.json"))
    gone = sorted(k for k in a["census"] if k not in b["census"])
    mep = [k.split("|")[2] + str(a["census"][k]) for k in gone if ".mep|" in k]
    print(f"declared {d!r}: findings {len(a['finding_keys'])} -> {len(b['finding_keys'])}, issues {len(a['issue_keys'])} -> {len(b['issue_keys'])}")
    print(f"   gone from the merged model: {' '.join(mep)}")
    print(f"   gone from the other two models: {len(gone) - len(mep)} (model, rule) groups")
EOF
echo "-- the same naive filter with the prototype coverage record present (merged model declared Plumbing)"
pristine; "$PY" "$M/apply_R.py" . >/dev/null; "$PY" "$M/apply_D.py" . >/dev/null
"$PY" "$M/make_n.py" . N --mep-discipline Plumbing >/dev/null; isolate
EPC_PROTO_COVERAGE_OUT="$W/cov-RD" cli --config isolated/probe.toml run >/dev/null; "$PY" "$M/covsum.py" "$W/cov-RD" | sed -n 1,9p

echo; echo "### SX adoption declared by a PUBLISHED project, inside the shared published run"
declare_pcert() {  # $1 = space-separated rule ids to mark not-adopted
  "$PY" - "$M/adoption_all_adopted.toml" "$1" <<'EOF'
import sys
t = open(sys.argv[1], encoding="utf-8").read()
for r in sys.argv[2].split():
    t = t.replace(f'rule_id = "{r}"\ndecision = "adopted"', f'rule_id = "{r}"\ndecision = "not-adopted"\nreason = "Counterexample only."')
open("projects/pcert-sample/project.toml", "a", encoding="utf-8", newline="\n").write(t)
EOF
}
for V in "all:" "all-notadopted-only:--identity-not-adopted-only" ; do
  NAME="${V%%:*}"; FLAG="${V#*:}"
  pristine; "$PY" "$M/apply_R.py" . $FLAG >/dev/null; declare_pcert ""
  cli run >/dev/null; snap "SX-$NAME"
  echo "-- pcert declares every rule adopted; identity rule: ${FLAG:-every decision enters validation_run_id}"
  cmp_ S0 "SX-$NAME" | grep '^validation_run_id\|^files\|^findings of\|^issues of'
  cmp_ S0 "SX-$NAME" --projects iso-reference-view | grep '^findings of\|^issues of'
done
pristine; "$PY" "$M/apply_R.py" . --identity-not-adopted-only >/dev/null; declare_pcert "R-009"
cli run >/dev/null; snap SX-noR009
echo "-- pcert declares R-009 not adopted (R-009 is not in the frozen legacy rule set 0.1)"
cmp_ S0 SX-noR009 | grep -v '^   keyless'
cmp_ S0 SX-noR009 --projects iso-reference-view | grep '^findings of\|^issues of'
pristine; "$PY" "$M/apply_R.py" . --identity-not-adopted-only >/dev/null; declare_pcert "R-005A R-005B"
cli run >/dev/null; echo "-- pcert declares R-005A/R-005B not adopted (both are in the frozen legacy rule set 0.1)"
git status --porcelain -- data reports | sed 's/^/   /'
cli snapshot 2>&1 | sed -n 1,3p | sed 's/^/   /'

echo; echo "### C what check writes"
pristine
"$PY" "$M/touched.py" record . "$W/t0.json"; cli check >/dev/null; echo "check exit=$?"
"$PY" "$M/touched.py" record . "$W/t1.json"; "$PY" "$M/touched.py" diff "$W/t0.json" "$W/t1.json"
cli check --reports-dir "$W/check-reports" >/dev/null; echo "check --reports-dir <outside> exit=$?; reports written there: $(ls "$W/check-reports/ids" | wc -l)"
"$PY" "$M/touched.py" record . "$W/t2.json"; "$PY" "$M/touched.py" diff "$W/t1.json" "$W/t2.json"
echo "tracked files under reports/ids and ids/ listed in artifact_manifest.json: $(grep -c '"path": "\(reports/ids\|ids/\)' reports/artifact_manifest.json)"

echo; echo "### F failure residue"
pristine
echo "-- F2 a checker raises on one model (check)"
"$PY" "$M/touched.py" record . "$W/f0.json"; "$PY" "$M/fail_inject.py" checker-hvac check > "$W/F2.out" 2>&1; echo "exit=$?"
head -1 "$W/F2.out"; tail -2 "$W/F2.out"
"$PY" "$M/touched.py" record . "$W/f1.json"; echo "files rewritten: $("$PY" "$M/touched.py" diff "$W/f0.json" "$W/f1.json" | wc -l); hvac report rewritten: $("$PY" "$M/touched.py" diff "$W/f0.json" "$W/f1.json" | grep -c hvac)"
pristine; "$PY" "$M/make_n.py" . N1 >/dev/null
echo "-- F4 the last exporter raises after the others wrote (run, N1 present)"
"$PY" "$M/touched.py" record . "$W/g0.json"; "$PY" "$M/fail_inject.py" exporter-legacy-pbip run 2>&1 | tail -1; echo "exit=${PIPESTATUS[0]}"
"$PY" "$M/touched.py" record . "$W/g1.json"; "$PY" "$M/touched.py" diff "$W/g0.json" "$W/g1.json" | grep -v "same bytes"
"$PY" - <<'EOF'
import json, hashlib, pathlib
m = json.load(open("reports/artifact_manifest.json", encoding="utf-8"))
bad = [a["path"] for a in m["artifacts"] if hashlib.sha256(pathlib.Path(a["path"]).read_bytes()).hexdigest() != a["sha256"]]
run = json.load(open("data/processed/canonical/run.json", encoding="utf-8"))["run"]["validation_run_id"]
print(f"artifact_manifest.json: run {m['validation_run_id']}, {len(bad)}/{len(m['artifacts'])} listed hashes do not match disk; canonical run.json: run {run}")
EOF
pristine; "$PY" "$M/make_n.py" . N1 >/dev/null; isolate
echo "-- F6 outputs configured outside the repository root"
OUT="$W/outside"; printf "[run]\nruleset_path = \"rules/epc-delivery\"\nproject_manifests = [\"isolated/probe-applicability/project.toml\"]\nprocessed_data_dir = \"$(cygpath -m "$OUT")/processed\"\nreports_dir = \"$(cygpath -m "$OUT")/reports\"\nexporters = [\"csv\", \"json\"]\n" > isolated/out.toml
cli --config isolated/out.toml run 2>&1 | sed 's/: .*outside/: <outside>/'; echo "exit=${PIPESTATUS[0]}; files written outside before the refusal: $(find "$OUT" -type f | wc -l)"
echo "-- F7 a workspace (--repository-root) without the vendored BCF schemas"
WS="$W/ws"; mkdir -p "$WS/projects" "$WS/rules"; cp -r rules/epc-delivery "$WS/rules/"; cp -r isolated/probe-applicability "$WS/projects/"
printf '[run]\nruleset_path = "rules/epc-delivery"\nexporters = ["bcf", "csv", "json"]\n' > "$WS/control-tower.toml"
cli --repository-root "$WS" run 2>&1 | sed 's/: .*ws/: <ws>/'; echo "exit=${PIPESTATUS[0]}; files written in the workspace: $(find "$WS" -newer "$WS/control-tower.toml" -type f | wc -l)"
cp -r third_party "$WS/" ; cli --repository-root "$WS" run | sed -n 4p; echo "with third_party/ copied in: exit=${PIPESTATUS[0]}"

echo; echo "### cleanup"; pristine; echo "dirty/untracked: $(git status --porcelain --untracked-files=all | wc -l)"
```

### `make_n.py`

The synthetic counterexample project.

```python
"""Create the synthetic counterexample project inside a throwaway checkout.

usage: python make_n.py <checkout> <variant> [--mep-discipline D] [--adoption FILE]

variant "N"  : three models
    mep        merged MEP: data/raw/Building-Hvac.ifc plus the IfcSanitaryTerminal
               of projects/iso-reference-view/basin-tessellation.ifc, contained in
               the HVAC file's storey. Declared discipline = --mep-discipline
               (default "MEP").
    facade     projects/iso-reference-view/wall-with-opening-and-window.ifc,
               declared discipline "Facade" (in no rule's discipline_scope).
    structural data/raw/Building-Structural.ifc, declared "Structural".
variant "N1" : the facade model only.

Every input is a file already tracked in the repository. Nothing private.
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

import ifcopenshell

PROJECT = "probe-applicability"


def merged_mep(root: Path, target: Path) -> None:
    hvac = ifcopenshell.open(str(root / "data/raw/Building-Hvac.ifc"))
    basin = ifcopenshell.open(str(root / "projects/iso-reference-view/basin-tessellation.ifc"))
    storey = sorted(hvac.by_type("IfcBuildingStorey"), key=lambda s: s.GlobalId)[0]
    added = [hvac.add(t) for t in sorted(basin.by_type("IfcSanitaryTerminal"), key=lambda t: t.GlobalId)]
    owner = hvac.by_type("IfcOwnerHistory")
    hvac.create_entity(
        "IfcRelContainedInSpatialStructure",
        GlobalId="1mergedMepContainment0",
        OwnerHistory=owner[0] if owner else None,
        Name="probe merged MEP containment",
        RelatedElements=added,
        RelatingStructure=storey,
    )
    hvac.write(str(target))
    # Pin line endings so the bytes do not depend on the platform.
    target.write_bytes(target.read_bytes().replace(b"\r\n", b"\n"))


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    variant = sys.argv[2]
    args = sys.argv[3:]
    mep_discipline = args[args.index("--mep-discipline") + 1] if "--mep-discipline" in args else "MEP"
    adoption = Path(args[args.index("--adoption") + 1]).read_text(encoding="utf-8") if "--adoption" in args else ""
    project_dir = root / "projects" / PROJECT
    if project_dir.exists():
        shutil.rmtree(project_dir)
    project_dir.mkdir(parents=True)

    models = []
    if variant == "N":
        merged_mep(root, project_dir / "mep-combined.ifc")
        models.append(("mep", mep_discipline, "mep-combined.ifc"))
    shutil.copyfile(root / "projects/iso-reference-view/wall-with-opening-and-window.ifc", project_dir / "facade.ifc")
    models.append(("facade", "Facade", "facade.ifc"))
    if variant == "N":
        shutil.copyfile(root / "data/raw/Building-Structural.ifc", project_dir / "structural.ifc")
        models.append(("structural", "Structural", "structural.ifc"))

    lines = [
        "[project]",
        f'project_id = "{PROJECT}"',
        'name = "Applicability counterexample (synthetic)"',
        'stage = "Probe"',
        'description = "Throwaway counterexample assembled from tracked sample files."',
        "",
    ]
    for model_id, discipline, filename in models:
        lines += [
            "[[models]]",
            f'model_id = "{model_id}"',
            f'discipline = "{discipline}"',
            f'filename = "{filename}"',
            'license = "CC BY 4.0 (derived from tracked buildingSMART samples)"',
            f'content_sha256 = "{sha(project_dir / filename)}"',
            "",
        ]
    for stage, due in (("Design", "2026-07-01"), ("Coordination", "2026-08-01"), ("Handover", "2026-12-01")):
        lines += ["[[milestones]]", f'stage = "{stage}"', f'due = "{due}T00:00:00Z"', ""]
    if adoption:
        lines.append(adoption)
    (project_dir / "project.toml").write_bytes("\n".join(lines).encode("utf-8"))
    for model_id, discipline, filename in models:
        print(f"{PROJECT}.{model_id:<11} {discipline:<11} {filename:<18} {sha(project_dir / filename)}")


if __name__ == "__main__":
    main()
```

### `snap.py`

Snapshot of one checkout's generated state (keys, keyless content, BCF topics, bytes).

```python
"""Snapshot one checkout's generated state, for keyless before/after comparison.

usage: python snap.py <checkout> <out.json> [--processed DIR] [--reports DIR]

Collects, without interpreting:
  * sha256 of every file under data/processed, reports, ids (or the given dirs)
  * validation_run_id / artifact_bundle_id
  * finding keys and a KEYLESS content signature per finding
  * issue keys, keyless issue signature (with keyless member-finding signatures)
  * BCF topic guids and per-entry sha256 for every .bcf archive
  * a (project, model, rule) census of finding statuses
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


FINDING_CONTENT = (
    "project_id", "model_key", "element_key", "requirement_key", "status",
    "severity", "is_applicable", "is_issue", "expected", "actual", "reason",
)
ISSUE_CONTENT = (
    "project_id", "model_key", "element_key", "grouping_policy", "group_ref",
    "lifecycle_state", "assignee_role", "priority", "stage", "due", "labels",
    "is_overdue",
)


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2])
    args = sys.argv[3:]
    processed = root / "data" / "processed"
    reports = root / "reports"
    if "--processed" in args:
        processed = root / args[args.index("--processed") + 1]
    if "--reports" in args:
        reports = root / args[args.index("--reports") + 1]
    canonical = processed / "canonical"

    files = {}
    for base in (processed, reports, root / "ids"):
        if base.exists():
            for p in sorted(base.rglob("*")):
                if p.is_file():
                    files[p.relative_to(root).as_posix()] = sha(p.read_bytes())

    run = {}
    run_json = canonical / "run.json"
    if run_json.is_file():
        doc = json.loads(run_json.read_text(encoding="utf-8"))
        run = doc.get("run", doc)
    manifest = reports / "artifact_manifest.json"
    bundle_id = ""
    if manifest.is_file():
        bundle_id = json.loads(manifest.read_text(encoding="utf-8")).get("artifact_bundle_id", "")

    reqs = {r["requirement_key"]: r for r in rows(canonical / "requirements.csv")}
    findings = rows(canonical / "findings.csv")
    by_key = {}
    for f in findings:
        sig = "|".join(f[c] for c in FINDING_CONTENT)
        by_key[f["finding_key"]] = sig
    issues = rows(canonical / "issues.csv")
    members: dict[str, list[str]] = {}
    for link in rows(canonical / "issue_findings.csv"):
        members.setdefault(link["issue_key"], []).append(by_key.get(link["finding_key"], "?"))
    issue_sigs = {}
    for i in issues:
        sig = "|".join(i[c] for c in ISSUE_CONTENT) + "||" + "##".join(sorted(members.get(i["issue_key"], [])))
        issue_sigs[i["issue_key"]] = sig

    census: dict[str, dict[str, int]] = {}
    for f in findings:
        rule = reqs.get(f["requirement_key"], {}).get("rule_id", "?")
        k = f"{f['project_id']}|{f['model_key']}|{rule}"
        census.setdefault(k, {})
        census[k][f["status"]] = census[k].get(f["status"], 0) + 1

    bcf = {}
    for base in (reports,):
        for p in sorted(base.rglob("*.bcf")):
            z = zipfile.ZipFile(io.BytesIO(p.read_bytes()))
            entries = {n: sha(z.read(n)) for n in z.namelist() if not n.endswith("/")}
            topics = sorted({n.split("/")[0] for n in z.namelist() if "/" in n})
            bcf[p.relative_to(root).as_posix()] = {"topics": topics, "entries": entries}

    state = {
        "validation_run_id": run.get("validation_run_id", ""),
        "artifact_bundle_id": bundle_id,
        "files": files,
        "finding_keys": sorted(by_key),
        "finding_sigs": sorted(by_key.values()),
        "finding_key_to_sig": by_key,
        "issue_keys": sorted(issue_sigs),
        "issue_sigs": sorted(issue_sigs.values()),
        "issue_projects": {i["issue_key"]: i["project_id"] for i in issues},
        "finding_projects": {f["finding_key"]: f["project_id"] for f in findings},
        "census": census,
        "bcf": bcf,
    }
    out.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
    print(f"snapshot {out.name}: files={len(files)} findings={len(findings)} "
          f"issues={len(issues)} run={state['validation_run_id']} bundle={bundle_id}")


if __name__ == "__main__":
    main()
```

### `compare.py`

Keyed and keyless comparison of two snapshots.

```python
"""Compare two snapshots from snap.py, keyed and keyless.

usage: python compare.py <before.json> <after.json> [--projects p1,p2]

--projects restricts the finding/issue comparison to the named projects
(default: pcert-sample,iso-reference-view — the two published projects).
"""
from __future__ import annotations

import json
import sys
from collections import Counter


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    a, b = load(sys.argv[1]), load(sys.argv[2])
    args = sys.argv[3:]
    projects = set((args[args.index("--projects") + 1] if "--projects" in args else "pcert-sample,iso-reference-view").split(","))

    print(f"validation_run_id  {a['validation_run_id']}  ->  {b['validation_run_id']}  "
          f"({'same' if a['validation_run_id'] == b['validation_run_id'] else 'CHANGED'})")
    print(f"artifact_bundle_id {a['artifact_bundle_id']}  ->  {b['artifact_bundle_id']}  "
          f"({'same' if a['artifact_bundle_id'] == b['artifact_bundle_id'] else 'CHANGED'})")

    fa, fb = a["files"], b["files"]
    changed = sorted(p for p in fa if p in fb and fa[p] != fb[p])
    added = sorted(p for p in fb if p not in fa)
    removed = sorted(p for p in fa if p not in fb)
    print(f"files: {len(fa)} -> {len(fb)}; changed {len(changed)}, added {len(added)}, removed {len(removed)}")
    for label, items in (("changed", changed), ("added", added), ("removed", removed)):
        for p in items:
            print(f"   {label:<8} {p}")

    def scoped(state, kind):
        owner = state[f"{kind}_projects"]
        keys = {k for k, pid in owner.items() if pid in projects}
        return keys

    ka, kb = scoped(a, "finding"), scoped(b, "finding")
    sa = Counter(a["finding_key_to_sig"][k] for k in ka)
    sb = Counter(b["finding_key_to_sig"][k] for k in kb)
    print(f"findings of {sorted(projects)}: {len(ka)} -> {len(kb)}; keys survived {len(ka & kb)}/{len(ka)}; "
          f"keyless content identical: {sa == sb} (only-before {sum((sa - sb).values())}, only-after {sum((sb - sa).values())})")
    all_a, all_b = set(a["finding_keys"]), set(b["finding_keys"])
    print(f"findings, whole run: {len(all_a)} -> {len(all_b)}; keys survived {len(all_a & all_b)}")

    ia, ib = scoped(a, "issue"), scoped(b, "issue")
    ika = {k for k in ia}
    ikb = {k for k in ib}
    # keyless issue signature is recorded per key in issue_sigs order; rebuild map
    print(f"issues of {sorted(projects)}: {len(ia)} -> {len(ib)}; keys survived {len(ika & ikb)}/{len(ia)}")
    ca = Counter(s for s in a["issue_sigs"] if s.split("|", 1)[0] in projects)
    cb = Counter(s for s in b["issue_sigs"] if s.split("|", 1)[0] in projects)
    print(f"   keyless issue content (incl. keyless member findings) identical: {ca == cb}")

    for path in sorted(set(a["bcf"]) | set(b["bcf"])):
        ba, bb = a["bcf"].get(path), b["bcf"].get(path)
        if not ba or not bb:
            print(f"bcf {path}: present before={bool(ba)} after={bool(bb)}")
            continue
        ta, tb = set(ba["topics"]), set(bb["topics"])
        ea, eb = ba["entries"], bb["entries"]
        ch = sorted(n for n in ea if n in eb and ea[n] != eb[n])
        print(f"bcf {path}: topics {len(ta)} -> {len(tb)}, survived {len(ta & tb)}; "
              f"entries {len(ea)} -> {len(eb)}, changed bytes {len(ch)}")


if __name__ == "__main__":
    main()
```

### `diag.py`

Current-state diagnosis from the published canonical CSVs only.

```python
"""Diagnose a published run from its canonical CSVs alone (no prototype code).

For every (model, requirement) pair: what came back (N/A only, PASS/FAIL, or
nothing) and how the rule's discipline_scope relates to the model's declared
discipline. For every element: reached by at least one finding, or not.
"""
import csv
import sys
from collections import Counter
from pathlib import Path

root = Path(sys.argv[1]) / "data/processed/canonical"


def rows(name):
    with (root / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


reqs = rows("requirements.csv")
models = rows("models.csv")
findings = rows("findings.csv")
vocabulary = sorted({d for r in reqs for d in r["discipline_scope"].split(";") if d})
by_pair = Counter()
status = {}
for f in findings:
    status.setdefault((f["model_key"], f["requirement_key"]), Counter())[f["status"]] += 1
pairs = Counter()
outside_evaluated = []
for m in models:
    for r in reqs:
        scope = [d for d in r["discipline_scope"].split(";") if d]
        rel = "inside" if m["discipline"] in scope else ("outside" if m["discipline"] in vocabulary else "model-discipline-unknown")
        c = status.get((m["model_key"], r["requirement_key"]), Counter())
        got = "PASS/FAIL" if c["PASS"] + c["FAIL"] else ("N/A only" if c["N/A"] else "no finding")
        pairs[(got, rel)] += 1
        if got == "PASS/FAIL" and rel != "inside":
            outside_evaluated.append((m["model_key"], m["discipline"], r["rule_id"], r["requirement_id"], r["discipline_scope"], c["PASS"], c["FAIL"]))
print(f"pairs = {len(models)} models x {len(reqs)} requirements = {len(models) * len(reqs)}")
print(f"discipline vocabulary used by discipline_scope: {vocabulary}")
for k in sorted(pairs):
    print(f"   {k[0]:<11} {k[1]:<25} {pairs[k]}")
print("evaluated although the rule's own discipline_scope does not name the model's discipline:")
for row in outside_evaluated:
    print("   %s (%s) %s %s scope=%s pass=%d fail=%d" % row)
elements = rows("elements.csv")
reached = {f["element_key"] for f in findings if f["element_key"]}
un = Counter((e["model_key"], e["ifc_class"]) for e in elements if e["element_key"] not in reached)
print(f"elements: {len(elements)}; reached by >=1 finding: {len(reached)}; reached by none: {sum(un.values())}")
for k in sorted(un):
    print(f"   unreached {k[0]:<34} {k[1]:<26} {un[k]}")
```

### `apply_B.py`

PROTOTYPE — Option B.

```python
"""THROWAWAY PROTOTYPE, never for merge: Option B — per-project validation identity.

Each project's findings and issues are keyed from a validation_run_id that
digests only that project's models. The run-level validation_run_id (all
models) is kept for run.json and the artifact bundle. Applied to a throwaway
checkout by exact string replacement; every replacement must match once.
"""
import sys
from pathlib import Path

root = Path(sys.argv[1])


def patch(rel, old, new):
    p = root / rel
    text = p.read_bytes().decode("utf-8")
    assert text.count(old) == 1, (rel, old[:60])
    p.write_bytes(text.replace(old, new).encode("utf-8"))


# pipeline: derive one id per project, hand it to check, group per project
patch("epc_control_tower/pipeline.py",
"""    checked = check(
        registry=registry,""",
"""    _project_of = {model.model_key: model.project_id for model in ingested.models}
    project_run_ids = {
        project.project_id: build_validation_run_id(
            ruleset_id=ruleset.ruleset_id,
            ruleset_version=ruleset.version,
            ruleset_normalized_digest=ruleset.normalized_digest,
            models=[item for item in model_inputs if _project_of[item[0]] == project.project_id],
            checkers=checker_fingerprints,
            as_of=config.as_of,
        )
        for project in ingested.projects
    }

    checked = check(
        project_run_ids=project_run_ids,
        registry=registry,""")
patch("epc_control_tower/pipeline.py",
"""    grouped = group(
        checked.findings,
        registry=registry,
        policy_id=config.grouping_policy,
        validation_run_id=validation_run_id,
        as_of=config.as_of,
        requirements=ruleset.requirements,
        programmes=programmes,
    )
""",
"""    from .stages.group import GroupResult

    _issues, _events = [], []
    for _pid in sorted(project_run_ids):
        _g = group(
            [f for f in checked.findings if f.project_id == _pid],
            registry=registry,
            policy_id=config.grouping_policy,
            validation_run_id=project_run_ids[_pid],
            as_of=config.as_of,
            requirements=ruleset.requirements,
            programmes=programmes,
        )
        _issues.extend(_g.issues)
        _events.extend(_g.events)
    _issues.sort(key=lambda issue: issue.group_ref)
    _order = {issue.issue_key: n for n, issue in enumerate(_issues)}
    _events.sort(key=lambda event: (_order[event.issue_key], event.sequence))
    grouped = GroupResult(issues=tuple(_issues), events=tuple(_events))
""")
patch("epc_control_tower/stages/check.py",
"""    reports_dir: Path,
) -> CheckResult:""",
"""    reports_dir: Path,
    project_run_ids=None,
) -> CheckResult:""")
patch("epc_control_tower/stages/check.py",
"""                validation_run_id=validation_run_id,
                as_of=as_of,
                project=project,""",
"""                validation_run_id=(project_run_ids or {}).get(project.project_id, validation_run_id),
                as_of=as_of,
                project=project,""")
# validation: a finding/issue belongs to its project's validation, not the run's
patch("epc_control_tower/validation.py",
"""    for finding in bundle.findings:
        if finding.project_id not in project_ids:""",
"""    _project_of = {m.model_key: m.project_id for m in bundle.models}
    _allowed = {bundle.run.validation_run_id} | {
        build_validation_run_id(
            ruleset_id=bundle.run.ruleset_id,
            ruleset_version=bundle.run.ruleset_version,
            ruleset_normalized_digest=bundle.run.ruleset_normalized_digest,
            models=[i for i in bundle.run.model_inputs if _project_of.get(i[0]) == pid],
            checkers=bundle.run.checker_fingerprints,
            as_of=bundle.run.as_of,
        )
        for pid in project_ids
    }

    for finding in bundle.findings:
        if finding.project_id not in project_ids:""")
patch("epc_control_tower/validation.py",
"""        if finding.validation_run_id != bundle.run.validation_run_id:""",
"""        if finding.validation_run_id not in _allowed:""")
patch("epc_control_tower/validation.py",
"""        if issue.validation_run_id != bundle.run.validation_run_id:""",
"""        if issue.validation_run_id not in _allowed:""")
print("Option B prototype applied")
```

### `apply_R.py`

PROTOTYPE — the recommended scheme's code half (adoption + coverage record).

```python
"""THROWAWAY PROTOTYPE, never for merge: the recommended scheme's code half.

  * `[adoption]` in project.toml — validation-layer project data, NOT under
    `[overlay]`: one decision per rule of the pinned rule set, adopted or
    not-adopted (the latter with a reason). Refuses on a missing, duplicated or
    unknown rule, or a rule set mismatch.
  * A not-adopted requirement is not evaluated for that project.
  * The adoption decisions (never the reasons) enter validation_run_id — as a
    member that is ABSENT when no project declares adoption, so every existing
    identity is unchanged.
  * A coverage record (pair grain + element grain) is written to the directory
    named by EPC_PROTO_COVERAGE_OUT, outside every published root. It is not an
    exporter and not a published artifact in this prototype.
  * discipline_scope is NOT enforced. It is only *related* to the model's
    declared discipline: inside / outside / model-discipline-unknown.
"""
import sys
from pathlib import Path

root = Path(sys.argv[1])
# --identity-not-adopted-only: only "not-adopted" decisions enter validation_run_id
# (an "adopted" decision cannot change a finding). Default: every decision does.
ALL = "--identity-not-adopted-only" not in sys.argv


def patch(rel, old, new):
    p = root / rel
    text = p.read_bytes().decode("utf-8")
    assert text.count(old) == 1, (rel, old[:70])
    p.write_bytes(text.replace(old, new).encode("utf-8"))


# -- identity: an optional member, absent unless declared -------------------
patch("epc_control_tower/identity.py",
"""    checkers: Iterable[ComponentFingerprint],
    as_of: str,
) -> str:
    \"\"\"Derive the deterministic identity of a validation.""",
"""    checkers: Iterable[ComponentFingerprint],
    as_of: str,
    adoption: Iterable[tuple[str, str, str]] = (),
) -> str:
    \"\"\"Derive the deterministic identity of a validation.""")
patch("epc_control_tower/identity.py",
"""    digest = hashlib.sha256(
        canonical_json_document(document).encode("utf-8")
    ).hexdigest()
    return f"{ruleset_id}-v{ruleset_version}-{digest[:16]}\"""",
"""    adoption = sorted(adoption)
    if adoption:
        document["adoption"] = [
            {"project_id": p, "rule_id": r, "decision": d} for p, r, d in adoption
        ]
    digest = hashlib.sha256(
        canonical_json_document(document).encode("utf-8")
    ).hexdigest()
    return f"{ruleset_id}-v{ruleset_version}-{digest[:16]}\"""")

# -- domain: the run carries its adoption so the id recomputes ---------------
patch("epc_control_tower/domain.py",
"""    checker_fingerprints: tuple[ComponentFingerprint, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.validation_run_id, "validation_run_id")""",
"""    checker_fingerprints: tuple[ComponentFingerprint, ...] = ()
    adoption: tuple[tuple[str, str, str], ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.validation_run_id, "validation_run_id")""")
patch("epc_control_tower/validation.py",
"""            checkers=bundle.run.checker_fingerprints,
            as_of=bundle.run.as_of,
        )
        if expected_run_id != bundle.run.validation_run_id:""",
"""            checkers=bundle.run.checker_fingerprints,
            as_of=bundle.run.as_of,
            adoption=bundle.run.adoption,
        )
        if expected_run_id != bundle.run.validation_run_id:""")

# -- config: read [adoption] ---------------------------------------------------
patch("epc_control_tower/config.py",
"""    milestones: tuple[ProjectMilestone, ...] = ()

    def model_by_filename""",
"""    milestones: tuple[ProjectMilestone, ...] = ()
    #: None = the project declares no adoption (every rule is evaluated, and the
    #: coverage record says "undeclared"). Otherwise (ruleset_id, version,
    #: ((rule_id, decision, reason), ...)).
    adoption: tuple | None = None

    def model_by_filename""")
patch("epc_control_tower/config.py",
"""    return ProjectManifest(
        project=project,
        models=tuple(models),
        raw_data_dir=raw_data_dir,
        milestones=milestones,
    )""",
"""    adoption = None
    section = document.get("adoption")
    if section is not None:
        decisions = []
        for entry in section.get("rules", []):
            decision = str(_require(entry, "decision", path))
            if decision not in ("adopted", "not-adopted"):
                raise ValueError(f"{path}: adoption decision {decision!r} is not adopted/not-adopted")
            reason = str(entry.get("reason", ""))
            if decision == "not-adopted" and not reason:
                raise ValueError(f"{path}: rule {entry.get('rule_id')!r} is not-adopted without a reason")
            decisions.append((str(_require(entry, "rule_id", path)), decision, reason))
        adoption = (
            str(_require(section, "ruleset_id", path)),
            str(_require(section, "ruleset_version", path)),
            tuple(decisions),
        )

    return ProjectManifest(
        project=project,
        models=tuple(models),
        raw_data_dir=raw_data_dir,
        milestones=milestones,
        adoption=adoption,
    )""")

# -- pipeline: validate adoption against the rule set, fail closed -----------
patch("epc_control_tower/pipeline.py",
"""    ingested = ingest(manifests)""",
f"""    IDENTITY_ALL_DECISIONS = {ALL}
""" + """    adopted_by_project: dict[str, frozenset[str]] = {}
    adoption_members: list[tuple[str, str, str]] = []
    rule_ids = sorted({r.rule_id for r in ruleset.requirements})
    for manifest in manifests:
        if manifest.adoption is None:
            continue
        pid = manifest.project.project_id
        rs_id, rs_version, decisions = manifest.adoption
        if (rs_id, rs_version) != (ruleset.ruleset_id, ruleset.version):
            raise ValueError(
                f"project {pid!r} records adoption against {rs_id} {rs_version}; "
                f"this run evaluates {ruleset.ruleset_id} {ruleset.version}. "
                "Nothing is evaluated for a project whose adoption names another rule set."
            )
        seen = [rule_id for rule_id, _d, _r in decisions]
        missing = sorted(set(rule_ids) - set(seen))
        unknown = sorted(set(seen) - set(rule_ids))
        duplicated = sorted({r for r in seen if seen.count(r) > 1})
        if missing or unknown or duplicated:
            raise ValueError(
                f"project {pid!r} adoption is not a decision per rule: "
                f"missing {missing}, unknown {unknown}, duplicated {duplicated}"
            )
        adopted_rules = {rule_id for rule_id, d, _r in decisions if d == "adopted"}
        adopted_by_project[pid] = frozenset(
            r.requirement_key for r in ruleset.requirements if r.rule_id in adopted_rules
        )
        adoption_members.extend(
            (pid, rule_id, d) for rule_id, d, _r in decisions
            if IDENTITY_ALL_DECISIONS or d == "not-adopted"
        )

    ingested = ingest(manifests)""")
patch("epc_control_tower/pipeline.py",
"""        checkers=checker_fingerprints,
        as_of=config.as_of,
    )

    checked = check(""",
"""        checkers=checker_fingerprints,
        as_of=config.as_of,
        adoption=adoption_members,
    )

    checked = check(
        adopted_by_project=adopted_by_project,""")
patch("epc_control_tower/pipeline.py",
"""        model_inputs=model_inputs,
        checker_fingerprints=checker_fingerprints,
    )
""",
"""        model_inputs=model_inputs,
        checker_fingerprints=checker_fingerprints,
        adoption=tuple(sorted(adoption_members)),
    )
""")
patch("epc_control_tower/pipeline.py",
"""    if verify:
        validate_bundle(bundle)
""",
"""    if verify:
        validate_bundle(bundle)

    import os
    if os.environ.get("EPC_PROTO_COVERAGE_OUT"):
        from ._proto_coverage import write_coverage
        write_coverage(bundle, manifests, Path(os.environ["EPC_PROTO_COVERAGE_OUT"]))
""")
patch("epc_control_tower/stages/check.py",
"""    reports_dir: Path,
) -> CheckResult:""",
"""    reports_dir: Path,
    adopted_by_project=None,
) -> CheckResult:""")
patch("epc_control_tower/stages/check.py",
"""        for checker_id, requirements in routed.items():
            context = CheckContext(""",
"""        for checker_id, requirements in routed.items():
            adopted = (adopted_by_project or {}).get(project.project_id)
            if adopted is not None:
                requirements = tuple(r for r in requirements if r.requirement_key in adopted)
                if not requirements:
                    continue
            context = CheckContext(""")

(root / "epc_control_tower/_proto_coverage.py").write_bytes('''"""PROTOTYPE coverage record: every (project, model, requirement) pair in exactly
one of (a) not-adopted, (b) out-of-discipline-scope, (c) no-applicable-entity,
(d) evaluated-no-outcome, (e) evaluated; plus element-grain reach."""
import csv
from collections import Counter, defaultdict
from pathlib import Path

ENFORCE_DISCIPLINE_SCOPE = False  # BIM constraint 3: not before merged-model declaration


def write_coverage(bundle, manifests, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    adoption = {m.project.project_id: m.adoption for m in manifests}
    vocabulary = sorted({d for r in bundle.ruleset.requirements for d in r.discipline_scope})
    counts = defaultdict(Counter)
    for f in bundle.findings:
        counts[(f.model_key, f.requirement_key)][str(f.status)] += 1
    rows = []
    for model in sorted(bundle.models, key=lambda m: m.model_key):
        decl = adoption.get(model.project_id)
        decisions = {r: (d, why) for r, d, why in decl[2]} if decl else {}
        for req in sorted(bundle.ruleset.requirements, key=lambda r: (r.rule_id, r.requirement_id)):
            if model.discipline in req.discipline_scope:
                relation = "inside"
            elif model.discipline in vocabulary:
                relation = "outside"
            else:
                relation = "model-discipline-unknown"
            c = counts.get((model.model_key, req.requirement_key), Counter())
            if decl is None:
                adoption_state, reason = "undeclared", ""
            else:
                adoption_state, reason = decisions[req.rule_id]
            if adoption_state == "not-adopted":
                state = "a:not-adopted"
            elif ENFORCE_DISCIPLINE_SCOPE and relation != "inside":
                state = "b:out-of-discipline-scope"
            elif c["PASS"] + c["FAIL"]:
                state = "e:evaluated"
            elif c["N/A"]:
                state = "c:no-applicable-entity"
            else:
                state = "d:evaluated-no-outcome"
            rows.append({
                "project_id": model.project_id, "model_key": model.model_key,
                "model_discipline": model.discipline, "rule_id": req.rule_id,
                "requirement_id": req.requirement_id, "requirement_key": req.requirement_key,
                "adoption": adoption_state, "adoption_reason": reason,
                "discipline_scope": ";".join(req.discipline_scope),
                "scope_relation": relation, "state": state,
                "pass": c["PASS"], "fail": c["FAIL"], "na": c["N/A"],
            })
    with (out / "requirement_coverage.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\\n")
        w.writeheader(); w.writerows(rows)
    reached = {f.element_key for f in bundle.findings if f.element_key}
    erows = [{"project_id": next(m.project_id for m in bundle.models if m.model_key == e.model_key),
              "model_key": e.model_key, "element_key": e.element_key, "ifc_class": e.ifc_class,
              "state": "reached" if e.element_key in reached else "d:unreached"}
             for e in sorted(bundle.elements, key=lambda e: e.element_key)]
    with (out / "element_coverage.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(erows[0]), lineterminator="\\n")
        w.writeheader(); w.writerows(erows)
''' .encode("utf-8"))
print("recommended-scheme prototype applied")
```

### `apply_D.py`

PROTOTYPE — Option D.

```python
"""THROWAWAY PROTOTYPE, never for merge: Option D — enforce discipline_scope naively.

usage: python apply_D.py <checkout> [--no-filter]

Adds a counterexample-only Plumbing rule (R-P01, sanitary terminals need spatial
assignment) so that a merged MEP model has a rule from each of two disciplines
to lose. Unless --no-filter, the check stage then drops every finding whose
model's declared discipline is not in the requirement's discipline_scope — the
"just make discipline_scope work" change, with no record of what it dropped.
"""
import sys
from pathlib import Path

root = Path(sys.argv[1])
(root / "rules/epc-delivery/R-P01.toml").write_bytes(b'''rule_id = "R-P01"
title = "Sanitary terminals need spatial assignment (counterexample only)"
description = "Throwaway rule for a measurement; never committed."
checker = "ids"
severity = "ERROR"
owner_role = "mep-lead"
stage = "Coordination"
discipline_scope = ["Plumbing"]
citation = "Counterexample only."

[[applicability]]
facet = "entity"
name = "IFCSANITARYTERMINAL"

[[requirements]]
facet = "partof"
relation = "IFCRELCONTAINEDINSPATIALSTRUCTURE"
cardinality = "required"
instructions = "Assign the terminal to an IfcSpace or IfcBuildingStorey."

[requirements.name]
enumeration = ["IFCSPACE", "IFCBUILDINGSTOREY"]
''')
if "--no-filter" not in sys.argv:
    p = root / "epc_control_tower/stages/check.py"
    text = p.read_bytes().decode("utf-8")
    old = """    # Sorted here rather than trusted from the checkers"""
    new = """    _discipline = {model.model_key: model.discipline for model in models}
    _scope = {r.requirement_key: r.discipline_scope for r in ruleset.requirements}
    findings = [f for f in findings if _discipline[f.model_key] in _scope[f.requirement_key]]

    # Sorted here rather than trusted from the checkers"""
    assert text.count(old) == 1
    p.write_bytes(text.replace(old, new).encode("utf-8"))
print("Option D prototype applied", "(rule only)" if "--no-filter" in sys.argv else "(rule + naive filter)")
```

### `covsum.py`

Summary of a prototype coverage record.

```python
"""Summarise a prototype coverage record: pair states x scope relation, and element reach."""
import csv, sys
from collections import Counter
d = sys.argv[1]
rows = list(csv.DictReader(open(f"{d}/requirement_coverage.csv", encoding="utf-8-sig")))
print(f"pairs: {len(rows)}  (every row carries exactly one state: {all(r['state'][:2] in ('a:','b:','c:','d:','e:') for r in rows)})")
by = Counter((r["project_id"], r["state"]) for r in rows)
for k in sorted(by): print(f"   {k[0]:<22} {k[1]:<26} {by[k]}")
rel = Counter((r["state"], r["scope_relation"]) for r in rows)
print("state x scope_relation:")
for k in sorted(rel): print(f"   {k[0]:<26} {k[1]:<26} {rel[k]}")
odd = [r for r in rows if r["scope_relation"] != "inside" and r["state"] == "e:evaluated"]
print("evaluated although the rule's own discipline_scope does not name the model's discipline:")
for r in odd: print(f"   {r['model_key']:<34} {r['model_discipline']:<11} {r['rule_id']:<7} {r['requirement_id']:<34} scope={r['discipline_scope']:<22} {r['scope_relation']:<25} pass={r['pass']} fail={r['fail']}")
na = [r for r in rows if r["state"] == "a:not-adopted"]
print("not adopted:")
for r in na: print(f"   {r['model_key']:<34} {r['rule_id']:<7} {r['requirement_id']:<30} reason={r['adoption_reason'][:60]}")
els = list(csv.DictReader(open(f"{d}/element_coverage.csv", encoding="utf-8-sig")))
e = Counter((x["project_id"], x["state"]) for x in els)
print("elements:")
for k in sorted(e): print(f"   {k[0]:<22} {k[1]:<12} {e[k]}")
un = Counter((x["model_key"], x["ifc_class"]) for x in els if x["state"] != "reached")
print("unreached by class:", dict(sorted(un.items())))
```

### `touched.py`

Which files a command created or rewrote (mtime + sha256).

```python
"""Record (mtime_ns, sha256) of every file in a tree except .git; diff two records."""
import hashlib, json, os, sys
from pathlib import Path
if sys.argv[1] == "record":
    root = Path(sys.argv[2]); out = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "__pycache__", ".ruff_cache", ".pytest_cache")]
        for f in fn:
            p = Path(dp) / f
            out[p.relative_to(root).as_posix()] = [p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest()]
    Path(sys.argv[3]).write_text(json.dumps(out))
else:
    a = json.loads(Path(sys.argv[2]).read_text()); b = json.loads(Path(sys.argv[3]).read_text())
    for p in sorted(set(a) | set(b)):
        if p not in a: print(f"   created            {p}")
        elif p not in b: print(f"   deleted            {p}")
        elif a[p][1] != b[p][1]: print(f"   rewritten, changed {p}")
        elif a[p][0] != b[p][0]: print(f"   rewritten, same bytes {p}")
```

### `dangling.py`

BCF ReferenceLinks with no matching canonical finding.

```python
"""Count BCF ReferenceLinks whose finding key is absent from canonical findings.csv."""
import csv, re, sys, zipfile
keys = {r["finding_key"] for r in csv.DictReader(open("data/processed/canonical/findings.csv", encoding="utf-8-sig"))}
z = zipfile.ZipFile("reports/bcf/issues.bcf")
links = [m for n in z.namelist() if n.endswith("markup.bcf") for m in re.findall(r"urn:epc-digital-delivery:finding:([0-9a-f-]{36})", z.read(n).decode("utf-8"))]
print(f"   issues.bcf ReferenceLinks: {len(links)}; resolving in findings.csv: {sum(k in keys for k in links)}; dangling: {sum(k not in keys for k in links)}")
```

### `fail_inject.py`

Runs the real CLI with one component made to raise (in-process; edits no file).

```python
"""Run the real CLI with one component made to raise, to observe failure residue.

usage: python fail_inject.py <checker-hvac|exporter-legacy-pbip> <cli args...>
Injection is in-process (monkeypatch); no file in the checkout is edited.
"""
import os, sys
sys.path.insert(0, os.getcwd())
mode, argv = sys.argv[1], sys.argv[2:]
if mode == "checker-hvac":
    from epc_control_tower.checkers import ids_checker as m
    orig = m.IdsChecker._validate_model
    def boom(self, model, context):
        if model.model_key == "hvac":
            raise OSError("injected: model could not be read")
        return orig(self, model, context)
    m.IdsChecker._validate_model = boom
elif mode == "exporter-legacy-pbip":
    from epc_control_tower.exporters import legacy_pbip as m
    def boom(self, bundle, output_root):
        raise ValueError("injected: legacy-pbip could not write")
    m.LegacyPbipAdapter.export = boom
from epc_control_tower.cli import main
raise SystemExit(main(argv))
```

### `adoption_N.toml`

Adoption declaration used for N (counterexample only).

```toml
[adoption]
ruleset_id = "epc-delivery"
ruleset_version = "2.2"

[[adoption.rules]]
rule_id = "R-001"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-002"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-003"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-004A"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-004B"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-005A"
decision = "not-adopted"
reason = "Counterexample only: a project-assumed EPC property set this synthetic project never agreed."

[[adoption.rules]]
rule_id = "R-005B"
decision = "not-adopted"
reason = "Counterexample only: a project-assumed EPC property set this synthetic project never agreed."

[[adoption.rules]]
rule_id = "R-006"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-007"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-008"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-009"
decision = "not-adopted"
reason = "Counterexample only: CCI Construction classification is not a convention of this synthetic project."

[[adoption.rules]]
rule_id = "R-010"
decision = "adopted"
```

### `adoption_N_missing_R010.toml`

The same with R-010 omitted — must refuse.

```toml
[adoption]
ruleset_id = "epc-delivery"
ruleset_version = "2.2"

[[adoption.rules]]
rule_id = "R-001"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-002"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-003"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-004A"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-004B"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-005A"
decision = "not-adopted"
reason = "Counterexample only: a project-assumed EPC property set this synthetic project never agreed."

[[adoption.rules]]
rule_id = "R-005B"
decision = "not-adopted"
reason = "Counterexample only: a project-assumed EPC property set this synthetic project never agreed."

[[adoption.rules]]
rule_id = "R-006"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-007"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-008"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-009"
decision = "not-adopted"
reason = "Counterexample only: CCI Construction classification is not a convention of this synthetic project."
```

### `adoption_all_adopted.toml`

Every rule adopted — used for the SX counterfactuals.

```toml

[adoption]
ruleset_id = "epc-delivery"
ruleset_version = "2.2"

[[adoption.rules]]
rule_id = "R-001"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-002"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-003"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-004A"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-004B"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-005A"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-005B"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-006"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-007"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-008"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-009"
decision = "adopted"

[[adoption.rules]]
rule_id = "R-010"
decision = "adopted"
```
