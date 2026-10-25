# Phase 2 candidate: reproducible source and evidence

The candidate is named **Phase 2 RC1**. Its immutable identity is the complete
Git commit SHA recorded by the CI job, clean-install result and demonstration
manifest. The Python framework package version and the published data-contract
version are separate identities; neither is changed just to label this candidate.

## Delivery decisions

- Distribute the complete Git checkout. The Python wheel currently packages the
  framework, not the browser application and its rules, samples and static assets.
- Verify Python 3.14 on Windows and Ubuntu. A fresh virtual environment installs
  the checkout, starts a new loopback server with a new external data directory,
  saves project evidence and restores it after an actual process restart.
- Keep the existing full regression, IDS audit, published-artifact determinism,
  dashboard and dependency checks. Candidate verification supplements those gates.
- Record the current public 3D and revision workflow from the same CI commit,
  using pinned Playwright tooling. Public sample geometry and an explicitly
  synthetic editable model are sufficient; no private model, account, API key,
  Revit installation or pre-existing project database is required.
- Upload generated video, screenshots, manifests and clean-install JSON as
  commit-named CI artifacts. Do not commit a final recording back into its own
  source: that would change the SHA the recording claims to demonstrate.
- Treat the October 13 recordings and earlier phase screenshots as historical
  evidence. The README points readers to current candidate instructions and
  exact-SHA CI artifacts rather than presenting older media as this candidate.

## Verification contract

- Candidate source and Windows/Ubuntu CI checks refer to the final PR head.
- Both platforms run the clean-install/save/restart/restore verification.
- Current demonstration and manifests identify that same source SHA.
- README, quick start, persistence instructions and limits match the product.
- A reviewable PR contains source, commands, limitations and linked CI evidence.

Execution results belong in the commit-named CI artifact and PR description.
Updating this source document after a successful run would create a different
commit that needs its own evidence.

Delivery is a reviewable PR and commit-named CI artifacts. This candidate is not
a formal tagged release; main-branch integration and release publication remain
separate maintainer decisions.
