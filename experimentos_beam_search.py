"""Experimenta con Beam Search variando k=1,2,4,8."""

import sys
import json
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))

from src.scenario.loader import ScenarioLoader
from src.application.test_executor import TestExecutor
from src.algorithms.search import beam_search
from src.algorithms.heuristics import manhattan_distance


def run_beam_search_experiment(scenario_file: Path, k_values: List[int]) -> Dict:
    """Ejecuta Beam Search con múltiples valores de k."""

    print("\n" + "=" * 80)
    print(f"🔬 EXPERIMENTO: BEAM SEARCH - Variando k")
    print("=" * 80)
    print(f"\nEscenario: {scenario_file.name}\n")

    # Cargar escenario
    executor = TestExecutor()
    executor.load_scenario(scenario_file)

    # Crear grafo y costos
    graph = executor.create_graph_from_scenario()
    costs = executor.create_costs_from_scenario(graph)

    # Obtener start y goal
    scenario = executor.scenario
    start = scenario.get_unit_position("A1")
    goal = scenario.test_objective

    print(f"Inicio: {start}")
    print(f"Objetivo: {goal}\n")

    # Ejecutar con diferentes k
    results = {}
    print(f"{'k':<5} {'Éxito':<8} {'Pasos':<8} {'Costo':<10} {'Explorados':<12} {'Memoria':<8}")
    print("-" * 65)

    for k in k_values:
        result = beam_search(graph, start, goal, manhattan_distance, k=k, costs=costs)

        if result.path:
            movimientos = len(result.path) - 1
            costo = result.cost
            explorados = result.explored
            memoria_frontera = k  # Beam Search limita a k elementos

            print(
                f"{k:<5} {'✅':<8} {movimientos:<8} {costo:<10} {explorados:<12} {memoria_frontera:<8}"
            )

            results[k] = {
                'exito': True,
                'movimientos': movimientos,
                'costo': costo,
                'explorados': explorados,
                'memoria_frontera': memoria_frontera
            }
        else:
            print(f"{k:<5} {'❌':<8} {'-':<8} {'∞':<10} {result.explored:<12} {k:<8}")
            results[k] = {
                'exito': False,
                'explorados': result.explored,
                'memoria_frontera': k
            }

    return results


def analyze_beam_search_results(all_results: Dict) -> str:
    """Analiza los resultados del experimento."""
    print("\n" + "=" * 80)
    print("📊 ANÁLISIS DE RESULTADOS")
    print("=" * 80 + "\n")

    analysis = []

    for scenario_name, results in all_results.items():
        print(f"\n{'─' * 80}")
        print(f"Escenario: {scenario_name}")
        print(f"{'─' * 80}\n")

        k_values = sorted(results.keys())

        # Analizar convergencia
        successful = {k: r for k, r in results.items() if r.get('exito')}

        if successful:
            first_k = k_values[0]
            first_result = results[first_k]

            print("💡 OBSERVACIONES:\n")

            # 1. Éxito vs k
            print("1. **Tasa de éxito:**")
            for k in k_values:
                status = "✅ Solución encontrada" if results[k].get('exito') else "❌ Sin solución"
                print(f"   k={k}: {status}")

            # 2. Exploración vs k
            if successful:
                min_explored = min(r['explorados'] for r in successful.values())
                max_explored = max(r['explorados'] for r in successful.values())
                print(f"\n2. **Exploración:**")
                print(f"   Mínimo explorado: {min_explored} nodos")
                print(f"   Máximo explorado: {max_explored} nodos")
                print(f"   Diferencia: {max_explored - min_explored} nodos ({((max_explored - min_explored) / min_explored * 100):.0f}%)")

            # 3. Calidad de solución
            if len(successful) > 1:
                costs = [r['costo'] for r in successful.values() if 'costo' in r]
                if len(costs) > 1:
                    min_cost = min(costs)
                    max_cost = max(costs)
                    print(f"\n3. **Calidad de solución:**")
                    print(f"   Costo mínimo: {min_cost}")
                    print(f"   Costo máximo: {max_cost}")
                    if min_cost < max_cost:
                        print(f"   Diferencia: {max_cost - min_cost} ({((max_cost - min_cost) / min_cost * 100):.0f}% peor)")

            # 4. Trade-off memoria vs calidad
            print(f"\n4. **Trade-off Memoria vs Calidad:**")
            print(f"   k pequeño (1-2): Menos memoria, peor solución")
            print(f"   k grande (4-8): Más memoria, mejor solución")

            # 5. Recomendación
            k_values_success = [k for k in k_values if results[k].get('exito')]
            if k_values_success:
                best_k = min(k_values_success, key=lambda k: results[k].get('costo', float('inf')))
                best_result = results[best_k]
                print(f"\n5. **Recomendación:**")
                print(f"   Usar k={best_k} para balance óptimo")
                print(f"   (Costo: {best_result['costo']}, Explorados: {best_result['explorados']}, Memoria: {best_k})")

        analysis.append({
            'scenario': scenario_name,
            'results': results
        })

    return analysis


def main():
    """Script principal."""
    print("\n" + "=" * 80)
    print("🔬 EXPERIMENTOS BEAM SEARCH")
    print("=" * 80)
    print("\nEste script experimenta con k=1, 2, 4, 8")
    print("Objetivo: Ver cómo k afecta exploración, costo y memoria\n")

    scenarios_dir = Path(__file__).parent / "scenarios"
    scenario_files = sorted(scenarios_dir.glob("*.json"))

    k_values = [1, 2, 4, 8]
    all_results = {}

    # Ejecutar experimento en cada escenario
    for scenario_file in scenario_files:
        scenario_name = scenario_file.name
        results = run_beam_search_experiment(scenario_file, k_values)
        all_results[scenario_name] = results

    # Análisis global
    analyze_beam_search_results(all_results)

    # Guardar resultados
    output_file = Path(__file__).parent / "experimentos_beam_search_resultados.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "=" * 80)
    print("✅ EXPERIMENTO COMPLETADO")
    print("=" * 80)
    print(f"\n📊 Resultados guardados en: {output_file.name}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
