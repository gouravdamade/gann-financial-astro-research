# ADR-0017: Product-First Recovery Scope

- Status: active for the product-first branch
- Date: 2026-08-01
- Branch: `product-first-sbc-phase-lab`

## Context

The desktop application already contains source-profiled SBC facts, a Chakra
board, linked audit projections, and a fixed 0/pi visualization. They are
useful ingredients, but the visible product is fragmented by research and
certification controls that are not part of a founder's daily workflow.

The Product-First Codex Recovery Directive defines a bounded recovery path:
deliver a usable Windows SBC and phase-analysis beta before returning to
certification expansion or prospective validation.

## Decision

1. This branch implements only PFR-1 through PFR-7 in the supplied directive,
   sequentially.
2. Existing safety locks remain unchanged: the product is read-only,
   timestamp-safe, no-lookahead, non-voting, non-financially-validated, and
   execution-disabled.
3. The existing Chakra board, Vedha ledger, and fixed 0/pi projection are
   reused. The product must not create a parallel calculation engine merely to
   present them.
4. New source-certification, reviewer, signature, authority, governance,
   speculative research, Auto Suggest, ML, shadow-validation, live-inference,
   trade, and MT5 work is outside this branch.
5. The founder-facing workspace hides parked certification workflow from the
   normal product path while preserving current implementation and safety
   behavior.
6. Work stops after the PFR-7 Windows beta and native founder acceptance
   checkpoint. Any later source certification or financial validation requires
   a new explicit decision.

## Consequences

- Product progress is measured by a coherent Windows workflow, not by more
  research controls.
- Existing experimental labeling and zero execution authority remain visible.
- The branch may improve presentation and interaction, but does not promote
  any SBC or phase output to an advice, prediction, or order signal.
