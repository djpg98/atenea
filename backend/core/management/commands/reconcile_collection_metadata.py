from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from core.repositories.collection_item_repository import CollectionItemRepository
from core.services.collection_service import CollectionService
from core.utils.collection_metadata_manager import CollectionMetadata


class Command(BaseCommand):
    help = "Recalcula Collection.metadata a partir de los CollectionItem reales en DB, corrigiendo cualquier drift."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('--dry-run', action='store_true', help='Muestra los cambios sin aplicarlos.')

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run: bool = options['dry_run']

        collection_service = CollectionService()
        item_repository = CollectionItemRepository()

        counts_by_collection: dict[int, dict[str, int]] = {}
        for row in item_repository.count_by_collection_and_area():
            counts_by_collection.setdefault(row['collection_id'], {})[row['area']] = row['count']

        updated = 0
        for collection in collection_service.list_all():
            correct_metadata = CollectionMetadata(**counts_by_collection.get(collection.id, {})).model_dump()

            if collection.metadata == correct_metadata:
                continue

            self.stdout.write(
                f"Collection {collection.id} ({collection.name}): {collection.metadata} -> {correct_metadata}"
            )
            updated += 1

            if not dry_run:
                with transaction.atomic():
                    collection_service.update(collection_id=collection.id, metadata=correct_metadata)

        if updated == 0:
            self.stdout.write(self.style.SUCCESS("Todas las colecciones ya tenian metadata correcto."))
        elif dry_run:
            self.stdout.write(self.style.WARNING(f"Dry-run: {updated} coleccion(es) necesitarian actualizacion."))
        else:
            self.stdout.write(self.style.SUCCESS(f"{updated} coleccion(es) actualizada(s)."))
