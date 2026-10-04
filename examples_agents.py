"""Ejemplos de uso de agentes en TacticalGrid."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agents.unit import UnitBFS, UnitDFS
from src.agents.smart_unit import SmartUnit, SmartUnitEuclidean
from src.agents.tactical_unit import TacticalUnit, TacticalUnitAlfaBeta


def crear_mapa_simple() -> dict:
    """Crear un mapa simple para pathfinding."""
    # Mapa 5x5 con obstáculos (1 = obstáculo, 0 = libre)
    mapa = {
        (0, 0): [(0, 1), (1, 0)],
        (0, 1): [(0, 0), (0, 2), (1, 1)],
        (0, 2): [(0, 1), (0, 3), (1, 2)],
        (0, 3): [(0, 2), (0, 4), (1, 3)],
        (0, 4): [(0, 3), (1, 4)],
        (1, 0): [(0, 0), (1, 1), (2, 0)],
        (1, 1): [(0, 1), (1, 0), (1, 2), (2, 1)],
        (1, 2): [(0, 2), (1, 1), (1, 3), (2, 2)],
        (1, 3): [(0, 3), (1, 2), (1, 4), (2, 3)],
        (1, 4): [(0, 4), (1, 3), (2, 4)],
        (2, 0): [(1, 0), (2, 1), (3, 0)],
        (2, 1): [(1, 1), (2, 0), (2, 2), (3, 1)],
        (2, 2): [(1, 2), (2, 1), (2, 3), (3, 2)],
        (2, 3): [(1, 3), (2, 2), (2, 4), (3, 3)],
        (2, 4): [(1, 4), (2, 3), (3, 4)],
        (3, 0): [(2, 0), (3, 1), (4, 0)],
        (3, 1): [(2, 1), (3, 0), (3, 2), (4, 1)],
        (3, 2): [(2, 2), (3, 1), (3, 3), (4, 2)],
        (3, 3): [(2, 3), (3, 2), (3, 4), (4, 3)],
        (3, 4): [(2, 4), (3, 3), (4, 4)],
        (4, 0): [(3, 0), (4, 1)],
        (4, 1): [(3, 1), (4, 0), (4, 2)],
        (4, 2): [(3, 2), (4, 1), (4, 3)],
        (4, 3): [(3, 3), (4, 2), (4, 4)],
        (4, 4): [(3, 4), (4, 3)],
    }
    return mapa


def visualizar_mapa_5x5(mapa_actual=None):
    """Visualizar mapa 5x5."""
    print("Mapa 5×5:")
    print("     0   1   2   3   4")
    for fila in range(5):
        print(f"{fila}  ", end="")
        for col in range(5):
            if mapa_actual and (fila, col) == mapa_actual:
                print(" @ ", end=" ")  # Posición actual
            else:
                print(" . ", end=" ")
        print()


def ejemplo_1_comparacion_basica():
    """Ejemplo 1: BFS vs DFS en mapa simple."""
    print("=" * 70)
    print("EJEMPLO 1: Comparación BFS vs DFS")
    print("=" * 70)

    mapa = crear_mapa_simple()
    inicio = (0, 0)
    goal = (4, 4)

    print(f"\nMisión: Ir de {inicio} a {goal}")
    visualizar_mapa_5x5(inicio)

    # BFS
    unit_bfs = UnitBFS("Unit1", "TeamA", inicio, goal)
    if unit_bfs.find_path(mapa):
        print(f"\n✅ BFS encontró camino:")
        print(f"  Algoritmo: {unit_bfs.get_algorithm_name()}")
        print(f"  Longitud: {len(unit_bfs.path) - 1} movimientos")
        print(f"  Camino: {' -> '.join(str(p) for p in unit_bfs.path[:5])} ...")
    else:
        print(f"\n❌ BFS no encontró camino")

    # DFS
    unit_dfs = UnitDFS("Unit2", "TeamB", inicio, goal)
    if unit_dfs.find_path(mapa):
        print(f"\n✅ DFS encontró camino:")
        print(f"  Algoritmo: {unit_dfs.get_algorithm_name()}")
        print(f"  Longitud: {len(unit_dfs.path) - 1} movimientos")
        print(f"  Camino: {' -> '.join(str(p) for p in unit_dfs.path[:5])} ...")
    else:
        print(f"\n❌ DFS no encontró camino")


def ejemplo_2_smart_units():
    """Ejemplo 2: SmartUnit con A*."""
    print("\n" + "=" * 70)
    print("EJEMPLO 2: SmartUnit (A* con heurística)")
    print("=" * 70)

    mapa = crear_mapa_simple()
    inicio = (0, 0)
    goal = (4, 4)

    print(f"\nMisión: Ir de {inicio} a {goal}")
    visualizar_mapa_5x5(inicio)

    # A* con Manhattan
    unit_smart = SmartUnit("SmartUnit1", "TeamA", inicio, goal)
    if unit_smart.find_path(mapa):
        print(f"\n✅ A* (Manhattan) encontró camino:")
        print(f"  Algoritmo: {unit_smart.get_algorithm_name()}")
        print(f"  Longitud: {len(unit_smart.path) - 1} movimientos")
        print(f"  Camino: {' -> '.join(str(p) for p in unit_smart.path)}")
    else:
        print(f"\n❌ A* no encontró camino")

    # A* con Euclidean
    unit_euclidean = SmartUnitEuclidean("SmartUnit2", "TeamB", inicio, goal)
    if unit_euclidean.find_path(mapa):
        print(f"\n✅ A* (Euclidean) encontró camino:")
        print(f"  Algoritmo: {unit_euclidean.get_algorithm_name()}")
        print(f"  Longitud: {len(unit_euclidean.path) - 1} movimientos")
    else:
        print(f"\n❌ A* (Euclidean) no encontró camino")


def ejemplo_3_movimiento_automatico():
    """Ejemplo 3: Movimiento automático paso a paso."""
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Movimiento Automático (SmartUnit)")
    print("=" * 70)

    mapa = crear_mapa_simple()
    inicio = (0, 0)
    goal = (4, 4)

    unit = SmartUnit("Soldado1", "TeamA", inicio, goal)

    print(f"\nUnidad: {unit}")
    print(f"Buscando camino de {inicio} a {goal}...")

    if unit.find_path(mapa):
        print(f"✅ Camino encontrado. Longitud: {len(unit.path) - 1}")

        print(f"\nMovimiento simulado:")
        step = 0
        while not unit.has_reached_goal() and step < 10:
            pos = unit.move()
            remaining = unit.get_remaining_distance()
            print(f"  Paso {step + 1}: Posición {pos}, Distancia restante: {remaining}")
            step += 1

        if unit.has_reached_goal():
            print(f"\n🎯 ¡Objetivo alcanzado en {unit.current_step} pasos!")
        else:
            print(f"\n⏸ Simulación pausada después de {step} pasos")
    else:
        print(f"❌ No se encontró camino")


def ejemplo_4_multiples_unidades():
    """Ejemplo 4: Múltiples unidades con diferentes algoritmos."""
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Múltiples Unidades (Diferentes Algoritmos)")
    print("=" * 70)

    mapa = crear_mapa_simple()
    inicio = (0, 0)
    goal = (4, 4)

    print(f"\nMisión: 4 unidades con diferentes algoritmos")
    visualizar_mapa_5x5(inicio)

    units = [
        UnitBFS("Unit1", "TeamA", inicio, goal),
        UnitDFS("Unit2", "TeamA", inicio, goal),
        SmartUnit("Unit3", "TeamA", inicio, goal),
        SmartUnitEuclidean("Unit4", "TeamA", inicio, goal),
    ]

    print(f"\nResultados:")
    for unit in units:
        if unit.find_path(mapa):
            length = len(unit.path) - 1
            algo = unit.get_algorithm_name()
            print(f"  ✅ {unit.unit_id:10s} ({algo:35s}): {length} movimientos")
        else:
            print(f"  ❌ {unit.unit_id:10s}: No encontró camino")


def ejemplo_5_estadisticas():
    """Ejemplo 5: Estadísticas de rendimiento."""
    print("\n" + "=" * 70)
    print("EJEMPLO 5: Estadísticas de Rendimiento")
    print("=" * 70)

    mapa = crear_mapa_simple()
    inicio = (0, 0)
    goal = (4, 4)

    print(f"\nComparativa de algoritmos en mapa 5×5:")
    print(f"Inicio: {inicio}, Objetivo: {goal}\n")

    algorithms = [
        ("BFS", UnitBFS("", "", inicio, goal)),
        ("DFS", UnitDFS("", "", inicio, goal)),
        ("A* Manhattan", SmartUnit("", "", inicio, goal)),
        ("A* Euclidean", SmartUnitEuclidean("", "", inicio, goal)),
    ]

    results = []
    for name, unit in algorithms:
        if unit.find_path(mapa):
            length = len(unit.path) - 1
            results.append((name, length, "✅"))
        else:
            results.append((name, "-", "❌"))

    # Mostrar tabla
    print(f"{'Algoritmo':<20} {'Movimientos':<15} {'Estado':<10}")
    print("-" * 45)
    for name, moves, status in results:
        print(f"{name:<20} {str(moves):<15} {status:<10}")


if __name__ == "__main__":
    ejemplo_1_comparacion_basica()
    ejemplo_2_smart_units()
    ejemplo_3_movimiento_automatico()
    ejemplo_4_multiples_unidades()
    ejemplo_5_estadisticas()

    print("\n" + "=" * 70)
    print("✅ Todos los ejemplos completados")
    print("=" * 70)
