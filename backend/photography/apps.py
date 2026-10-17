from django.apps import AppConfig


class PhotographyConfig(AppConfig):
    name = 'photography'

    def ready(self) -> None:
        from core.registry_resolvers import register_resolver
        from photography.resolvers import resolve_photos_by_registry_ids

        register_resolver('photography', resolve_photos_by_registry_ids)
