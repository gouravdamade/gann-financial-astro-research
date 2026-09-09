# MO-R4A-P0 Non-Expert Explanation Contract

## Objective

The product must let a non-expert understand the current state without asking
them to derive Sanskrit-source doctrine, relationship tables, bala, Vedha,
Latta, Argha, or a market sign. An explanation must keep astronomy, source
doctrine, astrology interpretation, market bridge, currency-side state, and
financial validation visibly separate.

This is an explanation contract and synthetic-test reference. It adds no UI,
does not classify a real April event, and does not introduce a market rule.

## Required Explanation Fields

Every future machine interpretation packet exposes these fields:

| Question for the reader | Field | Rule |
| --- | --- | --- |
| What is happening? | `headline` | State the current currency-side condition plainly. |
| Why does it matter? | `why` | State the evidence boundary in ordinary language. |
| Which part is classical? | `classicalEvidence` | Identify source coverage, not a financial conclusion. |
| Which part is experimental? | `experimentalStatus` | Identify an explicit bridge, if one exists. |
| What is unknown? | `unknowns` | Keep missing operator/precedence dependencies visible. |
| Is it financially validated? | `financialValidation` | Present `NOT_FINANCIALLY_VALIDATED` until a separately authorized study changes it. |

## Required Plain-Language Outcomes

### Source-Supported Astrology, No Market Bridge

```text
Currency direction: unknown

Why:
Direction unknown because the astrology is source-supported but no approved
USD/JPY market bridge exists.

Classical evidence:
Source-bound astrology operator coverage is available.

Experimental status:
No authorized market bridge.

Financial validation:
Not yet established.
```

This is the expected outcome when a source operator closes an astrology state
but neither a source-backed nor experimental currency bridge is approved.

### Explicit Experimental Bridge

```text
Currency pressure: adverse

Why:
Experimental adverse interpretation. Classical evidence supports the astrology
condition; the currency mapping is experimental and not yet financially
validated.

Classical evidence:
Source-bound astrology operator coverage is available.

Experimental status:
Versioned experimental market hypothesis.

Financial validation:
Not yet established.
```

This is permitted only for a future, versioned, exact-input hypothesis that is
explicitly approved for a blinded test. It is not source-certified financial
doctrine and it carries neither a signed unit nor magnitude.

### Conflicting Source Operators

```text
Currency direction: unknown

Why:
Mixed interpretation because two applicable operators conflict and no approved
precedence rule exists.

Unknowns:
No approved astrological precedence contract.
```

`MIXED` and `UNKNOWN_MORE_EVIDENCE_REQUIRED` remain categorical and
non-numeric. They are never silently converted to neutral or zero.

### Missing Source Dependency

```text
Currency direction: unknown

Why:
Direction unknown because a required astrology operator is not yet available or
remains unresolved.
```

## Required Product Labels

When shown to a user, an interpretation must make all applicable labels
visible:

- `SOURCE_CERTIFIED`, `EXPERIMENTAL_PROFILED`, or `EXPLORATORY_UNSIGNED`;
- source coverage state;
- market-bridge state;
- financial validation state;
- `MAGNITUDE_NOT_CONFIGURED`; and
- `executionAllowed = false`.

## Prohibited Presentation

The explanation layer must not:

- state or imply a source-certified financial forecast where the bridge is
  experimental or absent;
- call an astrology state a USD/JPY result without an approved bridge;
- turn a bala measurement into a size, confidence score, or oscillator weight;
- reduce `MIXED` or `UNKNOWN` to a numeric zero;
- render a signed side wave or pair resultant;
- conceal unresolved dependencies behind an affirmative headline; or
- display an order, execution, Auto Suggest, ML, or MT5 action.

## Synthetic-Test Boundary

The callable MO-R4A-P0 interpreter is intentionally limited to identifiers
starting `SYNTHETIC_`. The examples above are contract text, not a rule for any
real canonical event. Real April identities currently use the separate
identity-only coverage report and remain directionally unknown.
