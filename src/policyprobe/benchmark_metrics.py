"""Summarize known seeded defects without counting repeated failures twice."""


def summarize(runs):
    summaries = []
    for run in runs:
        failures = [i for i, row in enumerate(run["attempts"], 1) if row["passed"] is False]
        defect = run.get("seeded_defect")
        summaries.append({
            "scenario": run["scenario"], "target": run["target"],
            "method": run["method"], "attempts": len(run["attempts"]),
            "incomplete": sum(row["passed"] is None for row in run["attempts"]),
            "failing_cases": len({row["case_id"] for row in run["attempts"] if row["passed"] is False}),
            "distinct_seeded_defects": int(bool(failures) and defect is not None),
            "clean_target_mismatches": len(failures) if defect is None else 0,
            "first_failing_attempt": failures[0] if failures else None,
            "model_calls": run["model_calls"],
        })
    return summaries
