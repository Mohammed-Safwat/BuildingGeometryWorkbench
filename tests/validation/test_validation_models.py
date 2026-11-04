"""Tests for geometry validation result models."""

import pytest

from buildingpipeline.validation.models import (
    ValidationIssue,
    ValidationReport,
    ValidationSeverity,
)


@pytest.fixture
def sample_issues() -> tuple[ValidationIssue, ...]:
    """Return sample validation issues with different severities."""
    return (
        ValidationIssue(
            issue_code="FLOOR_INVALID",
            severity=ValidationSeverity.ERROR,
            message="Floor outline is invalid.",
            element_id="F1",
            floor_id="F1",
        ),
        ValidationIssue(
            issue_code="COLUMN_UNSUPPORTED",
            severity=ValidationSeverity.WARNING,
            message="Column has insufficient support.",
            element_id="C1-1",
            floor_id="F1",
        ),
        ValidationIssue(
            issue_code="SLAB_CHECK",
            severity=ValidationSeverity.INFO,
            message="Slab geometry checked.",
            element_id="F1",
            floor_id="F1",
        ),
    )


def test_validation_issue_creation() -> None:
    """Verify that a validation issue stores its properties."""
    issue = ValidationIssue(
        issue_code="FLOOR_INVALID",
        severity=ValidationSeverity.ERROR,
        message="Invalid floor outline.",
        element_id="F1",
        floor_id="F1",
    )

    assert issue.issue_code == "FLOOR_INVALID"
    assert issue.severity == ValidationSeverity.ERROR
    assert issue.element_id == "F1"
    assert issue.floor_id == "F1"


def test_validation_issue_allows_missing_floor_id() -> None:
    """Verify that floor ID can be omitted for building-level issues."""
    issue = ValidationIssue(
        issue_code="BUILDING_INVALID",
        severity=ValidationSeverity.ERROR,
        message="Building validation failed.",
        element_id="BUILDING",
    )

    assert issue.floor_id is None


def test_validation_issue_rejects_empty_issue_code() -> None:
    """Verify that an empty issue code is rejected."""
    with pytest.raises(ValueError, match="Issue code"):
        ValidationIssue(
            issue_code=" ",
            severity=ValidationSeverity.ERROR,
            message="Invalid geometry.",
            element_id="F1",
        )


def test_validation_issue_rejects_invalid_severity() -> None:
    """Verify that invalid severity types are rejected."""
    with pytest.raises(TypeError, match="Severity"):
        ValidationIssue(
            issue_code="FLOOR_INVALID",
            severity="error",
            message="Invalid geometry.",
            element_id="F1",
        )


def test_validation_report_stores_issues() -> None:
    """Verify that a report stores the supplied issues."""
    issue = ValidationIssue(
        issue_code="FLOOR_INVALID",
        severity=ValidationSeverity.ERROR,
        message="Invalid floor outline.",
        element_id="F1",
    )

    report = ValidationReport(issues=(issue,))

    assert report.issues == (issue,)

def test_validation_report_rejects_invalid_issue_type() -> None:
    """Verify that a report rejects non-ValidationIssue objects."""
    with pytest.raises(TypeError, match="ValidationIssue"):
        ValidationReport(issues=("invalid issue",))

def test_empty_validation_report_is_valid() -> None:
    """Verify that an empty report is considered valid."""
    report = ValidationReport()

    assert report.is_valid
    assert report.error_count == 0
    assert report.warning_count == 0
    assert report.info_count == 0


def test_validation_report_counts_issues(
    sample_issues: tuple[ValidationIssue, ...],
) -> None:
    """Verify issue counts by severity."""
    report = ValidationReport(issues=sample_issues)

    assert report.error_count == 1
    assert report.warning_count == 1
    assert report.info_count == 1


def test_validation_report_is_invalid_when_errors_exist(
    sample_issues: tuple[ValidationIssue, ...],
) -> None:
    """Verify that error-level issues make a report invalid."""
    report = ValidationReport(issues=sample_issues)

    assert not report.is_valid


def test_validation_report_is_valid_with_warnings_only() -> None:
    """Verify that warnings do not make a report invalid."""
    issue = ValidationIssue(
        issue_code="COLUMN_WARNING",
        severity=ValidationSeverity.WARNING,
        message="Column support should be reviewed.",
        element_id="C1-1",
    )

    report = ValidationReport(issues=(issue,))

    assert report.is_valid
    assert report.warning_count == 1