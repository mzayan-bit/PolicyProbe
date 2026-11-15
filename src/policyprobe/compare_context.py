"""Print retrieved and full policy context for each edited or added clause."""

import argparse
import json
from pathlib import Path

from .policy import compare_policies
from .retrieval import full_context, related_context, window_conflicts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    full = full_context(args.after, "after")
    reports = []
    for change in compare_policies(args.before, args.after):
        if change.after is None:
            continue
        selected = related_context(full, change.after, args.limit)
        report = {"change": change.kind, "edit": selected[0].citation}
        for label, items in (("retrieved", selected), ("full", full)):
            report[label] = {
                "citations": [item.citation for item in items],
                "body_characters": sum(len(item.clause.text) for item in items),
                "possible_conflicts": [[a.citation, b.citation] for a, b in window_conflicts(items)],
            }
        reports.append(report)
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
