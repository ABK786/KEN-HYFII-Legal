"""KAI public safe evaluation harness.

This sample checks response text against simple role, safety, and disclosure rules.
It is intentionally local and does not call any external service.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class KAITestCase:
    case_id: str
    title: str
    prompt: str
    must_contain: list[str]
    must_not_contain: list[str]
    severity: str = "major"


@dataclass
class KAITestResult:
    case_id: str
    title: str
    severity: str
    score: str
    passed: list[str]
    failed: list[str]


def load_cases(path: Path) -> list[KAITestCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [KAITestCase(**item) for item in raw]


def evaluate_response(case: KAITestCase, response_text: str) -> KAITestResult:
    passed: list[str] = []
    failed: list[str] = []
    lower = response_text.lower()

    for item in case.must_contain:
        if item.lower() in lower:
            passed.append(f"contains:{item}")
        else:
            failed.append(f"missing:{item}")

    for item in case.must_not_contain:
        if re.search(re.escape(item), response_text, re.IGNORECASE):
            failed.append(f"forbidden:{item}")
        else:
            passed.append(f"absent:{item}")

    score = "PASS" if not failed else "FAIL"
    return KAITestResult(case.case_id, case.title, case.severity, score, passed, failed)


def main() -> None:
    parser = argparse.ArgumentParser(description="KAI public safe evaluation harness")
    parser.add_argument("--cases", required=True, help="Path to public safe test cases JSON")
    parser.add_argument("--responses", required=True, help="Folder containing response text files named by case_id")
    parser.add_argument("--report", default="kai_eval_report.json", help="Output report path")
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    response_dir = Path(args.responses)
    results: list[KAITestResult] = []

    for case in cases:
        response_file = response_dir / f"{case.case_id}.txt"
        response_text = response_file.read_text(encoding="utf-8") if response_file.exists() else ""
        results.append(evaluate_response(case, response_text))

    output = {
        "total": len(results),
        "passed": sum(1 for result in results if result.score == "PASS"),
        "failed": sum(1 for result in results if result.score == "FAIL"),
        "results": [asdict(result) for result in results],
    }
    Path(args.report).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"KAI evaluation complete: {output['passed']}/{output['total']} passed")


if __name__ == "__main__":
    main()
