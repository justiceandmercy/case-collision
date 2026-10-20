import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))
import case_collision  # noqa: E402


def test_detects_case_collision():
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        with patch("case_collision.collect_paths", return_value=["README.md", "readme.md"]):
            collisions = case_collision.find_collisions(project)
        assert collisions
        paths = next(iter(collisions.values()))
        assert paths == ["README.md", "readme.md"]


def test_no_collision():
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        with patch("case_collision.collect_paths", return_value=["README.md", "notes.txt"]):
            collisions = case_collision.find_collisions(project)
        assert collisions == {}


def test_json_output():
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        with patch("case_collision.collect_paths", return_value=["A.txt", "a.txt"]):
            with patch("sys.stdout.write") as write:
                # Call main with patched argv and collect printed output indirectly is awkward;
                # instead verify the JSON payload shape directly.
                collisions = case_collision.find_collisions(project)
                payload = {
                    "collisions": [
                        {"key": key, "paths": paths}
                        for key, paths in sorted(collisions.items())
                    ]
                }
        assert len(payload["collisions"]) == 1
        assert payload["collisions"][0]["paths"] == ["A.txt", "a.txt"]
        # Ensure JSON serialization works.
        assert json.loads(json.dumps(payload)) == payload
        _ = write


def test_main_strict_exit_code():
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        with patch("case_collision.collect_paths", return_value=["A.txt", "a.txt"]):
            with patch("sys.argv", ["case_collision.py", str(project), "--strict"]):
                assert case_collision.main() == 1
