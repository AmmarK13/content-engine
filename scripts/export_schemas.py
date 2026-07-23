"""
Export JSON Schemas for every Pydantic model defined in contracts/common,
contracts/registry, and contracts/stages.

Each model is written to contracts/<package>/v<version>/<snake_case_name>.schema.json,
where <version> is the trailing "VN" suffix on the class name (e.g. IdeaRequestV1
-> contracts/stages/v1/idea_request.schema.json).

Usage:
    python scripts/export_schemas.py
"""

from __future__ import annotations

import importlib
import inspect
import json
import re
import sys
from pathlib import Path

from pydantic import BaseModel

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

PACKAGES = ["common", "registry", "stages"]

VERSION_SUFFIX_RE = re.compile(r"^(?P<base>.+)V(?P<version>\d+)$")
CAMEL_TO_SNAKE_RE = re.compile(r"(?<!^)(?=[A-Z])")


def snake_case(name: str) -> str:
    return CAMEL_TO_SNAKE_RE.sub("_", name).lower()


def discover_modules(package: str) -> list[str]:
    package_dir = REPO_ROOT / "contracts" / package
    module_names = []
    for path in sorted(package_dir.glob("*.py")):
        if path.stem == "__init__":
            continue
        module_names.append(f"contracts.{package}.{path.stem}")
    return module_names


def model_classes(module) -> list[type[BaseModel]]:
    classes = []
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if obj is BaseModel:
            continue
        if obj.__module__ != module.__name__:
            continue
        if issubclass(obj, BaseModel):
            classes.append(obj)
    return classes


def export_model(package: str, model: type[BaseModel]) -> Path:
    match = VERSION_SUFFIX_RE.match(model.__name__)
    if not match:
        raise ValueError(
            f"{model.__name__} in contracts.{package} has no version suffix (e.g. 'V1')"
        )

    base_name = snake_case(match.group("base"))
    version = match.group("version")

    out_dir = REPO_ROOT / "contracts" / package / f"v{version}"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{base_name}.schema.json"
    schema = model.model_json_schema()
    out_path.write_text(json.dumps(schema, indent=2) + "\n")
    return out_path


def main() -> None:
    written = []
    for package in PACKAGES:
        for module_name in discover_modules(package):
            module = importlib.import_module(module_name)
            for model in model_classes(module):
                written.append(export_model(package, model))

    for path in written:
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    print(f"\n{len(written)} schema(s) exported")


if __name__ == "__main__":
    main()
