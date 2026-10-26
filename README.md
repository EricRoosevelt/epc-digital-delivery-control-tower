# BIM Doctor — enterprise rules and purpose review

**Bring project rules, review a declared delivery purpose, and trace what changed.**

[中文](README.zh-CN.md) · [Candidate demo and exact-commit evidence](docs/evidence/phase2-candidate/README.md) · [Quick start](#quick-start) · [Windows / Ubuntu CI](https://github.com/EricRoosevelt/epc-digital-delivery-control-tower/actions/workflows/ci.yml?query=branch%3Afeat%2Fdoctor-product-phase1)

BIM Doctor is a personal open-source application for engineers and BIM
coordinators reviewing IFC model exchanges. It runs in a local browser and keeps
project records on that computer. A rule result and a person's engineering
acceptance remain separate decisions.

## What this candidate does

- **Bring and adopt project rules:** import one ZIP containing native TOML rules
  and a purpose manifest. Inspect source, version, applicability, requirements
  and unsupported parts before explicitly adopting an immutable project version.
- **Review a delivery purpose:** choose internal review, tender submission or a
  package-defined handover, select the revision and scope, and read the existing
  Purpose engine's evidence-backed results. Missing coverage, unsupported checks
  and absent evidence remain UNKNOWN; zero FAIL is not a readiness decision.
- **Close the evidence loop:** open a blocker at its rule and exact 3D element,
  record attributable human evidence separately from progress notes, then create
  a successor review. Model, rule, scope, engine and human-evidence changes remain
  distinct; an unverified possible cause stays a hypothesis.
- **Real 3D inspection:** load the bundled public buildingSMART example or one
  IFC file, select a result, and focus or isolate its actual tessellated geometry.
- **Projects and revision rechecks:** save immutable reports and 3D snapshots,
  record an owner/status/note, import a new IFC into the same model slot, compare
  revisions and download a Markdown work brief. Reopen saved evidence after a
  server restart without uploading the source again.
- **Evidence-based comparison:** distinguish passed rechecks, remaining/new
  findings, missing objects, no-longer-applicable checks and unavailable
  comparisons. Deletion, reclassification or a changed rule is not a repair.
- **Local guidance and optional OpenAI advice:** guidance works without an API
  key. Optional generated advice uses the selected finding's text evidence;
  source IFC and meshes are not sent. [AI setup](doctor/README.md#openai-setup).

The four base workspace checks cover air-terminal type (PV-001), readable names,
storey association and file-local GlobalId integrity. PV-001 shares the existing
rule definition and IfcTester predicate with the framework. Name/storey findings
are information prompts, not a count of engineering defects.
Enterprise checks have their own immutable assessment records and do not rewrite
those base reports or their meshes.

In **Projects & rechecks**, open **Project rules**, download the editable public
package, inspect/adopt it and open **Purpose review**. Existing revisions require
an explicit, SHA-matching original IFC attachment for new rule checks. That
source is retained only in the local project library for later rechecks; rules
and source models are not sent to an AI provider. The public package demonstrates
machine-only internal review, tender evidence, and a handover that also needs an
actual counterpart model. [Format and workflow](docs/product/enterprise-purpose.md).

## Quick start

Use **Python 3.14**, **Git** and a browser with WebGL2, ES modules and import maps.
Windows and Ubuntu are the candidate CI platforms. Node.js, Revit and an OpenAI
account are not required to run the application. Keep the complete source checkout:
the framework wheel alone does not contain the browser application and assets.

The candidate is on `feat/doctor-product-phase1`; cloning the default branch may
still give the earlier product until the candidate PR is merged.

**Windows PowerShell**

```powershell
git clone -c core.longpaths=true --branch feat/doctor-product-phase1 https://github.com/EricRoosevelt/epc-digital-delivery-control-tower.git
cd epc-digital-delivery-control-tower
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
$doctorState = Join-Path $env:LOCALAPPDATA 'BIMDoctor\phase2-rc1'
.\.venv\Scripts\python.exe doctor/serve.py --checks-dir "$doctorState"
```

**Ubuntu / Bash**

```bash
git clone --branch feat/doctor-product-phase1 https://github.com/EricRoosevelt/epc-digital-delivery-control-tower.git
cd epc-digital-delivery-control-tower
python3.14 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python doctor/serve.py --checks-dir "$HOME/.local/state/bim-doctor/phase2-rc1"
```

Open **[the 3D workspace](http://127.0.0.1:8765/review.html?lang=en)** and choose
**Load public example**. Save it to a project, then open
**[Projects & rechecks](http://127.0.0.1:8765/projects.html?lang=en)**. Stop with
Ctrl+C and restart using the **same checks directory** to reopen saved revisions.
If the port is occupied, use `--port 8770` and change the browser URL accordingly.

[Step-by-step workflow, backup and troubleshooting](docs/quick-start.md) ·
[Storage and API details](doctor/README.md#projects-and-revision-rechecks)

## Reproduce this version and its demonstration

Run `git rev-parse HEAD` and compare it with `source_sha` in the candidate CI
artifact manifests. For an immutable rerun, use `git checkout <source_sha>` before
installation. Both Windows and Ubuntu jobs run the full checks and a clean
installation/save/restart/restore workflow. Their commit-named artifacts contain
machine results, the current demonstration and its screenshots/checksums.

[Candidate evidence and recording commands](docs/evidence/phase2-candidate/README.md)
explain how to download or regenerate those files. CI results count only when
their head SHA matches the candidate; old green runs do not certify this branch.

## Current limits

This is a local candidate, with no authenticated team assignment, notifications,
automatic source-model editing or project acceptance decision. Cross-revision
pairing currently supports a single IFC file per logical model; public federated
examples can be saved/reopened but are not paired across revisions.

Imports run in a separate process with progress, confirmed cancellation and a
600-second server deadline. Individual browser requests time out after 30 seconds;
status polling can resume without starting another import. Existing results stay
readable during computation. The payload cache is limited to 16 entries / 64 MiB;
saved revisions reload from SQLite. Save work before leaving it: unsaved results
have bounded temporary storage and expire.

The upload limit is not a validated capacity guarantee. A recorded 2,055-mesh,
1.07-million-triangle case took 179.5 seconds under the earlier synchronous API.
One earlier cold 3D failure remains unexplained; request IDs and geometry/viewer
phase diagnostics now support investigation, and recovery paths run in browser CI.
[Measured scope and qualifications](docs/handoffs/model-case.md).
Live OpenAI advice requires the user's own configured account and was not a
prerequisite for the candidate's offline checks or demonstration.

## Earlier work and engineering reference

The [October 13 English recording](docs/evidence/doctor-resume-ui-en-2026-10-13/doctor-live-en.webm)
and [earlier case study](https://app.notion.com/p/3be1cb002005801b8d5dd536615d46f9)
show the previous simulated-handover experience. They remain historical material,
not evidence of the Phase 2 candidate or a source-model repair.

- [Engineering reference](docs/engineering-reference.md) and [candidate decisions](docs/product/phase2-candidate.md).
- [Rule definitions](rules/product-validation/README.md), [rule parity](docs/handoffs/rule-parity.md) and [data formats](docs/data_contract.md).
- [Earlier Power BI / Speckle work](dashboard/README.md).

## Data Source and Attribution

The IFC sample models are taken from the buildingSMART International
[Sample-Test-Files repository](https://github.com/buildingSMART/Sample-Test-Files),
specifically the
[IFC 4 PCERT Sample Scene](https://github.com/buildingSMART/Sample-Test-Files/tree/main/IFC%204.0.2.1%20%28IFC%204%29/PCERT-Sample-Scene).

Files used:

* `Building-Architecture.ifc`
* `Building-Structural.ifc`
* `Building-Hvac.ifc`

A second project uses three further unmodified samples from the same
repository, the
[IFC 4 ISO Spec Reference View 1.2 set](https://github.com/buildingSMART/Sample-Test-Files/tree/cecf656112a54a0d8cdd8b06b9398bfea5163886/IFC%204.0.2.1%20%28IFC%204%29/ISO%20Spec%20-%20ReferenceView_V1.2),
pinned at commit `cecf656112a54a0d8cdd8b06b9398bfea5163886`:

* `wall-with-opening-and-window.ifc`
* `column-straight-rectangle-tessellation.ifc`
* `basin-tessellation.ifc`

Copyright buildingSMART International Ltd.

The sample files are licensed under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

The IDS rules and normalization logic are authored for this portfolio
prototype and are not official buildingSMART delivery requirements.
