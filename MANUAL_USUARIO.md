# MANUAL DE USUARIO — TacticalGrid

Sistema inteligente de búsqueda y decisión adversarial para un juego táctico 2D.

## 1. Requisitos

- Python 3.8 o superior.
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

### 3.1 Ejecutar todos los escenarios (búsqueda)

```bash
python run_tests.py
```

Carga todos los escenarios JSON de `scenarios/`, visualiza cada mapa en ASCII y ejecuta BFS, DFS, UCS y A* sobre cada uno, mostrando métricas y análisis comparativo.

### 3.2 Ejecutar el modo interactivo

```bash
python interactive.py
```

Guía paso a paso: elegir escenario, ver información, visualizar el mapa, elegir algoritmo (BFS/DFS/UCS/A*), ejecutarlo y verificar la solución.

### 3.3 Ejecutar una partida por turnos (modo adversarial/partida)

```bash
python start.py
```

Ejecuta todos los escenarios. Para los escenarios con `"modo": "adversarial"` o `"modo": "partida"`, el sistema evalúa el estado con Minimax/Alfa-Beta y selecciona una acción (o juega la partida turno a turno).

### 3.4 Ejecutar pruebas automatizadas

```bash
python -m pytest tests/ -v
```

Ejecuta las 86 pruebas de la suite.

### 3.5 Demostrar los casos mínimos del enunciado

```bash
python casos_minimos.py
```

Reproduce los 10 casos mínimos del enunciado (BFS vs DFS, ruta corta vs económica, obstáculo y heurística, comparación de heurísticas, Beam Search, estado compuesto, decisión adversarial, Minimax vs Alfa-Beta, orden de acciones y profundidad).

### 3.6 Generar visualizaciones HTML

```bash
python visualize_search.py
```

Genera archivos HTML con el mapa, terrenos, bases, unidades y camino encontrado.

## 4. Formato de escenarios

Los escenarios son archivos JSON en `scenarios/`. La aplicación también acepta escenarios externos suministrados por el profesor, siempre que cumplan el formato común.

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

Modos de `prueba.modo`:

- `"busqueda"`: resolver una navegación con BFS, DFS, UCS o A*.
- `"adversarial"`: evaluar un estado con Minimax/Alfa-Beta y seleccionar una acción.
- `"partida"`: jugar una partida completa por turnos.

## 5. Salida e interpretación

Para una prueba de búsqueda, la salida muestra por algoritmo: éxito, movimientos, costo, estados generados, estados expandidos y tamaño máximo de la frontera.

Para una prueba adversarial, la salida muestra por algoritmo: éxito, valor, nodos generados, nodos evaluados, nodos podados, profundidad alcanzada y la acción seleccionada.

Para una partida, la salida muestra la secuencia de turnos con la acción elegida por cada bando, el valor, los nodos generados/evaluados/podados y el tiempo por decisión, además del ganador y el motivo de fin (ganador, bloqueo o límite de turnos).

## 6. Verificación de soluciones

El módulo `SolutionVerifier` comprueba que un camino sea conexo, transitable, con costo consistente y que alcance el objetivo. Se invoca desde `interactive.py` y desde las pruebas.

## 7. Algoritmos implementados

- No informada: BFS, DFS.
- Basada en costos: UCS.
- Informada: A* (con Manhattan y con heurística propia ponderada por costo).
- Memoria limitada: Beam Search (k configurable).
- Adversarial: Minimax y Minimax con poda alfa-beta (profundidad configurable).

## 8. Autor

Cristian Camilo Osorio Granada — Universidad de Caldas, Sistemas Inteligentes I.
