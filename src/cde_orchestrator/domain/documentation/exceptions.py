"""
Domain Exceptions for Documentation Module.

All documentation-related errors that represent business rule violations.
These are domain exceptions, NOT infrastructure errors (e.g., file I/O).

Exception Hierarchy:
    SpecificationError (base)
    ├── SpecificationNotFoundError
    ├── InvalidStatusTransitionError
    ├── InvalidLinkError
    └── SpecificationValidationError
"""


class SpecificationError(Exception):
    """Base exception for all specification domain errors."""

    pass


class SpecificationNotFoundError(SpecificationError):
    """Raised when specification does not exist in repository."""

    def __init__(self, spec_id: str):
        self.spec_id = spec_id
        super().__init__(f"Specification not found: {spec_id}")


class InvalidStatusTransitionError(SpecificationError):
    """Raised when attempting invalid status transition."""

    def __init__(self, current_status: str, target_status: str, reason: str = ""):
        self.current_status = current_status
        self.target_status = target_status
        self.reason = reason
        message = (
            f"Cannot transition from {current_status} to {target_status}"
            f"{': ' + reason if reason else ''}"
        )
        super().__init__(message)


class InvalidLinkError(SpecificationError):
    """Raised when semantic link violates business rules."""

    def __init__(self, source_id: str, target_id: str, reason: str):
        self.source_id = source_id
        self.target_id = target_id
        self.reason = reason
        super().__init__(f"Cannot link {source_id} → {target_id}: {reason}")


class SpecificationValidationError(SpecificationError):
    """Raised when specification fails validation rules."""

    def __init__(self, field: str, value: str, constraint: str):
        self.field = field
        self.value = value
        self.constraint = constraint
        super().__init__(f"Validation failed for {field}='{value}': {constraint}")
