from dataclasses import dataclass
from datetime import datetime
from typing import Any, Generic, TypeVar

T = TypeVar('T')

@dataclass
class ErroreDtail:
    code: str
    details: dict[str, Any] | None = None

@dataclass
class APIResponse(Generic[T]):
    status_code: int
    message: str | None = None
    data: T | None = None
    error: ErroreDtail | None = None
    trace_id: str | None = None
    timestamp: str | datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        if isinstance(self.timestamp, datetime):
            self.timestamp = self.timestamp.isoformat()
        response = {
            "status_code": self.status_code,
            "message": self.message,
            "data": self.data,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
        }
        if self.error:
            response["error"] = {
                "code": self.error.code,
                "details": self.error.details,
            }
        return {k: v for k, v in response.items() if v is not None}
