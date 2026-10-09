"""Visualizar búsqueda PASO A PASO con controles interactivos."""

import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scenario.loader import ScenarioLoader
from src.application.test_executor import TestExecutor
from src.application.search_tracker import SearchTracker
from src.application.step_visualizer import StepVisualizer


def main():
    print("\n" + "=" * 70)
    print("🎬 VER BÚSQUEDA PASO A PASO")
    print("=" * 70)

    # Seleccionar escenario
    scenarios_dir = Path(__file__).parent / "scenarios"
    scenario_files = sorted(scenarios_dir.glob("*.json"))

    print("\n📁 Escenarios:\n")
    for i, f in enumerate(scenario_files, 1):
        print(f"   {i}. {f.name}")

    while True:
        try:
            choice = int(input("\nSelecciona escenario (número): "))
            if 1 <= choice <= len(scenario_files):
                scenario_file = scenario_files[choice - 1]
                break
        except:
            print("❌ Número inválido")

    # Cargar escenario
    print(f"\n✅ {scenario_file.name}")
    scenario_data = ScenarioLoader.load(scenario_file)
    executor = TestExecutor()
    executor.load_scenario(scenario_file)

    # Crear grafo y costos
    graph = executor.create_graph_from_scenario()
    costs = executor.create_costs_from_scenario(graph)

    # Seleccionar algoritmo
    print("\n🔍 Algoritmos:\n")
    print("   1. BFS")
    print("   2. UCS")

    while True:
        try:
            choice = int(input("\nSelecciona algoritmo (número): "))
            if choice == 1:
                algo_name = "BFS"
                break
            elif choice == 2:
                algo_name = "UCS"
                break
        except:
            print("❌ Número inválido")

    # Obtener start y goal
    start = executor.scenario.get_unit_position("A1")
    goal = executor.scenario.test_objective

    print(f"\n⏳ Rastreando {algo_name}...")
    print(f"   Inicio: {start}")
    print(f"   Objetivo: {goal}\n")

    # Rastrear búsqueda
    tracker = SearchTracker(graph, start, goal, costs)

    if algo_name == "BFS":
        path, cost, explored = tracker.track_bfs()
    else:  # UCS
        path, cost, explored = tracker.track_ucs()

    if not path:
        print(f"❌ {algo_name} no encontró solución")
        return

    print(f"✅ {algo_name} completado")
    print(f"   Pasos: {len(path) - 1}")
    print(f"   Costo: {cost}")
    print(f"   Nodos explorados: {len(explored)}")
    print(f"   Total pasos en visualización: {tracker.total_steps()}")

    # Generar HTML interactivo
    print(f"\n🎨 Generando visualización interactiva...")
    visualizer = StepVisualizer(scenario_data, cell_size=60)
    html_path = visualizer.save_html(tracker, algo_name)

    print(f"✅ Archivo: {Path(html_path).name}")
    print(f"\n🌐 Abriendo en navegador...\n")

    webbrowser.open(f"file://{html_path}")

    print("=" * 70)
    print("CONTROLES DEL NAVEGADOR:")
    print("=" * 70)
    print("\n⏮️  Inicio         - Ir al primer paso")
    print("⬅️  Anterior       - Paso anterior")
    print("➡️  Siguiente      - Siguiente paso")
    print("⏭️  Fin            - Ir al último paso")
    print("🎚️  Deslizador     - Navegar entre pasos")
    print("\n💡 Observa:")
    print("   🟠 Naranja = Nodos explorados")
    print("   🔴 Rojo    = Frontera actual")
    print("   🟢 Verde   = Nodo siendo expandido")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
