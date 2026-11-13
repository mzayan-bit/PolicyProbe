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
