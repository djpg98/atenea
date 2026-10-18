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

### 5. Resolución polimórfica de recursos (registry resolvers)
Cuando algo en `core` necesita el contenido real de un recurso genérico identificado solo por `registry_id` (ej. los items de una `Collection`), `core` **nunca** importa modelos de los módulos para resolverlo — eso lo acoplaría a cada módulo existente, invirtiendo la regla de dependencias.

En su lugar, cada módulo se registra a sí mismo ante `core` al arrancar Django:

```python
# <app>/apps.py
class <App>Config(AppConfig):
    name = '<app>'

    def ready(self) -> None:
        from core.registry_resolvers import register_resolver
        from <app>.resolvers import resolve_<recurso>_by_registry_ids

        register_resolver('<area>', resolve_<recurso>_by_registry_ids)
```

- Los imports van **dentro** de `ready()`, nunca a nivel de módulo en `apps.py` (en ese punto no todas las apps están cargadas todavía y puede fallar)
- `<app>/resolvers.py` expone una función `(registry_ids: list[int]) -> dict[int, dict]` que resuelve **en una sola consulta batched** (`registry_id__in=[...]`), nunca una query por id
- `core/registry_resolvers.py` solo mantiene el registro `{área: función}` — no importa nada de ningún módulo
- Quien necesite resolver contenido (ej. `CollectionItemService`) agrupa los `registry_id` por área y llama a `resolve_registry_ids(area, ids)` una sola vez por área presente, nunca una vez por item

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

### Formato de respuesta

Toda respuesta HTTP sigue el formato:

```json
{ "result": "success" | "failure" | "error", "data": <...> }
```

- `result` se determina automáticamente por el status code de la respuesta: `success` (2xx), `failure` (4xx), `error` (5xx)
- `data` se omite por completo si la vista no devuelve contenido (ej. un `delete` exitoso → `{"result": "success"}`, nunca `204 No Content`)
- Implementado vía `core/renderers.py` (`EnvelopeJSONRenderer`) y `core/exception_handlers.py` (`envelope_exception_handler`), registrados en `REST_FRAMEWORK` (`atenea/settings.py`)
- Las vistas **no** construyen el sobre manualmente: devuelven `Response(data, status=...)` como siempre (incluyendo `Response(status=status.HTTP_200_OK)` sin `data` para los `delete`), y el renderer lo envuelve automáticamente según el status code

---

## Schema de base de datos

### Core

**`ResourceType`** — tipos de recurso por módulo

| Campo | Tipo | Notas |
|---|---|---|
| id | PK | |
| name | varchar | "photo", "movie", etc. |
| area | choices | photography, movies, music, computer_science, comics, general |

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

---

## Frontend

### Stack

- **Framework:** Next.js con **App Router**
- **Estilos:** Tailwind CSS
- **Data fetching / estado de servidor:** TanStack Query (React Query)
- **Tipos:** interfaces TypeScript escritas a mano (no generadas desde OpenAPI)
- **Comunicación con el backend:** fetch directo desde el cliente a la API Django (sin proxy de Next.js). Requiere `django-cors-headers` configurado en el backend. La URL base vive en `NEXT_PUBLIC_API_URL`

### Todo client-side

No se usa prefetch en Server Components ni hidratación de TanStack Query. Toda página o componente que necesite datos del backend es un Client Component (`'use client'`) y usa TanStack Query directamente. Las Server Components quedan solo para capas puramente estáticas (layout, estructura) que no leen datos de la API.

### Estructura de carpetas

Capas explícitas, análogas a las del backend, dentro de `frontend/`:

```
frontend/
  app/                  # rutas (App Router) — páginas y layouts, lo más delgado posible
  api/                  # funciones de fetch puras por recurso, sin estado ni hooks
  hooks/                # hooks de TanStack Query (useQuery/useMutation) que envuelven api/
  components/           # componentes de UI, agrupados por módulo cuando aplica
  types/                # interfaces TypeScript de las entidades (Photo, Artist, Tag, Collection, etc.)
  lib/                  # utilidades transversales (cliente HTTP base, helpers)
```

### Responsabilidades por capa

| Capa | Responsabilidad |
|---|---|
| **api/** | Llamadas `fetch` a la API Django. Reciben y devuelven tipos de `types/`. Sin hooks, sin estado, sin JSX |
| **hooks/** | Envuelven funciones de `api/` en `useQuery`/`useMutation`. Manejan query keys, invalidación y caché |
| **components/** | UI. Consumen hooks, nunca llaman `api/` directamente |
| **app/** | Composición de páginas a partir de `components/`. Mínima lógica propia |
| **types/** | Reflejan los serializers del backend. Se actualizan a mano si el backend cambia |

### Reglas

1. **`api/` nunca importa de `hooks/` ni de `components/`** — la dependencia va en un solo sentido: `components → hooks → api`
2. **Un archivo de `api/` por recurso del backend** (ej. `api/photos.ts`, `api/collections.ts`), reflejando los endpoints documentados en la sección API de este archivo
3. **Query keys centralizadas por recurso** (ej. `['photos', id]`), para invalidar caché de forma consistente tras mutaciones
4. **Todas las rutas de API ya usan el sobre `{ result, data }`** (ver sección API) — las funciones de `api/` deben desempaquetar `data` antes de devolver el tipo al resto del frontend, y lanzar un error si `result` no es `"success"`
5. **No se usa ningún form library por ahora** (ej. React Hook Form) salvo que la complejidad de un formulario lo justifique más adelante — se empieza con estado de React simple (`useState`) en los formularios

### Convenciones de estilo TypeScript/React

| Elemento | Convención | Ejemplo |
|---|---|---|
| Componentes | PascalCase | `PhotoCard`, `CollectionGrid` |
| Hooks | camelCase con prefijo `use` | `usePhotos`, `useCreatePhoto` |
| Funciones de `api/` | camelCase, verbo + recurso | `getPhotos`, `createPhoto`, `deletePhoto` |
| Archivos de componentes | PascalCase | `PhotoCard.tsx` |
| Archivos no-componente | camelCase | `photos.ts`, `usePhotos.ts` |
| Tipos/interfaces | PascalCase | `Photo`, `CollectionItem` |

Mismo criterio que en el backend: todos los nombres en inglés, sin excepción.
