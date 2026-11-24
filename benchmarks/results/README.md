# First pilot run

The boundary baseline executed forty cases across five evaluation scenarios and two scripted targets per scenario. All twenty clean-target cases matched the authored labels. The seeded short-window defect was found in all five scenarios. The summary deduplicates repeated failures using the known single seeded defect per scenario. Clean-target mismatch counts are an engineering check; they do not measure real-world false alarm rates.

Each case executes the requested action in a fresh SQLite ledger. Records include exchanges. Targets implement manually configured pilot policies independently of the scorer's answer file. The boundary baseline exhausts the four-case pool in each scenario.

Run from a clean checkout after installation:

```sh
python -m policyprobe.benchmark_suite benchmarks/v1 --split evaluation --output boundary-run.json
```

Compare verdicts and ledger actions with boundary-v1.json. Elapsed times vary. The saved file contains per-scenario timings and model-call counts; paid API calls were zero. Actual local-model runs for full-policy, retrieval, and adaptive selection remain pending. This result verifies the scripted execution and scoring path and cannot establish an advantage from agentic selection.

The frozen inputs and labels were authored together. External annotation review and evaluation on actual support bots remain pending.
