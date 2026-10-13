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

    Args:
        pos_a: Posición actual (fila, columna)
        pos_b: Posición objetivo (fila, columna)

    Returns:
        Estimación del costo restante (entero)
    """
    return max(abs(pos_a[0] - pos_b[0]), abs(pos_a[1] - pos_b[1]))


# Heurística nula (para comparar UCS con A*)
def zero_heuristic(pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> int:
    """
    Heurística trivial que siempre retorna 0.

    **Propósito**: Usar A* con h(n)=0 convierte A* en UCS.
    Útil para experimentar y ver el impacto de la heurística.

    **Admisibilidad**: ✓ SÍ (h(n)=0 siempre es admisible, es lo menos informativo).

    Args:
        pos_a: Posición actual
        pos_b: Posición objetivo

    Returns:
        Siempre 0
    """
    return 0
