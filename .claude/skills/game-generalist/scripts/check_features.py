"""Validate a features.json file.

The file is a list of objects with id (unique), description, verify (non-empty)
and passes (bool). With --start every passes value must be false.
Exit 0 valid, 1 invalid, 2 unreadable.
"""

import argparse
import json
import sys


def collect_problems(features, start_of_build):
    if not isinstance(features, list):
        return ["top level must be a list of feature objects"]
    problems = []
    seen_ids = set()
    for index, feature in enumerate(features):
        label = f"item {index}"
        if not isinstance(feature, dict):
            problems.append(f"{label}: not an object")
            continue
        feature_id = feature.get("id")
        if not isinstance(feature_id, str) or not feature_id.strip():
            problems.append(f"{label}: id missing or empty")
        elif feature_id in seen_ids:
            problems.append(f"{label}: duplicate id {feature_id!r}")
        else:
            seen_ids.add(feature_id)
        description = feature.get("description")
        if not isinstance(description, str) or not description.strip():
            problems.append(f"{label}: description missing or empty")
        verify = feature.get("verify")
        if not isinstance(verify, str) or not verify.strip():
            problems.append(f"{label}: verify missing or empty")
        passes = feature.get("passes")
        if not isinstance(passes, bool):
            problems.append(f"{label}: passes must be true or false")
        elif start_of_build and passes:
            problems.append(f"{label}: passes is true but --start expects all false")
    return problems


def print_table(features):
    print(f"{'id':<20} {'passes':<7} description")
    for feature in features:
        if not isinstance(feature, dict):
            continue
        print(f"{str(feature.get('id', '')):<20} {str(feature.get('passes', '')):<7} {feature.get('description', '')}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate features.json")
    parser.add_argument("path")
    parser.add_argument("--start", action="store_true", help="assert every passes is false")
    arguments = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        with open(arguments.path, encoding="utf-8") as feature_file:
            features = json.load(feature_file)
    except (OSError, ValueError) as error:
        print(f"cannot read {arguments.path}: {error}", file=sys.stderr)
        return 2
    if isinstance(features, list):
        print_table(features)
    problems = collect_problems(features, arguments.start)
    for problem in problems:
        print(f"INVALID {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
