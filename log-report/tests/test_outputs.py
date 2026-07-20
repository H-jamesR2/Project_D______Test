import json
import re
from collections import Counter
from pathlib import Path

REPORT_PATH = Path("/app/report.json")
LOG_PATH = Path("/app/access.log")

REQUEST_RE = re.compile(r'"(?:GET|POST|PUT|DELETE|HEAD|PATCH|OPTIONS)\s+(\S+)')


def _compute_expected():
    """Independently recompute ground truth from access.log.

    Deliberately re-implemented rather than importing solve.py — the test
    should verify against the log itself, not against the reference
    solution's code path, so a bug shared by both wouldn't be masked.
    """
    total = 0
    ips = set()
    paths = Counter()
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            parts = line.split()
            if parts:
                ips.add(parts[0])
            m = REQUEST_RE.search(line)
            if m:
                paths[m.group(1)] += 1
    return total, len(ips), paths


def _load_report():
    assert REPORT_PATH.exists(), "no report.json found"
    assert REPORT_PATH.stat().st_size > 0, "report.json is empty"
    try:
        with open(REPORT_PATH) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise AssertionError(f"report.json is not valid JSON: {e}")
    assert isinstance(data, dict), "report.json must contain a JSON object"
    return data

# tests JSON report exists
def test_report_exists():
    """The agent produced a report file."""
    assert REPORT_PATH.exists(), "no report.json found"

# tests JSON report has data
def test_report_is_valid_json_object():
    """The report is parseable JSON, not just non-empty bytes."""
    _load_report()


# tests JSON report has required keys ("total_requests", "unique_ips", "top_path")
def test_report_has_required_keys():
    data = _load_report()
    for key in ("total_requests", "unique_ips", "top_path"):
        assert key in data, f"missing key: {key!r}"

# tests JSON report key total_requests is an INT AND contains expected total for total requests.
def test_total_requests_correct():
    data = _load_report()
    expected_total, _, _ = _compute_expected()
    assert isinstance(data["total_requests"], int), "total_requests must be an int"
    assert data["total_requests"] == expected_total, (
        f"total_requests={data['total_requests']}, expected {expected_total}"
    )

# tests JSON report key unique_ips is an INT AND contains expected total for unique ips.
def test_unique_ips_correct():
    data = _load_report()
    _, expected_unique_ips, _ = _compute_expected()
    assert isinstance(data["unique_ips"], int), "unique_ips must be an int"
    assert data["unique_ips"] == expected_unique_ips, (
        f"unique_ips={data['unique_ips']}, expected {expected_unique_ips}"
    )

# tests JSON report key top_path string contains expected acceptable top_path at max count, no requirement for tie breaking.
def test_top_path_correct():
    data = _load_report()
    _, _, expected_paths = _compute_expected()
    assert expected_paths, "no request paths found in access.log to compare against"
    max_count = max(expected_paths.values())
    acceptable = {p for p, c in expected_paths.items() if c == max_count}
    assert data["top_path"] in acceptable, (
        f"top_path={data['top_path']!r}, expected one of {sorted(acceptable)} "
        f"(tied at count={max_count})"
    )