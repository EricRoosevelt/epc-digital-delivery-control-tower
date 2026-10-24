# First product increment: actual browser evidence

Captured on 2026-10-24 from the local server and the code in this increment.
All IFC content shown is the unmodified public buildingSMART PCERT sample
(CC BY 4.0, buildingSMART International Ltd.). There are no private project files,
credentials, generated mock models or simulated AI answers in these screenshots.

`tests/doctor_review.browser.cjs` captures this set against a running server.
`review-browser.json` records the exercised paths and page-error result. The final
script returned `passed: true` and `errors: []`. Its one deliberate HTTP 503 is a
transport recovery exercise; the normal model/check/geometry data is real.

| Image | What it verifies |
| --- | --- |
| `review-en-1440.png` | Loaded three-model workspace at 1440×1000, linked selection, actions visible in the first desktop viewport. |
| `review-en-isolated.png` | The selected actual mesh isolated in 3D. |
| `review-en-no-geometry.png` | An element without a representation keeps its evidence; locate controls are disabled. |
| `review-en-information-only-import.png` | An Architecture upload with information prompts opens a useful INFO list and matching selection. |
| `review-zh-390-top.png` | Chinese import/example controls and overview at 390×844. |
| `review-zh-390-viewport.png` | The real mobile WebGL view and named camera controls. |
| `review-zh-390-advice.png` | Chinese local guidance with concrete action and verification steps. |

PM inspected the desktop and mobile viewport/advice screenshots and corrected
the initially buried next actions. These captures support layout and observed
interaction findings; they do not establish physical-device, screen-reader or
full accessibility certification. `premium-audit.json` is the separate static
design-context audit, not a substitute for these browser observations.
