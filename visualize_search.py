"""Script para visualizar resultados de búsqueda en HTML."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.scenario.loader import ScenarioLoader
from src.application.test_executor import TestExecutor
from src.application.visualizer import MapVisualizer


def visualize_search_result(scenario_file: str, algorithm: str = "A*"):
    """
    Ejecuta búsqueda y genera visualización HTML.

    Parámetros:
        scenario_file: Ruta del escenario JSON
        algorithm: Algoritmo a visualizar ("BFS", "DFS", "UCS", "A*")
    """
    # Cargar escenario y ejecutar búsqueda
    executor = TestExecutor()
    executor.load_scenario(scenario_file)

    print(f"📁 Escenario: {Path(scenario_file).name}")
    print(f"🔍 Ejecutando {algorithm}...\n")

    results = executor.execute_test()

    # Obtener resultado del algoritmo especificado
    if algorithm not in results['algoritmos']:
        print(f"❌ Algoritmo {algorithm} no encontrado")
        return

    algo_result = results['algoritmos'][algorithm]

    if not algo_result.get('exito'):
        print(f"❌ {algorithm} no encontró solución")
        return

    path = algo_result['ruta']
    explored = algo_result['estados_generados']

    print(f"✅ {algorithm} encontró solución")
    print(f"   Camino: {len(path)-1} movimientos")
    print(f"   Costo: {algo_result['costo']}")
    print(f"   Nodos explorados: {explored}\n")

    # Generar visualización
    scenario_data = executor.scenario.to_dict()
    visualizer = MapVisualizer(scenario_data, cell_size=50)

    # Convertir path de tuplas a lista de tuplas para JSON
    path_list = [list(p) for p in path]

    output_file = f"visualizacion_{Path(scenario_file).stem}_{algorithm.replace('*', 'star').lower()}.html"
    html_path = visualizer.save_html(
        output_file,
        explored_nodes=None,  # Podríamos agregar esto si rastreamos explorados
        path=path_list
    )

    print(f"📊 Visualización guardada en:")
    print(f"   {html_path}")
    print(f"\n✨ Abre el archivo en tu navegador para ver el mapa y el camino encontrado")

    return html_path


if __name__ == "__main__":
    # Visualizar diferentes escenarios y algoritmos
    scenarios = [
        ("scenarios/ejemplo_basico.json", "A*"),
        ("scenarios/divergencia_bfs_ucs.json", "UCS"),
        ("scenarios/divergencia_bfs_ucs.json", "BFS"),
    ]

    print("=" * 70)
    print("VISUALIZADOR DE BÚSQUEDA - TacticalGrid")
    print("=" * 70 + "\n")

    for scenario, algo in scenarios:
        try:
            visualize_search_result(scenario, algo)
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")

    print("=" * 70)
    print("✅ Visualizaciones completadas")
    print("=" * 70)
