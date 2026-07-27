"""
scripts/contract_lint.py

Checks every Pydantic model under contracts/ for architecture-rule
violations. Currently enforces:

  1. Every BaseModel subclass must set model_config with extra="forbid".
     (Missed three times already in this project's history - this is
     the check that would have caught all three automatically.)

  2. No file under graph/ may reference a concrete provider/vendor name.
     (graph/ is empty as of M0 - this check runs and passes trivially
     for now, but starts protecting the rule the moment graph/ has
     real content, without needing to be written later.)

Exit code 0 = clean, 1 = violations found (CI-ready).

Usage:
    python scripts/contract_lint.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
import re



REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = REPO_ROOT / "contracts"
GRAPH_DIR = REPO_ROOT / "graph"
TESTS_DIR = REPO_ROOT / "tests"
VERSION_SUFFIX_RE = re.compile(r"^.+V\d+$")

# Known provider/vendor names the graph must never reference directly.
# Extend this list as new providers are integrated (M2+).
KNOWN_VENDOR_NAMES = [
    "elevenlabs",
    "liveportrait",
    "musetalk",
    "latentsync",
    "whisperx",
    "youtube",
]


def _model_config_has_extra_forbid(class_node: ast.ClassDef) -> bool:
    """
    Walk a class body looking for `model_config = {...}` and check
    whether that dict literal contains "extra": "forbid" specifically -
    not just the word "extra" appearing anywhere in the class.
    """
    for node in class_node.body:
        if not isinstance(node, ast.Assign):
            continue
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "model_config" not in targets:
            continue
        if not isinstance(node.value, ast.Dict):
            continue
        for key_node, value_node in zip(node.value.keys, node.value.values):
            if (
                isinstance(key_node, ast.Constant)
                and key_node.value == "extra"
                and isinstance(value_node, ast.Constant)
                and value_node.value == "forbid"
            ):
                return True
    return False


def _is_basemodel_subclass(class_node: ast.ClassDef) -> bool:
    return any(
        isinstance(base, ast.Name) and base.id == "BaseModel"
        for base in class_node.bases
    )


def check_extra_forbid(path: Path) -> list[str]:
    problems = []
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and _is_basemodel_subclass(node):
            if not _model_config_has_extra_forbid(node):
                rel = path.relative_to(REPO_ROOT)
                problems.append(
                    f'{rel}:{node.lineno} {node.name} missing model_config = {{"extra": "forbid"}}'
                )
    return problems


def check_no_vendor_names_in_graph(path: Path) -> list[str]:
    problems = []
    text = path.read_text().lower()
    for vendor in KNOWN_VENDOR_NAMES:
        if vendor in text:
            rel = path.relative_to(REPO_ROOT)
            problems.append(f"{rel}: references vendor name '{vendor}' - capability names only in graph/")
    return problems




def check_id_field_naming(path: Path) -> list[str]:
    """
    Flags any Pydantic model field literally named `id` instead of a
    scoped name like `identity_id`, `style_id`, `run_id`. A bare `id`
    is ambiguous once serialized to JSON and sitting next to other IDs
    in a log line or dashboard - exactly the bug found in
    IdentityProfileV1/VoiceProfileV1 before they were fixed.
    """
    problems = []
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and _is_basemodel_subclass(node):
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    if item.target.id == "id":
                        rel = path.relative_to(REPO_ROOT)
                        problems.append(
                            f"{rel}:{item.lineno} {node.name}.id should be a scoped "
                            f"name (e.g. <noun>_id), not bare 'id'"
                        )
    return problems


def check_model_version_suffix(path: Path) -> list[str]:
    """
    Every contract model must end in a version suffix like V1, matching
    the project's versioning convention (breaking changes get a new
    version, never an in-place edit). scripts/export_schemas.py already
    depends on this and crashes without it - this check catches the same
    problem earlier, with a clearer message.
    """
    problems = []
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and _is_basemodel_subclass(node):
            if not VERSION_SUFFIX_RE.match(node.name):
                rel = path.relative_to(REPO_ROOT)
                problems.append(
                    f"{rel}:{node.lineno} {node.name} has no version suffix (e.g. 'V1')"
                )
    return problems


def check_no_naive_utcnow(path: Path) -> list[str]:
    """
    Flags deprecated datetime.utcnow usage, whether called directly
    (datetime.utcnow()) or passed as a callable
    (default_factory=datetime.utcnow). Use datetime.now(UTC) instead.
    """
    problems = []
    tree = ast.parse(path.read_text(), filename=str(path))

    for node in ast.walk(tree):
        target = None

        if isinstance(node, ast.Call):
            target = node.func
        elif isinstance(node, ast.Attribute):
            target = node

        if (
            isinstance(target, ast.Attribute)
            and target.attr == "utcnow"
            and isinstance(target.value, ast.Name)
            and target.value.id == "datetime"
        ):
            rel = path.relative_to(REPO_ROOT)
            problems.append(
                f"{rel}:{node.lineno} uses deprecated datetime.utcnow - "
                f"use datetime.now(UTC)"
            )

    return problems
    
def check_test_file_has_real_tests(path: Path) -> list[str]:
    """
    Flags any tests/test_*.py or tests/*_test.py file with zero actual
    test functions and zero assert/pytest.raises usage - i.e. a script
    that LOOKS like a test file but that pytest would collect nothing
    meaningful from, and that could never fail a build. This is exactly
    the shape of bug found in the original tests/test_fixtures.py.
    """
    problems = []
    tree = ast.parse(path.read_text(), filename=str(path))

    has_test_function = any(
        isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        for node in ast.walk(tree)
    )
    has_assert = any(isinstance(node, ast.Assert) for node in ast.walk(tree))
    has_pytest_raises = any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "raises"
        for node in ast.walk(tree)
    )

    if not has_test_function and not has_assert and not has_pytest_raises:
        rel = path.relative_to(REPO_ROOT)
        problems.append(
            f"{rel}: looks like a test file but has no test_ functions, "
            f"assert statements, or pytest.raises - pytest will collect "
            f"nothing meaningful from it"
        )
    return problems


def check_no_orphaned_test_scripts(tests_dir: Path) -> list[str]:
    """
    Flags any .py file under tests/ that imports pytest or ValidationError
    (signals it's meant to be a test) but whose filename doesn't match
    pytest's default discovery pattern (test_*.py / *_test.py) - such a
    file is invisible to `pytest tests/` no matter what's inside it.
    Exactly the bug in the original verify_envelope.py.
    """
    problems = []
    if not tests_dir.exists():
        return problems
    for path in sorted(tests_dir.glob("*.py")):
        if path.name == "__init__.py":
            continue
        name = path.stem
        if name.startswith("test_") or name.endswith("_test"):
            continue
        text = path.read_text()
        if "import pytest" in text or "ValidationError" in text:
            rel = path.relative_to(REPO_ROOT)
            problems.append(
                f"{rel}: looks like a test file but its name doesn't match "
                f"pytest's discovery pattern (test_*.py / *_test.py) - "
                f"pytest will never collect it"
            )
    return problems


def check_every_model_has_a_fixture() -> list[str]:
    """
    Cross-references every discoverable contract model against
    tests/test_fixtures.py's fixture lists, and flags any model with
    zero fixture coverage. Automates the exact gap that previously
    needed a manual audit to find ("17 of 25 models have no fixtures").
    """
    problems = []
    test_fixtures_path = TESTS_DIR / "test_fixtures.py"
    if not test_fixtures_path.exists():
        return [f"{test_fixtures_path.relative_to(REPO_ROOT)} does not exist - cannot check fixture coverage"]

    fixtures_tree = ast.parse(test_fixtures_path.read_text(), filename=str(test_fixtures_path))
    covered_model_names = {
        node.id
        for node in ast.walk(fixtures_tree)
        if isinstance(node, ast.Name) and VERSION_SUFFIX_RE.match(node.id)
    }

    for package in ("common", "registry", "stages"):
        package_dir = CONTRACTS_DIR / package
        if not package_dir.exists():
            continue
        for path in sorted(package_dir.glob("*.py")):
            if path.name == "__init__.py":
                continue
            file_tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(file_tree):
                if isinstance(node, ast.ClassDef) and _is_basemodel_subclass(node):
                    if node.name not in covered_model_names:
                        rel = path.relative_to(REPO_ROOT)
                        problems.append(
                            f"{rel}: {node.name} has no fixture coverage in tests/test_fixtures.py"
                        )
    return problems

def main() -> int:
    all_problems: list[str] = []

    for path in sorted(CONTRACTS_DIR.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        all_problems.extend(check_extra_forbid(path))
        all_problems.extend(check_id_field_naming(path))
        all_problems.extend(check_model_version_suffix(path))
        all_problems.extend(check_no_naive_utcnow(path))

    if GRAPH_DIR.exists():
        for path in sorted(GRAPH_DIR.rglob("*.py")):
            all_problems.extend(check_no_vendor_names_in_graph(path))

    if TESTS_DIR.exists():
        for path in sorted(TESTS_DIR.glob("test_*.py")):
            all_problems.extend(check_test_file_has_real_tests(path))
        for path in sorted(TESTS_DIR.glob("*_test.py")):
            all_problems.extend(check_test_file_has_real_tests(path))
        all_problems.extend(check_no_orphaned_test_scripts(TESTS_DIR))

    all_problems.extend(check_every_model_has_a_fixture())

    if all_problems:
        print(f"contract-lint found {len(all_problems)} problem(s):\n")
        for problem in all_problems:
            print(f"  {problem}")
        print()
        return 1

    print("contract-lint: clean")
    return 0

if __name__ == "__main__":
    sys.exit(main())