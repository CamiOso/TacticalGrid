"""Ejemplos usando el sistema de escenarios JSON."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario
from src.algorithms.search import bfs, dfs, ucs, a_star
from src.algorithms.heuristics import manhattan_distance


def create_graph_from_scenario(scenario: Scenario) -> dict:
    """
    Convierte un escenario a un grafo de adyacencia.

    Cada celda transitable es un nodo, conectada con sus vecinos adyacentes.
    """
    graph = {}
    rows = scenario.rows
    cols = scenario.cols
    terrain_types = scenario.terrain_types

    for r in range(rows):
        for c in range(cols):
            terrain = scenario.get_terrain_type(r, c)
            if terrain_types[terrain]['transitable']:
                graph[(r, c)] = []
                # Vecinos: arriba, abajo, izq, der
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        neighbor_terrain = scenario.get_terrain_type(nr, nc)
                        if terrain_types[neighbor_terrain]['transitable']:
                            graph[(r, c)].append((nr, nc))

    return graph


def create_costs_from_scenario(scenario: Scenario, graph: dict) -> dict:
    """Extrae costos de aristas desde el escenario."""
    costs = {}
    terrain_types = scenario.terrain_types

    for node in graph:
        for neighbor in graph[node]:
            neighbor_terrain = scenario.get_terrain_type(neighbor[0], neighbor[1])
            cost = terrain_types[neighbor_terrain]['costo']
            costs[(node, neighbor)] = cost

    return costs


def ejemplo_1_cargar_escenario():
    """Ejemplo 1: Cargar y validar un escenario JSON."""
    print("=" * 70)
    print("EJEMPLO 1: Cargar Escenario JSON")
    print("=" * 70)

    scenario_path = Path(__file__).parent / "scenarios" / "ejemplo_basico.json"

    try:
        scenario = Scenario(ScenarioLoader.load(scenario_path))
        print(f"\n✅ Escenario cargado: {scenario}")
        print(f"\nDetalles del escenario:")
        print(f"  - Mapa: {scenario.rows} × {scenario.cols}")
        print(f"  - Unidades: {len(scenario.units)}")
        print(f"  - Recurso en: {scenario.resource_position}")
        print(f"  - Turno actual: {scenario.current_turn}")
        print(f"  - Profundidad Minimax: {scenario.max_minimax_depth}")

        print(f"\nUnidades:")
        for unit in scenario.units:
            pos = (unit['fila'], unit['columna'])
            print(f"  - {unit['id']} (Team {unit['bando']}): {pos}")

        print(f"\nBases:")
        for bando, pos in scenario.bases.items():
            print(f"  - Team {bando}: {pos}")

    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_2_busqueda_en_escenario():
    """Ejemplo 2: Realizar búsqueda en escenario JSON."""
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Búsqueda en Escenario JSON")
    print("=" * 70)

    scenario_path = Path(__file__).parent / "scenarios" / "ejemplo_basico.json"

    try:
        scenario = Scenario(ScenarioLoader.load(scenario_path))
        print(f"\nEscenario: {scenario}")

        # Construir grafo desde escenario
        graph = create_graph_from_scenario(scenario)
        costs = create_costs_from_scenario(scenario, graph)

        print(f"Grafo generado: {len(graph)} nodos transitables")

        # Configurar búsqueda desde JSON
        start = scenario.get_unit_position(scenario.test_unit_start)
        goal = scenario.test_objective

        print(f"Búsqueda: {start} → {goal}")

        # Ejecutar BFS
        print(f"\n1. BFS (menor cantidad de pasos):")
        result_bfs = bfs(graph, start, goal)
        if result_bfs.path:
            print(f"   ✅ Camino encontrado: {len(result_bfs.path)-1} movimientos")
            print(f"   Costo: {result_bfs.cost}, Nodos explorados: {result_bfs.explored}")
        else:
            print(f"   ❌ No hay camino")

        # Ejecutar UCS
        print(f"\n2. UCS (costo mínimo):")
        result_ucs = ucs(graph, start, goal, costs)
        if result_ucs.path:
            print(f"   ✅ Camino encontrado: {len(result_ucs.path)-1} movimientos")
            print(f"   Costo: {result_ucs.cost}, Nodos explorados: {result_ucs.explored}")
        else:
            print(f"   ❌ No hay camino")

        # Ejecutar A*
        print(f"\n3. A* con Manhattan (informado, más eficiente):")
        result_a_star = a_star(graph, start, goal, manhattan_distance, costs)
        if result_a_star.path:
            print(f"   ✅ Camino encontrado: {len(result_a_star.path)-1} movimientos")
            print(f"   Costo: {result_a_star.cost}, Nodos explorados: {result_a_star.explored}")
        else:
            print(f"   ❌ No hay camino")

        # Comparativa
        if result_bfs.path and result_ucs.path and result_a_star.path:
            print(f"\n{'Algoritmo':<15} {'Movimientos':<15} {'Costo':<10} {'Explorados':<12}")
            print("-" * 52)
            print(f"{'BFS':<15} {len(result_bfs.path)-1:<15} {result_bfs.cost:<10} {result_bfs.explored:<12}")
            print(f"{'UCS':<15} {len(result_ucs.path)-1:<15} {result_ucs.cost:<10} {result_ucs.explored:<12}")
            print(f"{'A* Manhattan':<15} {len(result_a_star.path)-1:<15} {result_a_star.cost:<10} {result_a_star.explored:<12}")

            print(f"\n📊 Análisis:")
            print(f"  - UCS costo vs BFS: {result_ucs.cost} vs {result_bfs.cost} " +
                  f"({'más barato' if result_ucs.cost < result_bfs.cost else 'igual'})")
            print(f"  - A* eficiencia: {result_a_star.explored}/{result_ucs.explored} " +
                  f"= {result_a_star.explored/result_ucs.explored*100:.1f}% nodos de UCS")

    except Exception as e:
        print(f"❌ Error: {e}")


def ejemplo_3_terrenos_costosos():
    """Ejemplo 3: Crear escenario con terrenos de costos variables."""
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Terrenos con Costos Variables")
    print("=" * 70)

    # Crear un escenario en memoria demostrando cómo los costos afectan
    print("\nDemostración: En un mapa donde hay 2 rutas:")
    print("  Ruta A: 5 pasos en pasto (costo 2 c/u) = costo total 10")
    print("  Ruta B: 8 pasos en camino (costo 1 c/u) = costo total 8")
    print("\n  - BFS elegiría Ruta A (menos pasos)")
    print("  - UCS elegiría Ruta B (menos costo total)")
    print("  - A* elegiría Ruta B (menos costo + heurística)")


if __name__ == "__main__":
    ejemplo_1_cargar_escenario()
    ejemplo_2_busqueda_en_escenario()
    ejemplo_3_terrenos_costosos()

    print("\n" + "=" * 70)
    print("✅ Ejemplos completados")
    print("=" * 70)
