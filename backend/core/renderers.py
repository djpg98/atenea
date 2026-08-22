from __future__ import annotations

from typing import Any

from rest_framework.renderers import JSONRenderer


class EnvelopeJSONRenderer(JSONRenderer):
    def render(
        self,
        data: Any,
        accepted_media_type: str | None = None,
        renderer_context: dict[str, Any] | None = None,
    ) -> bytes:
        renderer_context = renderer_context or {}
        response = renderer_context.get('response')
        status_code = response.status_code if response is not None else 200

        if status_code >= 500:
            result = 'error'
        elif status_code >= 400:
            result = 'failure'
        else:
            result = 'success'

        envelope: dict[str, Any] = {'result': result}
        if data is not None:
            envelope['data'] = data

        return super().render(envelope, accepted_media_type, renderer_context)
