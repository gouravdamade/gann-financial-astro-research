# PFR-V2B-R6-N1 Repository Hygiene Report

## Measured state

The tracked checkout is approximately 1.09 GiB. `CURRENT_PROJECT_HANDOFF.md`
is approximately 734 KiB and 10,488 lines. The dominant tracked artifacts are
historical Codex backup SQLite/WAL files, large rollout snapshots, research
CSVs, and historical visual evidence.

| Artifact class | Observed size | Runtime dependency | Recommendation |
| --- | ---: | --- | --- |
| `chat_session_backups/**/logs_2.sqlite` and WAL files | up to about 50 MiB each | none | historical provenance; migrate to a separate archive/release repository after a founder-approved retention plan |
| research result CSVs | about 10-16 MiB each | research-only | keep immutable datasets under an explicit archive manifest; do not delete automatically |
| `gann_aspect_annotations*.sqlite` | about 10 MiB | founder review data | retain locally; do not modify or migrate automatically |
| historical screenshot/PDF evidence | varied | no product runtime dependency | retain while source and validation gates rely on them; archive later with checksums |
| `CURRENT_PROJECT_HANDOFF.md` | 734 KiB | recovery context | split only under a separate archival milestone; preserve immutable history and leave a concise operational front section |

## N1 decision

No historical data was deleted or moved. The founder's active worktree is
dirty with live databases/logs/release material and was preserved. N1 used a
new clean worktree at `D:\PycharmProjects-n1`.

## Safe future migration plan

1. Create a checksum manifest for each backup collection.
2. Copy immutable backup and visual evidence to a D: archive location or
   separate archive repository.
3. Verify hashes and recovery instructions before removing only duplicated Git
   history, with founder approval.
4. Replace the active handoff's old body with links to archived milestone
   documents only after a full recovery drill.
