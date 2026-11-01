from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from core.exceptions import InvalidResourceArea


class CollectionMetadata(BaseModel):
    model_config = ConfigDict(extra='forbid', validate_assignment=True)

    photography: int = Field(default=0, ge=0)
    movies: int = Field(default=0, ge=0)
    music: int = Field(default=0, ge=0)
    computer_science: int = Field(default=0, ge=0)
    comics: int = Field(default=0, ge=0)
    general: int = Field(default=0, ge=0)


class CollectionMetadataManager:
    def __init__(self, metadata: dict[str, int] | None = None) -> None:
        try:
            self._metadata = CollectionMetadata(**(metadata or {}))
        except ValueError as exc:
            raise InvalidResourceArea(f"Invalid collection metadata: {metadata}") from exc

    def increment(self, area: str) -> dict[str, int]:
        self._set(area, self._get(area) + 1)
        return self.to_dict()

    def decrement(self, area: str) -> dict[str, int]:
        self._set(area, max(self._get(area) - 1, 0))
        return self.to_dict()

    def to_dict(self) -> dict[str, int]:
        return self._metadata.model_dump()

    def _get(self, area: str) -> int:
        if area not in CollectionMetadata.model_fields:
            raise InvalidResourceArea(f"Unknown resource area: {area}")
        return getattr(self._metadata, area)

    def _set(self, area: str, value: int) -> None:
        if area not in CollectionMetadata.model_fields:
            raise InvalidResourceArea(f"Unknown resource area: {area}")
        try:
            setattr(self._metadata, area, value)
        except ValueError as exc:
            raise InvalidResourceArea(f"Invalid value for area {area}: {value}") from exc
