#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
if str(IMPLEMENTATION_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION_ROOT))

from capstone_clip00.io import (
    load_acceptance_criteria,
    load_failure_catalog,
    load_task_specification,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate all Clip 00 YAML contracts.")
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=IMPLEMENTATION_ROOT / "configs",
    )
    args = parser.parse_args()

    task = load_task_specification(args.config_dir / "task-specification.yaml")
    criteria = load_acceptance_criteria(args.config_dir / "acceptance-criteria.yaml")
    catalog = load_failure_catalog(args.config_dir / "failure-codes.yaml")
    if task.task_id != criteria.task_id:
        raise ValueError(
            f"task_id mismatch: task specification={task.task_id}, acceptance={criteria.task_id}"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "task_id": task.task_id,
                "criteria": len(criteria.criteria),
                "failure_codes": len(catalog.failures),
                "observations": len(task.observations),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
