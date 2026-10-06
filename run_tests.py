"""Script para ejecutar pruebas desde escenarios JSON."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.application.test_executor import TestExecutor


def main():
    """Ejecuta pruebas desde todos los escenarios disponibles."""
    scenarios_dir = Path(__file__).parent / "scenarios"

    print("=" * 70)
    print("EXECUTOR DE PRUEBAS - TacticalGrid")
    print("=" * 70)

    # Buscar todos los escenarios JSON
    scenario_files = sorted(scenarios_dir.glob("*.json"))

    if not scenario_files:
        print("\n⚠ No se encontraron escenarios en", scenarios_dir)
        return

    print(f"\n📁 Encontrados {len(scenario_files)} escenario(s)\n")

    for scenario_file in scenario_files:
        print(f"\n{'=' * 70}")
        print(f"Ejecutando: {scenario_file.name}")
        print(f"{'=' * 70}")

        try:
            executor = TestExecutor()
            executor.load_scenario(scenario_file)

            print(f"\n✅ Escenario cargado:")
            print(f"   Mapa: {executor.scenario.rows}×{executor.scenario.cols}")
            print(f"   Unidades: {len(executor.scenario.units)}")
            print(f"   Modo de prueba: {executor.scenario.test_mode}")

            # Ejecutar prueba
            results = executor.execute_test()

            # Mostrar resultados formateados
            print("\n" + executor.format_results(results))

            # Análisis adicional para búsqueda
            if results['modo'] == 'busqueda':
                algos = results['algoritmos']
                if all(a.get('exito') for a in algos.values()):
                    print("\n📊 Análisis Comparativo:")
                    print("-" * 60)

                    # Comparar costos
                    bfs_cost = algos['BFS']['costo']
                    ucs_cost = algos['UCS']['costo']
                    a_star_cost = algos['A*']['costo']

                    if ucs_cost < bfs_cost:
                        print(f"  💰 UCS encontró ruta más barata:")
                        print(f"     BFS: {bfs_cost} vs UCS: {ucs_cost} "
                              f"({(1 - ucs_cost/bfs_cost)*100:.1f}% más barata)")

                    # Comparar exploración
                    ucs_explored = algos['UCS']['estados_generados']
                    a_star_explored = algos['A*']['estados_generados']

                    print(f"\n  🎯 A* es más eficiente que UCS:")
                    print(f"     UCS exploró: {ucs_explored} nodos")
                    print(f"     A* exploró: {a_star_explored} nodos "
                          f"({a_star_explored/ucs_explored*100:.1f}%)")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n\n{'=' * 70}")
    print("✅ Ejecución de pruebas completada")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
