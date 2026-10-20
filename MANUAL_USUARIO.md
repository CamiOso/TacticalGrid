# MANUAL DE USUARIO — TacticalGrid

Sistema inteligente de búsqueda y decisión adversarial para un juego táctico 2D.

## 1. Requisitos

- Python 3.8 o superior (probado con 3.11).
- Sin dependencias externas (solo la biblioteca estándar).
- Para las pruebas automatizadas: `pytest` (opcional).

## 2. Instalación

Clonar el repositorio y ubicarse en la raíz del proyecto:

```bash
git clone <url-del-repositorio>
cd Proyecto
```

No se requiere instalar dependencias.

## 3. Ejecución

### 3.1 Punto de entrada único (`start.py`)

`start.py` es el punto de entrada principal. Ejecuta todos los escenarios de
`scenarios/` (o uno específico) y despacha por el modo de cada `prueba.modo`.

```bash
python start.py                                               # todos los escenarios
python start.py scenarios/ejemplo_basico.json                  # un escenario concreto
```

Con el campo `prueba.modo`:

| Modo | Qué hace |
|------|----------|
| `busqueda` | Resuelve una navegación con BFS/DFS/UCS/A*/Beam y verifica la solución. |
| `partida` | Simula una partida completa por turnos entre dos bandos. |
| `adversarial` | Evalúa un estado con Minimax/alfa-beta y selecciona una acción. |

### 3.2 Banderas de `start.py`

| Bandera | Valores | Aplica a |
|---------|---------|----------|
| `--algoritmo` | `BFS`, `DFS`, `UCS`, `A*`/`ASTAR`, `BEAM` | búsqueda |
| `--algoritmo` | `MINIMAX` (puro) o `ALFA_BETA` (con poda) | partida/adversarial |
| `--heuristica` | `manhattan`, `manhattan_pasos`, `distancia_bfs`, `zero` | A* y Beam |
| `--k` | entero ≥ 1 | Beam Search |
| `--profundidad` | entero ≥ 1 | partida/adversarial |
| `--no-preguntar` | — | usa la sugerencia del JSON sin menú |

Ejemplos:

```bash
python start.py scenarios/terrenos_costosos.json --algoritmo A_ESTRELLA --heuristica distancia_bfs
python start.py scenarios/divergencia_bfs_ucs.json --algoritmo BEAM --k 4
python start.py scenarios/partida_simple.json --algoritmo ALFA_BETA --profundidad 2
python start.py scenarios/mapa_grande_adversarial.json --algoritmo MINIMAX --profundidad 3
```

Sin banderas y en terminal interactiva, aparece un menú numerado para elegir
algoritmo, heurística y ancho del haz `k`; el JSON queda como sugerencia
(`--no-preguntar` evita el menú).

### 3.3 Mapas de desarrollo (20×20, 3 unidades por bando)

- `scenarios/mapa_grande.json` — búsqueda 20×20 (A1 → base B, con muros y costos).
- `scenarios/mapa_grande_partida.json` — partida 20×20 (3 vs 3 unidades).
- `scenarios/mapa_grande_adversarial.json` — decisión adversarial 20×20 (3 vs 3).

```bash
python start.py scenarios/mapa_grande.json --algoritmo UCS --no-preguntar
```

### 3.4 Scripts auxiliares (en `scripts/`)

```bash
python scripts/casos_minimos.py           # los 10 casos mínimos del enunciado
python scripts/examples_search.py         # ejemplos de BFS/DFS/UCS/A*
python scripts/examples_adversarial.py    # ejemplos de Minimax y alfa-beta
python scripts/examples_agents.py         # ejemplos de agentes
python scripts/experimentos_beam_search.py # experimento Beam Search (k=1,2,4,8)
python scripts/visualize_search.py        # visualizaciones HTML
python scripts/interactive.py             # modo interactivo guiado paso a paso
```

### 3.5 Ejecutar pruebas automatizadas

```bash
python -m pytest tests/ -v
```

Ejecuta las 111 pruebas de la suite (búsqueda, heurísticas, adversarial, reglas
del recurso, casos mínimos, validación y verificación de soluciones).

## 4. Formato de escenarios

Los escenarios son archivos JSON en `scenarios/`. La aplicación también acepta
escenarios externos suministrados por el profesor, siempre que cumplan el formato
común. La carga es "todo o nada": si hay algún error, se lista y no se ejecuta nada.

Campos principales:

- `version`: versión del formato (ej. `"1.0"`).
- `mapa.filas` / `mapa.columnas`: dimensiones de la cuadrícula.
- `tipos_terreno`: catálogo de terrenos con `costo` y `transitable`.
- `terreno`: matriz de tipos de terreno.
- `bases.A` / `bases.B`: posiciones de las bases.
- `recurso`: posición del recurso.
- `unidades`: lista con `id`, `bando`, `tipo`, `fila`, `columna`.
- `turno`: `"A"` o `"B"`.
- `juego.portador_recurso`: unidad que transporta el recurso (o `null`).
- `juego.profundidad_maxima_minimax`: profundidad de Minimax.
- `prueba`: configuración de la prueba (`modo`, `unidad_inicio`, `objetivo`, etc.).

## 5. Salida e interpretación

Para una prueba de búsqueda, la salida muestra por algoritmo: éxito, camino, número
de movimientos, costo, estados generados, estados expandidos, máximo de frontera y
**tiempo de ejecución en milisegundos** (`tiempo_ms`), seguido de la verificación
independiente (camino válido, costo correcto, objetivo alcanzado, sin estados inválidos).

Para una prueba adversarial, muestra: acción elegida, valor, nodos generados, nodos
evaluados, podas y profundidad efectiva.

Para una partida, muestra la secuencia de turnos con la acción de cada bando, el
valor y las métricas por decisión, más el ganador o el empate por límite de turnos.

## 6. Verificación de soluciones

El módulo `SolutionVerifier` comprueba que un camino sea conexo, transitable, con
costo consistente y que alcance el objetivo. `start.py` lo invoca automáticamente en
el modo `busqueda`.

## 7. Algoritmos implementados

- No informada: BFS, DFS.
- Basada en costos: UCS.
- Informada: A* (Manhattan, Manhattan ponderada por costo mínimo y `distancia_bfs`).
- Memoria limitada: Beam Search (k configurable).
- Adversarial: Minimax y Minimax con poda alfa-beta (profundidad configurable).

## 8. Autor

Cristian Camilo Osorio Granada — Universidad de Caldas, Sistemas Inteligentes I.
