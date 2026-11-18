import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from check_features import main  # noqa: E402


def write_features(tmp_path, features):
    path = tmp_path / "features.json"
    path.write_text(json.dumps(features), encoding="utf-8")
    return str(path)


def feature(identifier, passes=False, verify="bot reaches the exit"):
    return {"id": identifier, "description": "a thing", "verify": verify, "passes": passes}


def test_valid(tmp_path):
    path = write_features(tmp_path, [feature("jump"), feature("exit", passes=True)])
    assert main([path]) == 0


def test_duplicate_id(tmp_path):
    path = write_features(tmp_path, [feature("jump"), feature("jump")])
    assert main([path]) == 1


def test_missing_verify(tmp_path):
    path = write_features(tmp_path, [feature("jump", verify="  ")])
    assert main([path]) == 1


def test_start_rejects_true_pass(tmp_path):
    path = write_features(tmp_path, [feature("jump", passes=True)])
    assert main([path, "--start"]) == 1


def test_start_accepts_all_false(tmp_path):
    path = write_features(tmp_path, [feature("jump")])
    assert main([path, "--start"]) == 0


def test_unreadable(tmp_path):
    assert main([str(tmp_path / "missing.json")]) == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    assert main([str(broken)]) == 2
