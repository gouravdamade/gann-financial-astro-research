# PFR-V2B-R6-SBC-TN1R1 - Trailokya Inspector Viewport Scroll Repair

## Scope

TN1R1 is a product-layout correction for the native Trailokya 1972 source
inspector. It does not change the source contract, board geometry, target rows,
ray semantics, astronomy, Fields, polarity, score, Auto Suggest, ML, MT5, or
execution behavior.

## Defect and root cause

The native Trailokya branch returned its inspector directly from the Chakra
surface. The generic Chakra workspace owns a bounded `minmax(0, 1fr)` grid track
and the desktop shell is intentionally `overflow: hidden`; consequently the
native inspector's content extended below the visible surface without a scroll
owner. The board could render while the lower rows, audit panels, and footer
were clipped.

## Bounded correction

`ChakraLabWorkspace` now wraps only the native Trailokya inspector in one
dedicated `trailokya-workspace-scroll` region. The region is the sole vertical
scroll owner for this branch, occupies the available Chakra content track, and
is keyboard-focusable (`tabIndex=0`) for PageUp/PageDown/Home/End navigation.
The existing board and inspector components remain reusable and their source
data is unchanged. No nested scroll container was added around the complete
inspector.

The wrapper preserves:

- EAST at the top, WEST at the bottom, NORTH on the left and SOUTH on the right;
- the source-derived 81-cell board and 28-row enumerated target authority;
- explicit unknown and ambiguous states;
- profile isolation when switching to Agarwal or another Chakra profile;
- all existing read-only and execution locks.

## Source-browser implementer evidence

The source UI was opened at `http://127.0.0.1:5174/` and inspected at
1280x720. After selecting Trailokya 1972 Research:

| Measurement | Result |
|---|---:|
| Scroll host client height | 650px |
| Scroll host content height | 1472px |
| Scroll behavior | `overflow-y: auto` |
| Trailokya grid cells | 81 |
| Bottom reach | WEST row, audit footer and status footer visible |

The top and bottom states were inspected separately. Switching
Trailokya -> Agarwal removed the Trailokya scroll host; switching back restored
the host and all 81 cells. These are implementer checks, not founder acceptance.

The requested 1920x1080, 1600x900 and 1366x768 physical packaged-window
checks remain part of the founder inspection checklist. They are not claimed
as completed by this source-browser measurement.

## Verification

The focused frontend test covers the visible scroll region, its keyboard
focusability, the 81-cell board containment and the no-range-request boundary.
The full frontend, backend, Rust and packaging results are recorded in the
immutable TN1R1 founder-candidate report after the clean build.

## Safety boundary

TN1R1 does not activate a Trailokya range compiler, directional field, market
interpretation, score, polarity, Auto Suggest, ML, MT5 or execution. The
Trailokya profile remains read-only and `executionAllowed=false`.
