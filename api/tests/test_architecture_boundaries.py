"""Mechanical checks for the one layering rule import-linter can't express:
adjacency, not just direction. import-linter's layers contract (see
pyproject.toml's [tool.importlinter]) forbids a repository importing a use
case, but it can't see *inside* a repository to catch it calling commit() or
rollback() directly — that's a method call, not an import. This file is the
minimal, intentionally narrow check for exactly that gap.

Enforces 13-transactions.md: "Repositories must never commit()... Repositories
must never rollback()." Transaction ownership belongs exclusively to the use
case that owns the transaction boundary.
"""

import re
from pathlib import Path

import pytest

REPOSITORY_DIRS = sorted(Path(__file__).parent.parent.glob("app/modules/*/repositories"))
FORBIDDEN_CALL = re.compile(r"\.(commit|rollback)\s*\(")


def _repository_source_files() -> list[Path]:
    files: list[Path] = []
    for repo_dir in REPOSITORY_DIRS:
        files.extend(sorted(repo_dir.rglob("*.py")))
    return files


@pytest.mark.parametrize("path", _repository_source_files(), ids=lambda p: str(p))
def test_repository_never_commits_or_rolls_back(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    match = FORBIDDEN_CALL.search(content)
    assert match is None, (
        f"{path} calls `.{match.group(1) if match else ''}(...)` — repositories "
        "must never commit or rollback a transaction; that belongs to the use "
        "case that owns the transaction boundary (13-transactions.md)."
    )


def test_repository_dirs_were_actually_found() -> None:
    """Guards against the parametrize list silently going empty (e.g. a
    folder rename) and the test above passing for the wrong reason —
    vacuously, because it never ran."""
    assert REPOSITORY_DIRS, "No */repositories/ directories found under app/modules/"
    assert _repository_source_files(), "No .py files found in any repositories/ directory"
