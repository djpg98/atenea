from __future__ import annotations

import logging
from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def envelope_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    logger.exception("Unhandled exception in view", exc_info=exc)
    return Response({'error': 'Internal server error'}, status=500)
