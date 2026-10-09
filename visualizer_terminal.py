"""Visualizador de búsqueda en terminal con mejor formato."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario
from src.application.test_executor import TestExecutor


class TerminalVisualizer:
    """Visualiza búsqueda y resultados en terminal con colores y formato."""

    def __init__(self, scenario: Scenario):
        self.scenario = scenario
        self.rows = scenario.rows
        self.cols = scenario.cols

    def draw_map(self, path=None, explored=None):
        """Dibuja el mapa con el camino y nodos explorados."""
        print("\n" + "=" * 70)
        print("🗺️  MAPA CON SOLUCIÓN")
        print("=" * 70 + "\n")

        # Crear grid
        grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                cell = self._get_cell_symbol(r, c, path, explored)
                row.append(cell)
            grid.append(row)

        # Encabezado de columnas
        print("     ", end="")
        for c in range(self.cols):
            print(f"{c:4}", end="")
        print()

        # Filas
        for r, row in enumerate(grid):
            print(f"{r:2} | ", end="")
            for cell in row:
                print(f"{cell:4}", end="")
            print()

        print()

    def _get_cell_symbol(self, r, c, path=None, explored=None):
        """Obtiene el símbolo para una celda."""
        terrain = self.scenario.get_terrain_type(r, c)
        terrain_info = self.scenario.terrain_types[terrain]

        # Prioridades de visualización:
        # 1. Inicio del camino
        if path and len(path) > 0 and (r, c) == path[0]:
            return "🔴"  # Inicio

        # 2. Fin del camino
        if path and len(path) > 0 and (r, c) == path[-1]:
            return "🟢"  # Fin

        # 3. Camino en medio
        if path and (r, c) in path:
            idx = path.index((r, c))
            return f"→{idx}"  # Número de paso

        # 4. Nodos explorados (pero no en camino)
        if explored and (r, c) in explored:
            return "⭐"

        # 5. Bases
        if (r, c) in self.scenario.bases.values():
            return "🚩"

        # 6. Recurso
        if (r, c) == self.scenario.resource_position:
            return "💎"

        # 7. Unidades
        for unit in self.scenario.units:
            unit_pos = (unit['fila'], unit['columna'])
            if unit_pos == (r, c):
                return f"[{unit['bando']}]"

        # 8. Terreno
        if terrain_info['transitable']:
            return " · "
        else:
            return " █ "

    def show_path_details(self, path, costo, algo_name, explorados):
        """Muestra detalles del camino encontrado."""
        print("\n" + "=" * 70)
        print(f"📊 DETALLES DE SOLUCIÓN - {algo_name}")
        print("=" * 70 + "\n")

        print(f"📍 CAMINO ({len(path)-1} movimientos):\n")

        # Mostrar cada paso
        print("   Paso | Posición | Terreno | Costo paso | Costo acum")
        print("   " + "-" * 58)

        acum_cost = 0
        for i, pos in enumerate(path):
            r, c = pos
            terrain = self.scenario.get_terrain_type(r, c)
            terrain_cost = self.scenario.terrain_types[terrain]['costo']

            # Para el primer paso, no hay costo
            if i == 0:
                step_cost = 0
                acum_cost = 0
            else:
                step_cost = terrain_cost
                acum_cost += terrain_cost

            print(
                f"   {i:4} | {str(pos):8} | {terrain:7} | "
                f"{step_cost:10} | {acum_cost:10}"
            )

        print(f"\n   Costo Total: {acum_cost}")
        print(f"   Nodos explorados: {explorados}")

    def show_algorithm_comparison(self, results):
        """Muestra comparación de algoritmos."""
        print("\n" + "=" * 70)
        print("📈 COMPARACIÓN DE ALGORITMOS")
        print("=" * 70 + "\n")

        print(f"{'Algoritmo':<12} {'Éxito':<8} {'Movimientos':<15} {'Costo':<15} {'Explorados':<12}")
        print("-" * 70)

        algos = results['algoritmos']

        for algo_name in ['BFS', 'DFS', 'UCS', 'A*']:
            if algo_name not in algos:
                continue

            algo_result = algos[algo_name]
            exito = "✅" if algo_result.get('exito') else "❌"
            movimientos = algo_result.get('movimientos', '-')
            costo = algo_result.get('costo', '-')
            costo_real = algo_result.get('costo_real')
            explorados = algo_result.get('estados_generados', '-')

            if costo_real:
                costo_str = f"{costo}/{costo_real}"
            else:
                costo_str = str(costo)

            print(
                f"{algo_name:<12} {exito:<8} {str(movimientos):<15} "
                f"{costo_str:<15} {str(explorados):<12}"
            )

        # Análisis
        print("\n" + "=" * 70)
        print("💡 ANÁLISIS")
        print("=" * 70 + "\n")

        if all(a.get('exito') for a in algos.values()):
            bfs_cost = algos['BFS'].get('costo_real', algos['BFS']['costo'])
            ucs_cost = algos['UCS']['costo']
            a_star_cost = algos['A*']['costo']

            # Comparación BFS vs UCS
            if ucs_cost < bfs_cost:
                diff = ((bfs_cost - ucs_cost) / ucs_cost) * 100
                print(f"🔴 BFS eligió ruta MÁS CARA:")
                print(f"   BFS: {bfs_cost} costo")
                print(f"   UCS: {ucs_cost} costo")
                print(f"   Diferencia: {diff:.0f}% más caro\n")

                print(f"💰 Razón:")
                print(f"   BFS minimiza PASOS (4 movimientos)")
                print(f"   UCS minimiza COSTO (costo total menor)\n")

            # Comparación UCS vs A*
            ucs_explored = algos['UCS']['estados_generados']
            a_star_explored = algos['A*']['estados_generados']

            if a_star_explored < ucs_explored:
                pct = (a_star_explored / ucs_explored) * 100
                print(f"⚡ A* es más EFICIENTE que UCS:")
                print(f"   UCS exploró: {ucs_explored} nodos")
                print(f"   A* exploró: {a_star_explored} nodos")
                print(f"   Eficiencia: {pct:.0f}%\n")

                print(f"🎯 Razón:")
                print(f"   A* usa HEURÍSTICA para guiar la búsqueda")
                print(f"   Explora menos nodos hacia el objetivo\n")


def main():
    """Script principal de visualización en terminal."""
    print("\n" + "=" * 70)
    print("🎮 VISUALIZADOR DE TERMINAL - TacticalGrid")
    print("=" * 70)

    # Elegir escenario
    scenarios_dir = Path(__file__).parent / "scenarios"
    scenario_files = sorted(scenarios_dir.glob("*.json"))

    print("\n📁 Escenarios disponibles:\n")
    for i, f in enumerate(scenario_files, 1):
        print(f"   {i}. {f.name}")

    while True:
        try:
            choice = int(input("\nSelecciona escenario (número): "))
            if 1 <= choice <= len(scenario_files):
                scenario_file = scenario_files[choice - 1]
                break
            print("❌ Número inválido")
        except ValueError:
            print("❌ Debes ingresar un número")

    print(f"\n✅ Escenario: {scenario_file.name}")

    # Cargar y ejecutar
    print("\n📊 Cargando y ejecutando búsqueda...")
    executor = TestExecutor()
    executor.load_scenario(scenario_file)
    scenario = executor.scenario

    # Visualizar mapa sin solución
    visualizer = TerminalVisualizer(scenario)
    visualizer.draw_map()

    # Ejecutar búsqueda
    results = executor.execute_test()

    # Mostrar información del escenario
    print("=" * 70)
    print("📋 INFORMACIÓN DEL ESCENARIO")
    print("=" * 70)
    print(f"\nMapa: {scenario.rows}×{scenario.cols}")
    print(f"Unidades: {len(scenario.units)}")
    print(f"Objetivo: {results['objetivo']}")

    # Mostrar resultados de cada algoritmo
    algos_to_show = ['BFS', 'DFS', 'UCS', 'A*']

    for algo_name in algos_to_show:
        if algo_name not in results['algoritmos']:
            continue

        algo_result = results['algoritmos'][algo_name]

        if not algo_result.get('exito'):
            print(f"\n❌ {algo_name}: No encontró solución")
            continue

        path = algo_result['ruta']
        costo = algo_result['costo']
        costo_real = algo_result.get('costo_real')
        costo_mostrar = costo_real if costo_real else costo
        explorados = algo_result['estados_generados']

        # Mostrar mapa con solución
        print(f"\n\n{'=' * 70}")
        print(f"🔍 ALGORITMO: {algo_name}")
        print(f"{'=' * 70}\n")

        visualizer.draw_map(path=path)
        visualizer.show_path_details(path, costo_mostrar, algo_name, explorados)

    # Comparación final
    visualizer.show_algorithm_comparison(results)

    print("\n" + "=" * 70)
    print("✅ VISUALIZACIÓN COMPLETADA")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
