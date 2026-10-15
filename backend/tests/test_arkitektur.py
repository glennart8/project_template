"""Arkitekturregler som låses med test i stället för att bara stå i CLAUDE.md."""

from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


def _repository_files() -> list[Path]:
    return [
        path
        for path in BACKEND.rglob("*.py")
        if ".venv" not in path.parts and "repositories" in path.parts
    ]


def test_repositories_committar_aldrig() -> None:
    # Ett flöde som skriver flera rader ska lyckas eller misslyckas helt.
    # Därför committar servicen, aldrig ett repository.
    offenders = [p for p in _repository_files() if ".commit(" in p.read_text(encoding="utf-8")]
    assert offenders == []
