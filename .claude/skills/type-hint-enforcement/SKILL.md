---
name: type-hint-enforcement
description: This skill should be used when the user asks to "check type hints", "fix type hints", "enforce typing", "revisar type hints", "corregir el tipado", "auditar type hints", or wants to verify/fix compliance with the type hinting rules defined in .claude/CLAUDE.md (strict annotations in every layer, the TYPE_CHECKING pattern for services/views, and the ban on runtime model imports outside repositories/serializers).
---

# Type Hint Enforcement (Atenea)

Enforce the rules in `.claude/CLAUDE.md` under "Convenciones de estilo Python" (regla obligatoria de tipado) and "Type hints", plus the layer-import rule they depend on ("Modelos solo en repositorios y serializers").

## Reglas a validar

1. Todo método/función en cualquier capa (`models/`, `repositories/`, `services/`, `serializers/`, `views/`) declara tipos en todos los parámetros (excepto `self`/`cls`) y en el valor de retorno.
2. `repositories/` y `serializers/` pueden importar modelos directamente en runtime y tipar con ellos sin restricción.
3. `services/` y `views/` NO importan modelos en runtime. Cuando necesiten tipar con una clase de modelo:
   - Agregar `from __future__ import annotations` como primer import del archivo.
   - Importar el modelo dentro de un bloque `if TYPE_CHECKING:`.
4. Cualquier archivo con un import de modelo bajo `TYPE_CHECKING` debe tener `from __future__ import annotations`, si no las anotaciones fallan en runtime.

Patrón de referencia correcto (ya presente en el repo, úsalo como plantilla):

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from photography.models import Photo


class PhotoService:
    def get_by_id(self, photo_id: int) -> Photo:
        ...
```

## Workflow

1. Correr el checker:
   ```
   python3 .claude/skills/type-hint-enforcement/scripts/check_type_hints.py backend
   ```
   (ajustar el path si el código Django no vive en `backend/`; el script usa `backend` por default si existe).
2. Por cada violación reportada, corregir el archivo correspondiente:
   - **Parámetro/retorno sin tipo** → agregar la anotación (ver "Cómo inferir tipos" abajo).
   - **Import de modelo en runtime dentro de `services/` o `views/`** → moverlo a un bloque `if TYPE_CHECKING:` y agregar `from __future__ import annotations` si falta.
   - **Falta `from __future__ import annotations` con import bajo `TYPE_CHECKING`** → agregarla como primera línea de imports del archivo.
3. Volver a correr el script hasta que imprima `No type hint violations found.` (exit code 0).
4. Reportar al usuario un resumen breve: qué archivos se modificaron y qué tipo de violación se corrigió en cada uno.

No editar nada bajo `migrations/` — CLAUDE.md prohíbe modificar migraciones ya aplicadas y el script ya las excluye.

## Cómo inferir tipos

- IDs (`*_id`, p. ej. `photo_id`, `registry_id`, `resource_type_id`) → `int`.
- Instancias de modelo recibidas/devueltas → la clase del modelo (import directo en `repositories`/`serializers`; `TYPE_CHECKING` + `from __future__ import annotations` en `services`/`views`).
- Métodos que no retornan nada (p. ej. `delete`) → `-> None`.
- `**kwargs` que representan campos variables de un modelo → `**kwargs: Any` (patrón ya usado en `photography/services/photo_service.py` y `photography/repositories/photo_repository.py`).
- Texto libre (`reference`, `name`, `title`, etc.) → `str`.
- QuerySets devueltos por un repositorio → `QuerySet["Model"]` (`from django.db.models import QuerySet`).
- Si el tipo correcto no es evidente por el contexto (llamadas a repositorio, campos del modelo, uso del valor), preguntar al usuario en vez de adivinar — no usar `Any` como salida fácil salvo que ya sea el patrón establecido en el proyecto para ese caso.

## Alcance y límites del script

`scripts/check_type_hints.py` es una aproximación estática vía AST, no un type checker. Detecta:

- Parámetros/retornos sin anotación (no evalúa si el tipo puesto es semánticamente correcto).
- Imports de modelos a nivel de módulo fuera de `if TYPE_CHECKING:` en `services/` y `views/`.
- Falta de `from __future__ import annotations` cuando existe un import de modelo bajo `TYPE_CHECKING`.

No detecta:

- Imports de modelos hechos dentro del cuerpo de una función (import local).
- Si una anotación existente es del tipo correcto (por ejemplo, un parámetro anotado como `str` que en realidad debería ser `int`) — eso requiere revisión humana al aplicar cada corrección.

Usar `--json` para obtener la lista de violaciones en formato estructurado (`path`, `line`, `message`) si se necesita procesarla programáticamente.
