# PFR-V2B-R6-BPHS-T1R-P2R2 Shared 3-Day Calendar Viewport

## Status

This is a bounded founder-product UI correction. The 14-calendar-day BPHS
research page remains the only backend calculation and cache unit. This change
does not alter the BPHS endpoint, interval boundaries, source provenance,
Tara dependency, or any research guardrail.

## Display contract

The BPHS pane renders one horizontal timeline for all seven categories:

- Muhurta
- Tithi
- Nakshatra
- Yoga
- Karana
- Civil weekday (engineering)
- Tara

The default viewport is three calendar days. The timeline width represents the
complete loaded 14-day half-open range, so each row uses the same time scale.
The category labels remain outside the horizontal scroll container and are
therefore frozen while the timeline moves. Blocks are sized from their exact
interval duration and are clipped by the common viewport at its edges.

The pane shows both identities: the loaded research page and the current BPHS
visible window. Scrolling updates only the visible-window label. It does not
change the Fields research-page index and does not call the BPHS backend. The
existing Previous 14 days, Next 14 days, and Load window containing crosshair
controls remain the only controls that can cause a new research-page request.

## Preserved behavior

The response remains one cached `BPHS_CLASSICAL_CALENDAR_RANGE_V1` result per
Fields research page. Half-open interval geometry is preserved. Tara remains
`DEPENDENCY_NOT_READY`; source and engineering provenance remain unchanged;
`executionAllowed` remains false. No polarity, score, market interpretation,
SBC integration, Auto Suggest, ML, smoothing, or execution path is added.

## Verification target

The focused Fields suite proves that a loaded 14-day response displays three
days by default, scrolling produces no additional BPHS request, all seven rows
share the timeline, and the Tara dependency remains visible. The full frontend
suite and production build are also required before packaging.
