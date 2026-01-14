import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response

from users.exceptions import BaseException
from users.response_handler import APIResponse, ErroreDtail

logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """
    Handler customizado que intercepta todas as exceptions e retorna APIResponse.
    
    Hierarquia:
    1. BaseException
    2. ValidationError (DRF)
    3. APIException (outras do DRF)
    4. Exception genérica (fallback)

    o validation Error vem depois do APIException porque ela herda dela.
    Já o BaseException vai pegar as exceptions customizadas dos usuários.
    """

    trace_id = str(uuid4())
    timestamp = timezone.now()

    if isinstance(exc, BaseException):
        error_detail = ErroreDtail(
            code=exc.error_code or "user_error",
            details=exc.details
        )

        api_response = APIResponse(
            status_code=exc.status_code,
            message=exc.message,
            error=error_detail,
            trace_id=trace_id,
            timestamp=timestamp,
        )

        logger.warning(
            f"User exception: {exc.error_code} - {exc.message} (trace_id: {trace_id})"
        )
        return Response(
            api_response.to_dict(),
            status=exc.status_code,
        )

    if isinstance(exc, ValidationError):
        # Extrai os erros de validação
        details = {}
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                details = exc.detail
            elif isinstance(exc.detail, list):
                details = {"non_field_errors": exc.detail}

        error_detail = ErroreDtail(
            code="validation_error",
            details=details
        )

        api_response = APIResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Dados inválidos",
            error=error_detail,
            trace_id=trace_id,
            timestamp=timestamp,
        )

        logger.warning(f"Validation error (trace_id: {trace_id}): {details}")
        return Response(
            api_response.to_dict(),
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    if isinstance(exc, APIException):
        error_detail = ErroreDtail(
            code=exc.__class__.__name__.upper(),
            details=None
        )

        api_response = APIResponse(
            status_code=exc.status_code,
            message=str(exc.detail),
            error=error_detail,
            trace_id=trace_id,
            timestamp=timestamp,
        )

        logger.warning(
            f"API exception: {exc.__class__.__name__} (trace_id: {trace_id})"
        )
        return Response(
            api_response.to_dict(),
            status=exc.status_code,
        )

    logger.exception(f"Unhandled exception (trace_id: {trace_id})")

    error_detail = ErroreDtail(
        code="internal_error",
        details=None
    )

    api_response = APIResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Erro interno do servidor",
        error=error_detail,
        trace_id=trace_id,
        timestamp=timestamp,
    )

    return Response(
        api_response.to_dict(),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
