"""Abre visualización HTML directamente en navegador."""

import sys
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scenario.loader import ScenarioLoader
from src.application.test_executor import TestExecutor
from src.application.visualizer import MapVisualizer


def main():
    print("\n" + "=" * 70)
    print("🎨 VISUALIZACIÓN EN NAVEGADOR")
    print("=" * 70)

    # Seleccionar escenario
    scenarios_dir = Path(__file__).parent / "scenarios"
    scenario_files = sorted(scenarios_dir.glob("*.json"))

    print("\n📁 Escenarios:\n")
    for i, f in enumerate(scenario_files, 1):
        print(f"   {i}. {f.name}")

    while True:
        try:
            choice = int(input("\nSelecciona (número): "))
            if 1 <= choice <= len(scenario_files):
                scenario_file = scenario_files[choice - 1]
                break
        except:
            pass

    # Cargar y ejecutar
    print(f"\n✅ {scenario_file.name}")
    print("⏳ Ejecutando búsqueda...\n")

    executor = TestExecutor()
    executor.load_scenario(scenario_file)
    results = executor.execute_test()

    # Seleccionar algoritmo
    print("🔍 Algoritmos disponibles:\n")
    algos = list(results['algoritmos'].keys())
    for i, algo in enumerate(algos, 1):
        print(f"   {i}. {algo}")

    while True:
        try:
            choice = int(input("\nSelecciona algoritmo (número): "))
            if 1 <= choice <= len(algos):
                algo_name = algos[choice - 1]
                break
        except:
            pass

    algo_result = results['algoritmos'][algo_name]

    if not algo_result.get('exito'):
        print(f"❌ {algo_name} no encontró solución")
        return

    # Generar HTML
    print(f"\n✅ {algo_name} encontró solución")
    print("🎨 Generando visualización...\n")

    path = algo_result['ruta']
    path_list = [list(p) for p in path]

    visualizer = MapVisualizer(executor.scenario.to_dict(), cell_size=60)
    output_file = f"viz_{algo_name.lower().replace('*', 'star')}.html"
    html_path = visualizer.save_html(output_file, explored_nodes=None, path=path_list)

    # Mostrar detalles
    print("=" * 70)
    print(f"📊 SOLUCIÓN - {algo_name}")
    print("=" * 70)
    print(f"\nMovimientos: {algo_result['movimientos']}")
    print(f"Costo: {algo_result['costo']}")
    if algo_result.get('costo_real'):
        print(f"Costo real: {algo_result['costo_real']}")
    print(f"Nodos explorados: {algo_result['estados_generados']}")

    # Abrir en navegador
    print(f"\n🌐 Abriendo en navegador...\n")
    webbrowser.open(f"file://{html_path}")

    print(f"✅ Archivo: {output_file}")
    print(f"📍 Ubicación: {html_path}")
    print("\n¡Revisa tu navegador!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelado")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
