#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
if str(IMPLEMENTATION_ROOT) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION_ROOT))

from capstone_clip00.evaluation import evaluate_acceptance, summarize_episode_logs
from capstone_clip00.io import load_acceptance_criteria, load_episode_logs_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize validated episode JSONL logs.")
    parser.add_argument("episodes", type=Path)
    parser.add_argument(
        "--acceptance",
        type=Path,
        default=IMPLEMENTATION_ROOT / "configs" / "acceptance-criteria.yaml",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    episodes = load_episode_logs_jsonl(args.episodes)
    criteria = load_acceptance_criteria(args.acceptance)
    summary = summarize_episode_logs(episodes)
    report = {"summary": summary, "acceptance": evaluate_acceptance(summary, criteria)}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
