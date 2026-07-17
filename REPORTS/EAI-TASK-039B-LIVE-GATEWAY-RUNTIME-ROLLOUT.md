# EAI-TASK-039B — Corrected two-label queue eligibility evidence

## Status

Ready for PM review. This correction replaces the earlier pm:ready-only search evidence with a real queue-eligibility check that requires both `pm:ready` and `hermes:ready`, plus a one-label negative control.

## Scope

Keep the queue-selection evidence reviewable in GitHub and capture the required artifact trail for issue #71.

## Published implementation

The reviewable implementation remains on the fork branch:

- branch: `eai-task-039b-review`
- PR: `https://github.com/moh0709/hermes-agent/pull/1`
- current reviewable head SHA: `19ba1ee6f62cfea0b39afa62ee87e8285d0d8353`

## Queue eligibility evidence

Disposable live controls were created for the corrected test and then cleaned up after capture:

- positive control: issue `#73` — `EAI-TASK-039B disposable positive control`
  - labels: `pm:ready`, `hermes:ready`
- negative control: issue `#74` — `EAI-TASK-039B disposable negative control`
  - labels: `pm:ready`

### Two-label eligibility query

Command:

```bash
gh issue list --repo moh0709/everythingAI --state open --label pm:ready --label hermes:ready --json number,title --jq '.[] | {number,title}'
```

Observed result:

```json
{"number":73,"title":"EAI-TASK-039B disposable positive control"}
{"number":71,"title":"EAI-TASK-039B: Deploy runtime-mode routing to live Hermes gateway"}
```

This proves the two-label queue candidate set includes the positive control and excludes the one-label negative control `#74`.

### One-label negative control query

Command:

```bash
gh issue list --repo moh0709/everythingAI --state open --label pm:ready --json number,title --jq '.[] | {number,title}'
```

Observed result included the negative control:

```json
{"number":74,"title":"EAI-TASK-039B disposable negative control"}
```

It also returned other pm:ready items, which is expected; the point of the negative control is that it appears in the one-label queue but not in the two-label queue.

## Cleanup

The disposable controls were closed after validation:

- issue `#73` closed
- issue `#74` closed

## Validation executed

- `gh issue list --repo moh0709/everythingAI --state open --label pm:ready --label hermes:ready --json number,title --jq '.[] | {number,title}'`
- `gh issue list --repo moh0709/everythingAI --state open --label pm:ready --json number,title --jq '.[] | {number,title}'`
- `gh issue view 74 --repo moh0709/everythingAI --json number,labels,title --jq '{number,title,labels:[.labels[].name]}'`
- `git diff --check`

## Remaining limitations

- This correction is evidence-only; it does not change runtime code.
- The earlier pm:ready-only discovery run is superseded by this label-eligibility proof.

## Rollback procedure

No code rollback is required for this correction. To discard the evidence-only commit, revert the commit that updates these artifacts.
