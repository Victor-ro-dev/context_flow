# src/users/exceptions.py
from typing import Any, Optional

from rest_framework import status

from users.response_handler import APIResponse, ErroreDtail


class BaseException(Exception):
    """Base exception class for user-related errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details

    def to_payload(self) -> APIResponse:
        error_detail = ErroreDtail(
            code=self.error_code or "user_error",
            details=self.details,
        )
        return APIResponse(
            status_code=self.status_code,
            message=self.message,
            error=error_detail,
            trace_id=None,
            timestamp=None,
            data=None,
        )


class UserNotFoundException(BaseException):
    """Exception raised when a user is not found."""

    def __init__(self, message: str | None = None, user_id: str | None = None):
        if message is None:
            message = f"User with ID {user_id} not found." if user_id else "User not found."
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="user_not_found",
        )


class InvalidCredentialsException(BaseException):
    """Exception raised for invalid login credentials."""

    def __init__(self, message: str | None = None):
        if message is None:
            message = "Invalid email or password."
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="invalid_credentials",
        )


class UserAlreadyExistsException(BaseException):
    """Exception raised when trying to register a user that already exists."""

    def __init__(self, message: str | None = None, email: str | None = None):
        if message is None:
            message = f"User with email {email} already exists." if email else "User already exists."
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="user_already_exists",
        )


class WeakPasswordException(BaseException):
    """Exception raised for weak passwords."""

    def __init__(self, message: str | None = None, details: dict[str, Any] | None = None):
        if message is None:
            message = "The provided password is too weak."
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="weak_password",
            details=details,
        )


class UnauthorizedAccessException(BaseException):
    """Exception raised for unauthorized access attempts."""

    def __init__(self, message: str | None = None):
        if message is None:
            message = "You do not have permission to perform this action."
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="unauthorized_access",
        )


class PlanNotFoundException(BaseException):
    """Exception raised when a specified plan tier is not found."""

    def __init__(self, message: str | None = None, plan_tier: str | None = None):
        if message is None:
            message = f"Plan tier '{plan_tier}' not found." if plan_tier else "Plan not found."
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="plan_not_found",
        )
