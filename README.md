# PolicyProbe

PolicyProbe tests whether customer-support agents apply a changed store policy to the right orders. The first fixture models a return window shortened from 30 to 14 days while older purchases retain their original terms.

## Research question

With a fixed conversation budget, does choosing the next shopper in response to earlier outcomes uncover more distinct policy failures than generating every shopper up front? The planned comparison includes handwritten boundary tests, full-policy generation, fixed retrieval, and adaptive retrieval. The scorer will check order records independently from the shopper.

## First checkpoint

Install the package and test extra from a checkout using Python 3.11 or newer:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install '.[test]'
python -m pytest -q
```

The initial test exercises a handwritten retail reference rule and an isolated SQLite store. It requires no model credentials. The interactive shopper, replay CLI, and research results are later milestones.

## Run the offline demo

After installation, run:

```sh
python -m policyprobe.demo
python -m policyprobe.demo --json > orders.json
```

Both shoppers request a return on November 20. The correct shop refunds the October 31 order under the earlier policy and declines the November 1 order. The flawed shop declines both. Look for the single failing row for the October 31 shopper. The JSON output includes the support reply, applicable clause, and refund status before and after each request. Each run uses fresh test orders.

These shoppers and bots are scripted. The expected failure is part of the demonstration. To try the demo with a support team, use the [interview guide](docs/pilot.md).

## Inspect a policy edit

From the repository root after installation:

```python
from pathlib import Path
from policyprobe.policy import compare_policies

root = Path("examples/returns")
for change in compare_policies(root / "before", root / "after"):
    clause = change.after or change.before
    print(change.kind, clause.document, clause.line, clause.headings, clause.date_boundaries)
```

The example reports an added exception and an edited return window. Sections are matched by document path, Markdown heading path, and occurrence. Renames appear as removal and addition. Explicit timing phrases retain their dates. The wording label covers simple prose wrapping and a narrow return-policy paraphrase. Other edits remain available for review.

## Find exceptions in other documents

The gift-order example changes the standard return window to 14 days. A separate gift-receipt policy keeps its 30-day window. Compare the context retrieved for the edit with every section in the new snapshot:

```sh
python -m policyprobe.compare_context examples/gift-orders/before examples/gift-orders/after --limit 2
```

The first citation identifies the edit. The second points to the unchanged gift exception. Full context also includes an unrelated delivery rule. Both outputs count body characters and preserve document and line references. The search ranks shared words; an exception with entirely different vocabulary can be missed. Conflict flags cover matching headings and wording with a single differing day count. Reviewing the cited clauses establishes whether their scopes actually overlap.

## Generate shoppers around a policy change

```sh
python -m policyprobe.shopper_preview --cutoff 2026-11-01 --requested-on 2026-11-20
```

This prints three order records purchased on October 31, November 1, and November 2. Each shopper requests a return on November 20. Supply a request date on or after the last purchase. The simulated dates and order IDs stay the same on replay, and the inputs carry no answer key. Use `shopper_store(order)` to run each generated shopper in a fresh SQLite session.

## Run against a local staging bot

Run `python -m policyprobe.demo --target-url http://127.0.0.1:9000 --json` with a staging server implementing this contract. Each shopper gets a fresh client-generated session ID. The client sends two messages, first requesting a return and then supplying its order ID.

| Method and path | Server behavior |
| --- | --- |
| PUT /sessions/{id} | Create an isolated test order from order_id, purchased_on, and requested_on. Return an empty JSON object. |
| POST /sessions/{id}/messages | Accept a JSON message string field, advance the conversation, and return a reply string field. |
| GET /sessions/{id}/order | Read the underlying order and return a boolean refunded field. |
| DELETE /sessions/{id} | Discard the session. Accept repeated cleanup and unknown IDs. |

The client uses a five-second network timeout per operation. An incomplete conversation includes the recorded turns and an error in the JSON report and exits with status 2. The runner attempts cleanup even if a request fails. Staging servers should expire abandoned sessions if cleanup cannot reach them.
