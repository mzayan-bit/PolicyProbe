"""Publish complete JSON reports without replacing an existing destination."""

import json
import os
from pathlib import Path
import tempfile


def write_report(path: Path, payload) -> None:
    # Serialize before touching the filesystem so invalid data leaves no artifact.
    encoded = json.dumps(payload, indent=2) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=path.parent, delete=False) as file:
            temporary = Path(file.name)
            file.write(encoded)
            file.flush()
            os.fsync(file.fileno())
        # A same-filesystem hard link publishes complete bytes exclusively.
        os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
