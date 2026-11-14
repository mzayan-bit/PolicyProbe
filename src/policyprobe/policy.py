"""Read Markdown policies and keep line references for each version."""

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re


@dataclass(frozen=True)
class Clause:
    document: str
    headings: tuple[str, ...]
    occurrence: int
    line: int
    text: str


    @property
    def date_boundaries(self) -> list[tuple[str, date]]:
        """Return explicit timing phrases and dates without inferring applicability."""
        pattern = (
            r"\b(on or after|on or before|before|after|effective(?: from)?|starting|from)"
            r"[:\s]+(\d{4}-\d{2}-\d{2}|[A-Za-z]+ \d{1,2}, \d{4})\b"
        )
        boundaries = []
        for phrase, value in re.findall(pattern, self.text, flags=re.IGNORECASE):
            try:
                day = (date.fromisoformat(value) if value[0].isdigit()
                       else datetime.strptime(value, "%B %d, %Y").date())
            except ValueError:
                continue
            boundaries.append((phrase.lower(), day))
        return boundaries


def read_policy(folder: Path) -> dict[tuple, Clause]:
    if not folder.is_dir():
        raise NotADirectoryError(folder)
    clauses = {}
    for path in sorted(folder.rglob("*.md")):
        document = path.relative_to(folder).as_posix()
        headings = []
        body = []
        occurrences = {}
        line = 1

        def save():
            text = "\n".join(body).strip()
            if text:
                names = tuple(name for _, name in headings)
                occurrence = occurrences.get(names, 0) + 1
                occurrences[names] = occurrence
                key = (document, names, occurrence)
                clauses[key] = Clause(*key, line, text)

        fence = ""
        for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = raw.lstrip()
            if fence:
                body.append(raw)
                if re.fullmatch(re.escape(fence[0]) + "{" + str(len(fence)) + ",}", stripped.rstrip()):
                    fence = ""
                continue
            opening = re.match(r"^(`{3,}|~{3,})", stripped)
            if opening:
                fence = opening[1]
            heading = re.fullmatch(r" {0,3}(#{1,6})[ \t]+(.+?)\s*", raw)
            if not heading:
                body.append(raw)
                continue
            save()
            level = len(heading[1])
            while headings and headings[-1][0] >= level:
                headings.pop()
            headings.append((level, heading[2]))
            body = []
            line = number
        save()
    return clauses


@dataclass(frozen=True)
class Change:
    kind: str
    before: Clause | None
    after: Clause | None


def _comparison_text(text: str) -> str:
    """Normalize prose wrapping and a narrowly scoped rewrite from the return policy."""
    if any(line.lstrip().startswith(("`", "~", "|", "-", "*", ">"))
           or line.startswith("    ") for line in text.splitlines()):
        return text
    wrapped = " ".join(text.split())
    return re.sub(r"\bmay be returned within (?=\d+ calendar days of purchase\b)",
                  "can be returned within ", wrapped)


def compare_policies(before: Path, after: Path) -> list[Change]:
    old = read_policy(before)
    new = read_policy(after)
    changes = []
    for key in sorted(old.keys() | new.keys()):
        previous = old.get(key)
        current = new.get(key)
        if previous is None:
            kind = "added"
        elif current is None:
            kind = "removed"
        elif previous.text != current.text:
            if _comparison_text(previous.text) == _comparison_text(current.text):
                kind = "wording"
            else:
                kind = "edited"
        else:
            continue
        changes.append(Change(kind, previous, current))
    return changes
