# Candidate C RUN1-R2 Isolated Runtime Execution Wiring Freeze

## Scope

RUN1-R2 freezes engineering infrastructure only. It does not execute the 645
real events, create raw A/B results, perform a real V2 comparison, read market
or outcome data, access a provider or Swiss Ephemeris, or authorize execution.

## Topology

`controller_r2` owns frozen-input validation, adapter orchestration, canonical
IPC, ticket issuance, subprocess launch, response validation, and future
artifact writing. It does not import Evaluator A or B scientific modules on
the execution path.

Each worker is launched as `python -I -B` and runs one complete chain in one
fresh PID: verify its clean detached root Git identity and protected bytes,
reject protected bytecode and preload contamination, isolate `sys.path`, import
from the designated root, verify every imported `__file__`, reverify bytes, and
only then invoke the frozen scientific functions. A and B have separate roots;
V2 has a third root.

The historical evaluator code has separately frozen source-input artifacts.
The worker accepts only an independently verified source-input snapshot for
its contract loader; code execution remains exclusively from the designated
historical code root. The loader validates those source-input bytes itself.

## V2 Trace

The normal V2 comparator import loads 18 project files: the Candidate C package
initializer; comparator package initializer, adapters, canonical, comparator,
fixtures, models, and projection; and the static A/B package, canonical,
contract-loader, evaluator, and schema/model dependencies. RUN1-R2 protects all
18 rather than treating `projection.py` alone as sufficient.

## Fixed Contract

- Runtime manifest: `0BDCC99821D767A40718C342F73737210483850D54F8CB404B7CCE178C2F273E`
- IPC contract: `D80E9FE7E3FCF072BB5FC6CD2B8675082A3BF9A577970FCA773AD3E35AC0E5D6`
- Worker ticket contract: `BC935E2C072BB91936BD109A6B9AD5603141CA2FF2AEEB261C5A4937239FF358`
- Execution wiring: `B0291A04CA909F0536F56DA0CE46D1E96B28BE91FC005416694BFE1AE09DF4ED`
- Implementation source aggregate: `250D1CBBBB885C973C2885C4E51EDAE2CDEC67AC8222C4816FDAABE89A3DBC0C`

Only ephemeral HMAC material may authorize a clearly fake `FAKE_REAL_RUN1_`
event probe. Production ticket issuance is disabled, each ticket binds role,
session, request, event identity, payload hash, population identity, and target
implementation commit, and retries are frozen at zero.

## Result Boundary

The 645-event population and 5,160-row universe were read only for identity,
structure, adapter, denylist, authorization, and execution-wiring validation.
They were not evaluated. No real output or real comparison exists.

`REAL_CANDIDATE_C_RUN_AUTHORIZED=false` and `executionAllowed=false` remain
active. Candidate C remains unsigned: no polarity, score, magnitude, wave,
forecast, Fields state, Auto Suggest, ML, MT5, broker, or order behavior exists.

Next gate: `CENTRAL_REVIEW_CANDIDATE_C_RUN1_R2_ISOLATED_RUNTIME_EXECUTION_WIRING`.
