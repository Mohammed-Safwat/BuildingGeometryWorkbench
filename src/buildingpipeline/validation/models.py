"""Data models for geometry validation results."""

from dataclasses import dataclass
from enum import StrEnum


class ValidationSeverity(StrEnum):
    """Represent the severity of a validation issue."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Represent one issue detected during geometry validation."""

    issue_code: str
    severity: ValidationSeverity
    message: str
    element_id: str
    floor_id: str | None = None

    def __post_init__(self) -> None:
        """Validate the issue properties."""
        if not isinstance(self.issue_code, str) or not self.issue_code.strip():
            raise ValueError("Issue code must be a non-empty string.")

        if not isinstance(self.severity, ValidationSeverity):
            raise TypeError("Severity must be a ValidationSeverity value.")

        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("Issue message must be a non-empty string.")

        if not isinstance(self.element_id, str) or not self.element_id.strip():
            raise ValueError("Element ID must be a non-empty string.")

        if self.floor_id is not None and (
            not isinstance(self.floor_id, str) or not self.floor_id.strip()
        ):
            raise ValueError("Floor ID must be a non-empty string or None.")


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """Collect and summarize geometry validation issues."""

    issues: tuple[ValidationIssue, ...] = ()

    def __post_init__(self) -> None:
        """Validate the collection of issues."""
        if not isinstance(self.issues, tuple):
            raise TypeError("Validation issues must be provided as a tuple.")

        if not all(
            isinstance(issue, ValidationIssue) for issue in self.issues
        ):
            raise TypeError("All report items must be ValidationIssue objects.")

    @property
    def is_valid(self) -> bool:
        """Return whether the report contains no error-level issues."""
        return not any(
            issue.severity == ValidationSeverity.ERROR
            for issue in self.issues
        )

    @property
    def error_count(self) -> int:
        """Return the number of error-level issues."""
        return sum(
            issue.severity == ValidationSeverity.ERROR
            for issue in self.issues
        )

    @property
    def warning_count(self) -> int:
        """Return the number of warning-level issues."""
        return sum(
            issue.severity == ValidationSeverity.WARNING
            for issue in self.issues
        )

    @property
    def info_count(self) -> int:
        """Return the number of informational issues."""
        return sum(
            issue.severity == ValidationSeverity.INFO
            for issue in self.issues
        )