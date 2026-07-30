from typing import Any


class ApplicationException(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        log_context: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        # Server-side only: merged into the global exception handler's log
        # line, never serialized to the client. Use this instead of `details`
        # for diagnostic fields (ids, internal identifiers) that shouldn't
        # reach API consumers.
        self.log_context = log_context or {}
        super().__init__(message)


class ValidationException(ApplicationException):
    def __init__(
        self,
        message: str = "Validation failed",
        *,
        code: str = "VALIDATION_ERROR",
        details: dict[str, Any] | None = None,
        log_context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, log_context=log_context)


class AuthenticationException(ApplicationException):
    def __init__(
        self,
        message: str = "Authentication required",
        *,
        code: str = "AUTHENTICATION_REQUIRED",
        details: dict[str, Any] | None = None,
        log_context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, log_context=log_context)


class AuthorizationException(ApplicationException):
    def __init__(
        self,
        message: str = "Access denied",
        *,
        code: str = "ACCESS_DENIED",
        details: dict[str, Any] | None = None,
        log_context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, log_context=log_context)


class ConflictException(ApplicationException):
    def __init__(
        self,
        message: str = "Conflict",
        *,
        code: str = "CONFLICT",
        details: dict[str, Any] | None = None,
        log_context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, log_context=log_context)


class NotFoundException(ApplicationException):
    def __init__(
        self,
        message: str = "Resource not found",
        *,
        code: str = "NOT_FOUND",
        details: dict[str, Any] | None = None,
        log_context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, log_context=log_context)


class PersistenceException(ApplicationException):
    def __init__(
        self,
        message: str = "Persistence error",
        *,
        code: str = "PERSISTENCE_ERROR",
        details: dict[str, Any] | None = None,
        log_context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, log_context=log_context)


class ExternalServiceException(ApplicationException):
    def __init__(
        self,
        message: str = "External service error",
        *,
        code: str = "EXTERNAL_SERVICE_ERROR",
        details: dict[str, Any] | None = None,
        log_context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, log_context=log_context)


class BusinessRuleViolation(ApplicationException):
    def __init__(
        self,
        message: str = "Business rule violation",
        *,
        code: str = "BUSINESS_RULE_VIOLATION",
        details: dict[str, Any] | None = None,
        log_context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, log_context=log_context)


class ServiceUnavailableException(ApplicationException):
    """Readiness / dependency unavailable (e.g. database not reachable)."""

    def __init__(
        self,
        message: str = "Service unavailable",
        *,
        code: str = "SERVICE_UNAVAILABLE",
        details: dict[str, Any] | None = None,
        log_context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(code=code, message=message, details=details, log_context=log_context)
