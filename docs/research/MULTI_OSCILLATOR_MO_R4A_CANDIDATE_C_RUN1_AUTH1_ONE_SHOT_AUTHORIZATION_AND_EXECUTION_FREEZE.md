# Candidate C RUN1 AUTH1 One-Shot Execution Freeze

## Authorization And Execution Base

- Authorization schema: `MO_R4A_CANDIDATE_C_RUN1_AUTH1_EXTERNAL_AUTHORIZATION_V1`.
- Authorization ID: `MO-R4A-CANDIDATE-C-RUN1-AUTH1-ONE-SHOT-001`.
- The authorization record was external and uncommitted during execution. The exact bytes were copied into the result commit afterward.
- Execution base: `1d884b93ba9f5b619c3b21cdb8d215bf5faefb5b`.
- Run session: `RUN1_R3R3_38e72138c537404baf85ce72fc17f82f`.
- One controller invocation issued one A worker, one B worker, and one V2 comparison. Scientific worker retries: `0`.

## Immutable Results

- A first-result artifact: `D72622AFDA30DC1092D0E96E40714FB1C1B37737E3B8BB8FCCB94DA55FCB0F25`.
- B first-result artifact: `A9B9F19A2868FE85478357A47BB8BB3B1EBBBA84A85CE27D2268DDFD5ACE17C9`.
- V2 first-comparison artifact: `A368D85E9AF89D8C8B3ED07A22357F324497A78C88C5F10FE80894CAF7DDD335`.
- A and B each preserve 5,160 validated rows. V2 projected 5,160 A rows and 5,160 B rows and compared 5,160 semantic rows.
- Comparison terminal: `REAL_SOURCE_REPRODUCTION_SEMANTIC_AGREEMENT`.
- Mismatch records: `0`; mismatch classification occurrences: `0`; class counts: `{}`.
- The comparison binds the exact A and B artifact self-hashes. All three artifact self-hashes reproduce.

## Boundaries

- This is deterministic source-contract reproduction, not market, forecast, polarity, score, or execution validation.
- No market outcome, provider, broker, or Swiss Ephemeris resource was accessed. No post-comparison interpretation was performed.
- The first-result paths are populated and therefore mechanically block replay. No second controller invocation occurred.
- `executionAllowed=false` remains locked.

Next gate: `CENTRAL_REVIEW_CANDIDATE_C_RUN1_AUTH1_FIRST_EXECUTION`.
