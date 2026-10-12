# New Doctor UI materials

Captured 2026-10-13 from accepted merge `0b36a2256b16daf0699ab1699d36142e68766c97` (tree `6f31cf3948441ad1d5e721223c9559b23c1b3fc6`). Its tree matches reviewed PR #64 head `de6940eb3c65b6e7a7af8872ffd37cc98018551a`. This is a local preview of a personal open-source project, not a production deployment or an acceptance decision for a real project.

| File | Actual route / content |
| --- | --- |
| home-zh.jpg | Chinese home, the recommended example entry and separate local IFC4 path |
| item-blocked-zh.jpg | `#/fixture/member-evidence/item/2/2/2`: building element, room data sheets and equipment schedules, blocked; conclusion and next action with source and assignment limits |
| local-detail-zh.jpg | `#/local/e7838dad4ac0d3b3/finding/49f98c89-ebf0-5ede-a651-54c38a4ddb75`: real PV-001 result over unchanged public Building-Hvac.ifc; FAIL with its product-validation limits and real input identity |
| doctor-live.webm | 79.772 seconds, 1280×900, silent VP9/WebM. Live home → catalogue → first check → independent item → next-step jump → same-item recheck |

Screenshots are original browser JPEG captures. Requested CSS viewport was 1280×900; the tool's raster captures may omit its gutter. Nothing was painted, composited or relabelled. No local record directory, account UI, private model or private case identifier appears in the accepted images or recording. The older README capture remains in its original directory.

The video records operations on the real application. The included handover scenario is simulated: team arrangements and human determinations are example settings. Neither model is reissued or edited; the changed conclusion is not proof that the original closure condition has been met. No Revit edit, automatic assignment or model repair is demonstrated. Capture was roughly two fresh browser frames per second, with the current screen held during tool gaps; native encoding is continuous. It is a simple operation recording, not a high-frame-rate edited film, and has no narration.

The local screenshot comes from the candidate's real upload/plan/check API over the unchanged public HVAC file, producing 2 FAIL. This material session's browser file chooser did not complete, so it does not claim a successful UI upload in this capture. It opens the real finished record; there is no fake envelope, synthetic input or altered model. The recording itself contains only the example path and never the local storage-directory panel.

Media hashes, source SHA and the actual video duration are in [manifest.json](manifest.json). The WebM was decoded and checked at its opening, action section and recheck ending. These files identify the accepted UI baseline; no release/tag is implied. If the frozen software SHA changes, recapture/recheck affected material before reuse.

Copyright buildingSMART International Ltd. Sample IFC data comes from [Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files), IFC 4 PCERT Sample Scene, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). IFC input data is unchanged. See the root README's Data Source and Attribution section.
