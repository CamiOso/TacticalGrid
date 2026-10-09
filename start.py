"""Script principal: ejecuta TODO el proyecto paso a paso."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.application.test_executor import TestExecutor


def main():
    print("\n" + "=" * 80)
    print("🎮 TACTICALRID - PROYECTO COMPLETO")
    print("=" * 80)
    print("\nEste script ejecuta TODOS los escenarios con TODOS los algoritmos")
    print("y muestra qué encontró cada uno.\n")

    scenarios_dir = Path(__file__).parent / "scenarios"
    scenario_files = sorted(scenarios_dir.glob("*.json"))

    if not scenario_files:
        print("❌ No se encontraron escenarios JSON")
        return

    for scenario_file in scenario_files:
        print("\n" + "=" * 80)
        print(f"📁 ESCENARIO: {scenario_file.name}")
        print("=" * 80)

        try:
            executor = TestExecutor()
            executor.load_scenario(scenario_file)

            # Mostrar info del escenario
            print(f"\n📊 Información del mapa:")
            print(f"   Tamaño: {executor.scenario.rows}×{executor.scenario.cols}")
            print(f"   Unidades: {len(executor.scenario.units)}")
            print(f"   Bases: {list(executor.scenario.bases.keys())}")
            print(f"   Recurso: {executor.scenario.resource_position}")

            # Ejecutar todas las búsquedas
            results = executor.execute_test()

            # Mostrar resultados
            print(f"\n🔍 RESULTADOS DE BÚSQUEDA:")
            print(f"\n{'Algoritmo':<12} {'Éxito':<8} {'Movimientos':<15} {'Costo':<20} {'Explorados':<12}")
            print("-" * 70)

            for algo_name, algo_result in results['algoritmos'].items():
                exito = "✅" if algo_result.get('exito') else "❌"
                movimientos = algo_result.get('movimientos', '-')
                costo = algo_result.get('costo', '-')
                costo_real = algo_result.get('costo_real')
                explorados = algo_result.get('estados_generados', '-')

                if costo_real:
                    costo_str = f"{costo}/{costo_real}"
                else:
                    costo_str = str(costo)

                print(f"{algo_name:<12} {exito:<8} {str(movimientos):<15} {costo_str:<20} {str(explorados):<12}")

            # Análisis comparativo
            algos = results['algoritmos']
            if all(a.get('exito') for a in algos.values()):
                print(f"\n💡 ANÁLISIS:")

                bfs_cost = algos['BFS'].get('costo_real', algos['BFS']['costo'])
                ucs_cost = algos['UCS']['costo']
                a_star_cost = algos['A*']['costo']

                if ucs_cost < bfs_cost:
                    diff = ((bfs_cost - ucs_cost) / ucs_cost) * 100
                    print(f"   → UCS encontró ruta más BARATA que BFS: {diff:.0f}% menos costo")

                if a_star_cost == ucs_cost:
                    ucs_explored = algos['UCS']['estados_generados']
                    a_star_explored = algos['A*']['estados_generados']
                    pct = (a_star_explored / ucs_explored) * 100
                    print(f"   → A* es más EFICIENTE que UCS: exploró {pct:.0f}% de nodos")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ EJECUCIÓN COMPLETADA")
    print("=" * 80)
    print("\n📝 PRÓXIMAS OPCIONES:\n")
    print("   1. Ver visualizaciones HTML:")
    print("      python visualize_search.py\n")
    print("   2. Ejecutar tests unitarios:")
    print("      python -m pytest tests/ -v\n")
    print("   3. Ver ejemplos de algoritmos:")
    print("      python examples_search.py\n")


if __name__ == "__main__":
    main()
