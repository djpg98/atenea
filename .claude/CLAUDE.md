# Atenea — Contexto del proyecto para Claude

## Descripción

Repositorio personal de conocimiento. Corre en local únicamente. Organiza referencias a recursos (fotos, películas, música, etc.) con soporte de colecciones, tags y notas. No almacena archivos, almacena referencias.

El diseño completo y las decisiones de cada sesión están en `documentation/session_N.md`.

---

## Stack

- **Backend:** Django + Django REST Framework
- **Frontend:** Next.js (desacoplado del backend; no mezclar decisiones de ambos al diseñar el backend)
- **Base de datos:** PostgreSQL
- **Gestor de entorno virtual:** uv

---

## Estructura de apps Django

```
atenea/            # config del proyecto (settings, urls raíz, wsgi)
core/              # entidades globales: ResourceRegistry, Tag, Collection, Artist, Notes
photography/       # módulo de fotografía: Photo, PhotoArtist
general/           # módulo general (pendiente de definir)
```

Cada módulo es una app Django independiente. Los módulos pueden depender de `core`, pero nunca entre sí.

---

## Arquitectura en capas

Cada app sigue esta estructura de carpetas:

```
<app>/
  models/          # solo definición de datos
  repositories/    # acceso a datos (queries)
  services/        # lógica de negocio
  serializers/     # validación y transformación de datos
  views/           # capa HTTP, lo más delgada posible
  urls.py
```

### Responsabilidades por capa

| Capa | Responsabilidad |
|---|---|
| **Models** | Definición de campos, relaciones y Meta. Sin lógica de negocio |
| **Repositories** | Toda interacción con la base de datos. Devuelven instancias de modelo o QuerySets |
| **Services** | Lógica de negocio. Llaman a repositorios, nunca a modelos directamente |
| **Views** | Reciben la request HTTP, llaman al servicio correspondiente, devuelven la response |
| **Serializers** | Validación de input y serialización de output |

---

## Reglas del código Django

### 1. Modelos solo en repositorios y serializers
Los modelos solo deben ser importados en repositorios, serializers y, si fuera necesario, en forms. Ninguna otra capa importa modelos directamente.

### 2. FKs con patrón string
Al declarar una ForeignKey (u otras relaciones) en un modelo, usar siempre el patrón de string en lugar de importar la clase:

```python
# Correcto
registry = models.ForeignKey("core.ResourceRegistry", on_delete=models.CASCADE)

# Incorrecto
from core.models.resource_registry import ResourceRegistry
registry = models.ForeignKey(ResourceRegistry, on_delete=models.CASCADE)
```

Esto evita imports circulares y mantiene el acoplamiento bajo entre apps.

### 3. Excepciones personalizadas por app
Cada app expone sus propias excepciones en `<app>/exceptions.py`. Los repositorios capturan excepciones de Django (como `Model.DoesNotExist`) internamente y lanzan la excepción propia correspondiente. Servicios y vistas solo importan excepciones, nunca modelos directamente.

```python
# core/exceptions.py
class ResourceRegistryNotFound(Exception):
    pass

# En el repositorio (único lugar donde se importa el modelo):
try:
    return ResourceRegistry.objects.get(id=registry_id)
except ResourceRegistry.DoesNotExist:
    raise ResourceRegistryNotFound(...)
```

### 4. Transacciones en operaciones que afectan ResourceRegistry
Cualquier operación que modifique tanto `ResourceRegistry` como el recurso específico (Photo, Movie, etc.) debe ejecutarse dentro de una transacción atómica. Esto incluye creación y cualquier modificación que afecte ambas tablas.

```python
# Patrón esperado en el service
from django.db import transaction

with transaction.atomic():
    registry_entry = resource_registry_repository.create(...)
    photo = photo_repository.create(registry=registry_entry, ...)
```

---

## Convenciones de estilo Python

Se sigue PEP 8 como estándar base. Resumen de las convenciones aplicables:

| Elemento | Convención | Ejemplo |
|---|---|---|
| Clases | PascalCase | `PhotoRepository`, `ResourceRegistry` |
| Funciones y métodos | snake_case | `get_by_id`, `create_photo` |
| Variables | snake_case | `registry_entry`, `photo_list` |
| Constantes | UPPER_SNAKE_CASE | `MAX_PREVIEW_ITEMS` |
| Módulos y archivos | snake_case | `photo_repository.py` |
| Atributos privados | `_prefijo` | `_cache`, `_registry` |

### Regla obligatoria
**Todos los nombres** (clases, funciones, variables, métodos, módulos, constantes) deben estar **en inglés**, sin excepción.

---

## Type hints

Se usa type hinting estricto en todas las capas. Todos los métodos y funciones deben declarar tipos en parámetros y valor de retorno.

### Repositorios y serializers
Importan modelos directamente (permitido por las reglas), por lo que pueden usar los tipos de modelo sin restricción:

```python
from photography.models import Photo

class PhotoRepository:
    def get_by_id(self, photo_id: int) -> Photo:
        ...
```

### Servicios y vistas
No deben importar modelos en runtime. Para tipar retornos o parámetros que son instancias de modelo, usar `TYPE_CHECKING`:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from photography.models import Photo

class PhotoService:
    def get_by_id(self, photo_id: int) -> Photo:
        ...
```

`from __future__ import annotations` hace que todas las anotaciones sean evaluadas de forma lazy, por lo que el tipo `Photo` en la firma no genera un import en runtime. El bloque `TYPE_CHECKING` solo se ejecuta cuando herramientas de análisis estático (mypy, Pylance) procesan el archivo.

---

## Migraciones

Se usa el sistema de migraciones de Django. Cada app tiene su carpeta `migrations/` con el historial completo de cambios al schema.

### Reglas
1. **Nombres descriptivos:** siempre usar `makemigrations --name <nombre>` con un nombre que describa el cambio. Nunca dejar el nombre automático (`0002_auto_...`)
2. **Una migración por cambio lógico:** no mezclar cambios no relacionados en la misma migración
3. **No editar migraciones ya aplicadas:** si hay un error, se corrige con una nueva migración

---

## API

- Todas las rutas bajo `/api/v1/`
- Ejemplo: `/api/v1/photography/photos/`, `/api/v1/core/collections/`

---

## Schema de base de datos

### Core

**`ResourceType`** — tipos de recurso por módulo

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| name | varchar | "photo", "movie", etc. |
| area | choices | photography, cinema, music, computer_science, comics, general |

**`ResourceRegistry`** — registro central de todos los recursos

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| resource_type_id | FK → ResourceType | |
| created_at | datetime | |
| updated_at | datetime | |

**`Tag`**

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| name | varchar, único | texto libre, cualquier idioma |

**`ResourceTag`** — relación M2M entre recursos y tags

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| registry_id | FK → ResourceRegistry | |
| tag_id | FK → Tag | |
| — | unique together | (registry_id, tag_id) |

**`Collection`**

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| name | varchar | |
| description | text | opcional |
| image | varchar | opcional |
| featured | boolean | default False |

**`CollectionItem`** — items de una colección, con orden manual

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| collection_id | FK → Collection | |
| registry_id | FK → ResourceRegistry | |
| order | integer | |
| — | unique together | (collection_id, registry_id) |

**`Artist`** — entidad global compartida entre módulos

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| name | varchar | |
| nationality | varchar | opcional |
| birth_date | date | opcional |

**`ArtistNote`**

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| artist_id | FK → Artist | |
| content | text | |
| created_at | datetime | |
| updated_at | datetime | |

**`ResourceNote`**

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| registry_id | FK → ResourceRegistry | |
| content | text | |
| created_at | datetime | |
| updated_at | datetime | |

---

### Photography

**`Photo`**

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| registry_id | FK → ResourceRegistry, único | OneToOne en la práctica |
| reference | varchar | |
| reference_type | enum | url / filesystem |
| title | varchar | opcional |
| year | integer | opcional |
| iso | integer | opcional |
| lens | varchar | opcional |
| camera | varchar | opcional |

**`PhotoArtist`** — relación M2M entre fotos y artistas

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| photo_id | FK → Photo | |
| artist_id | FK → Artist | |
| — | unique together | (photo_id, artist_id) |
