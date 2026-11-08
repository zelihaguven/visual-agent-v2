"""Modül sınırları: kodun nereye gittiği yapıdan okunabilsin diye test edilir."""

import ast
from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent.parent / "src" / "visual_agent"
LAYERS = {
    "domain",
    "ask",
    "conversation",
    "retrieval",
    "generation",
    "verification",
    "ingest",
    "catalog",
    "voice",
}
FORBIDDEN = {"domain": LAYERS - {"domain"}, "ingest": {"ask"}, "ask": {"ingest"}}


def _absolute_targets(node: ast.Import | ast.ImportFrom) -> list[tuple[str, ...]]:
    if isinstance(node, ast.Import):
        return [tuple(alias.name.split(".")) for alias in node.names]
    module = tuple(node.module.split(".")) if node.module else ()
    return [(*module, alias.name) for alias in node.names]


def _relative_targets(node: ast.ImportFrom, package: tuple[str, ...]) -> list[tuple[str, ...]]:
    base = package[: len(package) - (node.level - 1)]
    module = tuple(node.module.split(".")) if node.module else ()
    return [(*base, *module, alias.name) for alias in node.names]


def imported_layers(path: Path, root: Path) -> set[str]:
    """Bir dosyanın import ettiği paket içi katmanlar."""
    package = path.relative_to(root).parts[:-1]
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom) and node.level > 0:
            found.update(target[0] for target in _relative_targets(node, package) if target)
        elif isinstance(node, ast.Import | ast.ImportFrom):
            for target in _absolute_targets(node):
                if target[0] == "visual_agent" and len(target) > 1:
                    found.add(target[1])
    return found & LAYERS


def boundary_violations(root: Path) -> list[str]:
    violations = []
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root).parts
        layer = relative[0] if len(relative) > 1 else ""
        for imported in sorted(imported_layers(path, root) & FORBIDDEN.get(layer, set())):
            violations.append(f"{'/'.join(relative)} -> {imported}")
    return violations


def _write(root: Path, relative: str, source: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def test_project_respects_module_boundaries() -> None:
    assert boundary_violations(PACKAGE_ROOT) == []


def test_detects_each_forbidden_import_style(tmp_path: Path) -> None:
    _write(tmp_path, "domain/model.py", "from visual_agent.retrieval import search\n")
    _write(tmp_path, "ingest/job.py", "from ..ask import orchestrator\n")
    _write(tmp_path, "ask/flow.py", "import visual_agent.ingest.chunk\n")

    assert boundary_violations(tmp_path) == [
        "ask/flow.py -> ingest",
        "domain/model.py -> retrieval",
        "ingest/job.py -> ask",
    ]


def test_allows_imports_within_the_rules(tmp_path: Path) -> None:
    _write(tmp_path, "ask/flow.py", "from visual_agent.domain import result\nfrom . import steps\n")
    _write(tmp_path, "settings.py", "from visual_agent.ingest import chunk\n")

    assert boundary_violations(tmp_path) == []
