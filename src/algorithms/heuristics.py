"""Heurísticas para A* y búsqueda informada."""

from typing import Tuple


def manhattan_distance(pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> int:
    """
    Heurística Manhattan para grids con movimientos en 4 direcciones.

    **Qué intenta estimar**: El costo mínimo para ir de pos_a a pos_b.
    Asume que se puede mover solo en direcciones ortogonales (arriba, abajo, izq, der).

    **Información del estado que utiliza**: Solo las coordenadas (x, y) de ambas posiciones.
    No consulta el mapa, terrenos, ni obstáculos.

    **Costo computacional**: O(1) - suma de diferencias de coordenadas.

    **Admisibilidad**: ✓ SÍ es admisible (nunca sobrestima).
    - Mínimo costo real es cuando cada paso cuesta 1.
    - Manhattan nunca sobrestima porque:
      |dx| + |dy| <= costo_real (siempre hay un camino directo en grid abierto)
    - En presencia de obstáculos, la ruta real es ≥ Manhattan.

    **Cuándo es óptima para discriminación**:
    - Excelente en grids abiertos sin obstáculos.
    - Buena en grids con obstáculos dispersos.
    - Perfecta cuando hay camino "casi directo".

    **Limitación**: No considera terrenos costosos. Si hay zonas prohibidas,
    Manhattan puede subestimar significativamente.

    **IA**:
    - Usa: Suma |df| + |dc| para estimar distancia.
    - Interviene: Guía A* sin sobrestimar (admisible).
    - Validar: h(goal)=0; que h ≤ costo_real; que A* explora < nodos que UCS.

    Args:
        pos_a: Posición actual (fila, columna)
        pos_b: Posición objetivo (fila, columna)

    Returns:
        Estimación del costo restante (entero)
    """
    return abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1])


def euclidean_distance(pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> float:
    """
    Heurística Euclidiana: SOLO ADMISIBLE para movimiento diagonal (8 direcciones).
    ⚠️ NO ES ADMISIBLE para movimiento 4-direccional (arriba, abajo, izq, der).

    **Qué intenta estimar**: La distancia en línea recta entre dos posiciones.
    Asume que se puede mover en cualquier dirección (incluyendo diagonales).

    **Información del estado que utiliza**: Solo las coordenadas (x, y) de ambas posiciones.
    No consulta el mapa ni terrenos.

    **Costo computacional**: O(1) - cálculo algebraico simple.

    **Admisibilidad**:
    - ✓ SÍ admisible si se permite movimiento diagonal a costo 1.
    - ✗ NO admisible para movimiento 4-direccional (SUBESTIMA).
      Ejemplo: (0,0) a (1,1) → Euclidean=√2≈1.41 pero costo real es 2 (derecha+abajo).
    - En este proyecto con movimiento 4-directional, puede encontrar rutas subóptimas.

    **Limitación en TacticalGrid**:
    Como el proyecto solo permite 4 direcciones (no diagonal),
    Euclidean subestima y NO garantiza optimalidad en A*.

    **IA**:
    - Usa: Distancia euclidiana √(df² + dc²).
    - Interviene: Subestima en 4-dir → NO óptima en A*.
    - Validar: Comparar A*-Euclidean vs A*-Manhattan: resultados pueden diferir.

    Args:
        pos_a: Posición actual (fila, columna)
        pos_b: Posición objetivo (fila, columna)

    Returns:
        Estimación del costo restante (float)
    """
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]
    return (dx**2 + dy**2) ** 0.5


def chebyshev_distance(pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> int:
    """
    Heurística Chebyshev: SOLO ADMISIBLE para movimiento diagonal (8 direcciones).
    ⚠️ NO ES ADMISIBLE para movimiento 4-direccional (arriba, abajo, izq, der).

    **Qué intenta estimar**: Pasos mínimos si se permite movimiento diagonal.
    En ajedrez, es cómo se mueve un rey (máximo de cambios en cualquier dirección).

    **Información del estado que utiliza**: Solo las coordenadas (x, y).

    **Costo computacional**: O(1) - máximo de dos diferencias.

    **Admisibilidad**:
    - ✓ SÍ admisible cuando el movimiento diagonal cuesta 1 (8-directional).
    - ✗ NO admisible para movimiento 4-direccional (SUBESTIMA).
      Ejemplo: (0,0) a (1,1) → Chebyshev=max(1,1)=1 pero costo real es 2 (derecha+abajo).
    - En este proyecto con movimiento 4-directional, puede encontrar rutas subóptimas.

    **Limitación en TacticalGrid**:
    Como el proyecto solo permite 4 direcciones (no diagonal),
    Chebyshev subestima significativamente y NO garantiza optimalidad en A*.

    **IA**:
    - Usa: Máximo de cambios max(|df|, |dc|).
    - Interviene: Subestima mucho en 4-dir → NO usar en A*.
    - Validar: Que A*-Chebyshev explora > nodos que A*-Manhattan.

    Args:
        pos_a: Posición actual (fila, columna)
        pos_b: Posición objetivo (fila, columna)

    Returns:
        Estimación del costo restante (entero)
    """
    return max(abs(pos_a[0] - pos_b[0]), abs(pos_a[1] - pos_b[1]))


def manhattan_weighted_by_terrain(pos_a: Tuple[int, int], pos_b: Tuple[int, int],
                                  min_cost: float = 1.0) -> float:
    """
    Heurística propia: Manhattan escalada por costo mínimo de terreno.

    **Propósito**: Mejora Manhattan considerando terrenos costosos.
    Justificación: Si todos los terrenos cuesta ≥min_cost, el costo restante
    es ≥ Manhattan * min_cost. Más informativa que Manhattan en mapas con
    terrenos variados (pasto=1, montaña=5, etc).

    **Fórmula**: h(n) = (|df| + |dc|) * min_cost
    donde min_cost es el costo mínimo de un paso en cualquier terreno transitable.

    **Información del estado que utiliza**:
    - Coordenadas (x, y) de ambas posiciones
    - Costo mínimo de terreno transitable en el escenario

    **Costo computacional**: O(1) - suma + multiplicación.

    **Admisibilidad**: ✓ SÍ es admisible si min_cost ≤ costo_real_por_paso.
    Demostración:
    - Costo mínimo por paso es min_cost
    - Manhattan pasos = |df| + |dc|
    - Costo total mínimo ≥ (|df| + |dc|) * min_cost
    - Por lo tanto h(n) nunca sobrestima

    **Ventaja sobre Manhattan**:
    - En mapas con terrenos costosos, explora menos nodos
    - Ej: mapa con camino=1, montaña=5: esta heurística es 5x más informativa
    - Mantiene optimalidad de A* (sigue siendo admisible)

    **Limitación**:
    - Requiere conocer min_cost previamente (debe pasarse como parámetro)
    - Si min_cost se estima mal, pierde admisibilidad

    **IA**:
    - Usa: Manhattan * min_cost (escala por terreno).
    - Interviene: Mejor guía en mapas con terrenos caros vs Manhattan.
    - Validar: Que es admisible (h ≤ costo_real); que A* explora < nodos.

    Args:
        pos_a: Posición actual (fila, columna)
        pos_b: Posición objetivo (fila, columna)
        min_cost: Costo mínimo de un paso (default 1.0)

    Returns:
        Estimación del costo restante (float)
    """
    manhattan = abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1])
    return float(manhattan * min_cost)


# Heurística nula (para comparar UCS con A*)
def zero_heuristic(pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> int:
    """
    Heurística trivial que siempre retorna 0.

    **Propósito**: Usar A* con h(n)=0 convierte A* en UCS.
    Útil para experimentar y ver el impacto de la heurística.

    **Admisibilidad**: ✓ SÍ (h(n)=0 siempre es admisible, es lo menos informativo).

    **IA**:
    - Usa: h=0 para baseline (A* sin heurística = UCS).
    - Interviene: Desactiva guía para medir impacto.
    - Validar: Que A*(h=0) ≈ UCS en exploración; que A*(Manhattan) < A*(h=0).

    Args:
        pos_a: Posición actual
        pos_b: Posición objetivo

    Returns:
        Siempre 0
    """
    return 0
