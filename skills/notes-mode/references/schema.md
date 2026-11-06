# Note Schema

One note is one row. Keep it terse — the ledger is re-read, so every token recurs.

## Row

```
ID        | N0NN
STATUS    | ACTIVE | SUPERSEDED | REFUTED | ARCHIVED
CLAIM     | one sentence, imperative or declarative
SCOPE     | files / module / subsystem this governs
EVIDENCE  | test name, command, file:line, log excerpt
RATIONALE | why it matters — the part a summary drops
SUPERSEDES| prior note ID this replaces, if any
```

There is no DATE field. Provenance comes from `git log` on the ledger.

## STATUS, exactly one value

| Value | Meaning |
|---|---|
| ACTIVE | believed true and currently load-bearing |
| SUPERSEDED | was true, replaced by a later note — keep for history |
| REFUTED | proven false — keep it so nobody retries |
| ARCHIVED | no longer relevant to current work |

## Worked rows

```
N014 | ACTIVE | resolve_incoming() lowercases and truncates county keys
     | qc_excel.py incoming-file resolution
     | reproduced with Polola sheet1 and RUSK sheet3 fixtures
     | Producer writes short county keys, not full production stems; any fix
       must normalize BOTH key length and case
     | supersedes N009

N015 | REFUTED | Fuzzy stem matching alone fixes the batch failure
     | qc_excel.py merge pipeline
     | Both mismatches present; key truncation fails even when case matches
     | Prevents future attempts at a case-only fix
```

## Sharding

One file per SCOPE under `ledger/`, named for the module. `ledger/INDEX.md` maps scope to file and stays under ~25 lines. When ACTIVE notes across all shards exceed ~60, split the busiest shard; when a whole shard has gone REFUTED/SUPERSEDED, move it to `ledger/archive/`.

A single flat ledger file cannot be filtered without being read, and read cost is the entire problem this protocol exists to manage.
