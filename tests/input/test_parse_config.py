"""Test suite for parse_config function"""
from pathlib import Path

import pytest

from gatorgrade.input.parse_config import parse_config

# each entry is (case id, file contents or None for "do not create the file",
# expected fragment of the error message)
NO_CHECK_CASES = [
    ("empty_file", "", "contains no checks."),
    (
        "comment_only",
        "# checks are added in the next milestone\n",
        "contains no checks.",
    ),
    ("empty_list", "---\n[]\n", "contains no checks."),
    (
        "separator_only",
        "---\n",
        "contains a document separator but no checks.",
    ),
]


def test_parse_config_missing_file(tmp_path: Path) -> None:
    """A file that does not exist reports that it does not exist."""
    missing = tmp_path / "gatorgrade.yml"
    checks, error = parse_config(missing)
    # no checks should be produced and the message must be about the path
    assert checks == []
    assert error == f"The path {missing} does not exist."


@pytest.mark.parametrize(
    ("case_id", "contents", "expected"),
    NO_CHECK_CASES,
    ids=[case[0] for case in NO_CHECK_CASES],
)
def test_parse_config_existing_file_without_checks(
    tmp_path: Path, case_id: str, contents: str, expected: str
) -> None:
    """An existing file with no checks must not claim the file is missing."""
    config = tmp_path / "gatorgrade.yml"
    config.write_text(contents)
    checks, error = parse_config(config)
    assert checks == []
    assert error is not None
    assert expected in error
    assert "does not exist" not in error
    assert "NoneType" not in error


def test_parse_config_valid_file_still_works(tmp_path: Path) -> None:
    """A normal configuration still yields checks and no error."""
    config = tmp_path / "gatorgrade.yml"
    config.write_text("---\n- description: Say hello\n  command: echo hello\n")
    checks, error = parse_config(config)
    assert error is None
    assert len(checks) == 1
