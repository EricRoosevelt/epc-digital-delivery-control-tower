# English Doctor UI materials

Captured 2026-10-13 from current main `3108fb10cfe0cd2c3f638331b3c74407193ccff9` (tree `5c8efd336a420e8cd16e96bb0c90dd3c20c993ba`), with `?lang=en` before the route fragment. Doctor code, rules, models and fixtures match accepted UI merge `0b36a2256b16daf0699ab1699d36142e68766c97`; the intervening PR #65 changed documentation/media only. This is a personal open-source preview, not a production deployment or real-project acceptance decision.

| File | Actual English route / content |
| --- | --- |
| [home-en.jpg](home-en.jpg) | `?lang=en`: home and Choose a simulated example |
| [item-blocked-en.jpg](item-blocked-en.jpg) | `?lang=en#/fixture/member-evidence/item/2/2/2`: building element, Room data sheets and equipment schedules, Blocked; source and next action |
| [recheck-en.jpg](recheck-en.jpg) | `?lang=en#/fixture/recheck-requirement-relaxed/recheck/of/schedules-and-room-data-sheets/2/2`: same item, Blocked → Ready; simulated evidence, unchanged model versions and original-condition limit |
| [local-detail-en.jpg](local-detail-en.jpg) | `?lang=en#/local/e7838dad4ac0d3b3/finding/49f98c89-ebf0-5ede-a651-54c38a4ddb75`: real PV-001 FAIL on unchanged public Building-Hvac.ifc, with input identity and product-validation limit |
| [doctor-live-en.webm](doctor-live-en.webm) | 79.754 seconds, 1280×720, silent VP9/WebM: home → catalogue → first result → independent item → Jump to the next step → same-item recheck |

Screenshots are original browser JPEG captures at the default 1280×720 CSS viewport; the raster may omit the browser gutter. There is no relabelling, repainting, compositing or generated UI. The English language toggle retains its native 中文 option label. The screenshot viewport does not show every section of the long pages; captions describe the visible area. All earlier Chinese media stay unchanged in [the previous directory](../doctor-resume-ui-2026-10-13/README.md).

The video records real application operations using 128 fresh browser captures at roughly two frames per second, held during tool gaps and continuously encoded by the installed browser's native MediaRecorder. It is a simple silent operation recording, not a high-frame-rate edited film or an animation of older screenshots. Native decoding was checked at 0, 30 and 78 seconds. Media bytes and SHA-256 are in [manifest.json](manifest.json).

The handover record is simulated. Handling teams are example settings and nobody is assigned. The recheck's new evidence is marked Simulated check result; neither model was reissued or edited. Ready holds for this one item, this work and the listed model versions, and does not mean the whole handover is complete. A changed conclusion does not mean the original condition is met. No Revit operation, model repair or real delivery judgement is demonstrated.

The local screenshot uses a real upload/plan/check API run against the unchanged public HVAC model, producing 2 FAIL under product-validation 1.0 / PV-001. The browser file chooser did not establish a selected file in this material session; this image does not claim a successful UI upload. It opens the real finished record in English. There is no fake response or synthetic input. Its visible area contains no machine directory, account, private model or private case identifier. Raw API evidence with machine directories stays local and is not included. The video contains only the example path.

Copyright buildingSMART International Ltd. IFC sample data comes from [Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files), IFC 4 PCERT Sample Scene, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Input IFC data is unchanged. The root README's Data Source and Attribution block remains. A later software change requires review or recapture of affected media before reuse; this material date is not a release/tag.
