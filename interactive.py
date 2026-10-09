"""Script interactivo para ejecutar el proyecto paso a paso."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario
from src.application.test_executor import TestExecutor
from src.application.solution_verifier import SolutionVerifier
from src.application.visualizer import MapVisualizer


def print_menu(options):
    """Imprime un menú y retorna la opción seleccionada."""
    print("\n" + "-" * 70)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("-" * 70)
    while True:
        try:
            choice = int(input("Selecciona una opción (número): "))
            if 1 <= choice <= len(options):
                return choice - 1
            print(f"❌ Ingresa un número entre 1 y {len(options)}")
        except ValueError:
            print("❌ Debes ingresar un número")


def show_scenario_info(scenario: Scenario):
    """Muestra información detallada del escenario."""
    print("\n" + "=" * 70)
    print("📊 INFORMACIÓN DEL ESCENARIO")
    print("=" * 70)

    print(f"\n🗺️  MAPA:")
    print(f"   Tamaño: {scenario.rows} × {scenario.cols} ({scenario.rows * scenario.cols} celdas)")

    print(f"\n🏜️  TERRENOS:")
    for terrain_name, terrain_info in scenario.terrain_types.items():
        transitable = "✅ Transitable" if terrain_info['transitable'] else "❌ Bloqueado"
        print(f"   - {terrain_name}: costo={terrain_info['costo']} | {transitable}")

    print(f"\n🚩 BASES:")
    for team, pos in scenario.bases.items():
        print(f"   - Equipo {team}: {pos}")

    print(f"\n💎 RECURSO:")
    print(f"   Posición: {scenario.resource_position}")
    print(f"   Portador: {scenario.resource_carrier}")

    print(f"\n🎖️  UNIDADES:")
    for unit_data in scenario.units:
        pos = (unit_data['fila'], unit_data['columna'])
        print(f"   - {unit_data['id']}: posición={pos}, equipo={unit_data['bando']}")

    print(f"\n🎯 OBJETIVO DE PRUEBA:")
    print(f"   Modo: {scenario.test_mode}")
    if scenario.test_mode == 'busqueda':
        print(f"   Unidad: {scenario.test_config.get('unidad_inicio', 'N/A')}")
        print(f"   Objetivo: {scenario.test_objective}")


def visualize_grid(scenario: Scenario):
    """Visualiza el mapa en texto ASCII."""
    print("\n" + "=" * 70)
    print("🎨 VISUALIZACIÓN DEL MAPA (ASCII)")
    print("=" * 70)

    rows = scenario.rows
    cols = scenario.cols
    terrain_types = scenario.terrain_types

    # Crear representación
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            cell = "?"
            terrain = scenario.get_terrain_type(r, c)

            # Verificar qué hay en esta celda
            if (r, c) in scenario.bases.values():
                cell = "🚩"
            elif (r, c) == scenario.resource_position:
                cell = "💎"
            else:
                unit_found = False
                for unit_data in scenario.units:
                    unit_pos = (unit_data['fila'], unit_data['columna'])
                    if unit_pos == (r, c):
                        team = unit_data['bando']
                        cell = f"[{team}]"
                        unit_found = True
                        break
                if not unit_found:
                    if terrain_types[terrain]['transitable']:
                        cell = "·"
                    else:
                        cell = "█"
            row.append(cell)
        grid.append(row)

    # Imprimir grid
    print("\n   ", end="")
    for c in range(cols):
        print(f"{c:3}", end="")
    print()

    for r, row in enumerate(grid):
        print(f"{r}: ", end="")
        for cell in row:
            print(f"{cell:3}", end="")
        print()

    print("\nLegenda:")
    print("  · = Pasto (transitable)")
    print("  █ = Muro (bloqueado)")
    print("  🚩 = Base")
    print("  💎 = Recurso")
    print("  [A/B] = Unidad")


def execute_algorithm(executor: TestExecutor, scenario: Scenario, algo_name: str):
    """Ejecuta un algoritmo y muestra resultados detallados."""
    print("\n" + "=" * 70)
    print(f"🔍 EJECUTANDO: {algo_name}")
    print("=" * 70)

    # Ejecutar
    results = executor.execute_test()
    algo_result = results['algoritmos'].get(algo_name)

    if not algo_result:
        print(f"❌ Algoritmo {algo_name} no encontrado")
        return None

    if not algo_result.get('exito'):
        print(f"❌ {algo_name} NO encontró solución")
        return None

    # Mostrar resultados
    print(f"\n✅ {algo_name} ENCONTRÓ SOLUCIÓN\n")

    path = algo_result['ruta']
    costo = algo_result['costo']
    costo_real = algo_result.get('costo_real')
    movimientos = algo_result['movimientos']
    explorados = algo_result['estados_generados']

    print(f"📍 CAMINO ENCONTRADO:")
    print(f"   Inicio: {path[0]}")
    for i, pos in enumerate(path[1:], 1):
        print(f"   Paso {i}: {pos}")
    print(f"   Fin: {path[-1]}")

    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Movimientos: {movimientos}")
    if costo_real:
        print(f"   Costo algoritmo: {costo}")
        print(f"   Costo real: {costo_real}")
    else:
        print(f"   Costo: {costo}")
    print(f"   Nodos explorados: {explorados}")

    # Verificar solución
    # Para BFS/DFS usar costo real, para UCS/A* usar costo del algoritmo
    costo_para_verificar = costo_real if costo_real else costo
    verifier = SolutionVerifier(scenario.to_dict())
    is_valid, reporte = verifier.verify_complete_solution(path, costo_para_verificar, results['objetivo'])

    print(f"\n✓ VERIFICACIÓN:")
    print(f"   Camino válido: {'✅' if reporte['valid_path'] else '❌'}")
    print(f"   Costo correcto: {'✅' if reporte['valid_cost'] else '❌'}")
    print(f"   Objetivo alcanzado: {'✅' if reporte['objective_satisfied'] else '❌'}")
    print(f"   Estados válidos: {'✅' if reporte['no_invalid_states'] else '❌'}")

    return path, algo_result


def generate_visualization(executor: TestExecutor, scenario_file: Path, algo_name: str, path):
    """Genera visualización HTML."""
    print(f"\n🎨 GENERANDO VISUALIZACIÓN...")

    visualizer = MapVisualizer(executor.scenario.to_dict(), cell_size=50)
    path_list = [list(p) for p in path]

    output_file = f"visualizacion_interactivo_{algo_name.lower().replace('*', 'star')}.html"
    html_path = visualizer.save_html(output_file, explored_nodes=None, path=path_list)

    print(f"✅ Visualización guardada: {output_file}")
    print(f"📂 Ruta completa: {html_path}")
    print(f"\n🌐 Para abrir en navegador:")
    print(f"   xdg-open {output_file}")

    return html_path


def main():
    print("\n" + "=" * 70)
    print("🎮 TACTICALRID - MODO INTERACTIVO")
    print("=" * 70)
    print("\nTu controlas cada paso del proyecto")
    print("Verás qué hace cada algoritmo y por qué\n")

    # PASO 1: Elegir escenario
    print("=" * 70)
    print("PASO 1: ELEGIR ESCENARIO")
    print("=" * 70)

    scenarios_dir = Path(__file__).parent / "scenarios"
    scenario_files = sorted(scenarios_dir.glob("*.json"))

    if not scenario_files:
        print("❌ No se encontraron escenarios")
        return

    scenario_names = [f.name for f in scenario_files]
    selected_idx = print_menu(scenario_names)
    scenario_file = scenario_files[selected_idx]

    print(f"\n✅ Escenario seleccionado: {scenario_file.name}")

    # PASO 2: Cargar escenario
    print("\n" + "=" * 70)
    print("PASO 2: CARGAR ESCENARIO")
    print("=" * 70)

    print(f"\n📂 Cargando archivo JSON...")
    scenario_data = ScenarioLoader.load(scenario_file)
    scenario = Scenario(scenario_data)
    print(f"✅ Escenario cargado correctamente")

    # PASO 3: Ver información del escenario
    print("\n" + "=" * 70)
    print("PASO 3: INFORMACIÓN DEL ESCENARIO")
    print("=" * 70)

    show_scenario_info(scenario)

    # PASO 4: Ver mapa en ASCII
    print("\n" + "=" * 70)
    print("PASO 4: VISUALIZAR MAPA")
    print("=" * 70)

    visualize_grid(scenario)

    # PASO 5: Elegir algoritmo
    print("\n" + "=" * 70)
    print("PASO 5: ELEGIR ALGORITMO")
    print("=" * 70)

    algorithms = ["BFS", "DFS", "UCS", "A*"]
    algo_idx = print_menu(algorithms)
    algo_name = algorithms[algo_idx]

    # PASO 6: Ejecutar algoritmo
    print("\n" + "=" * 70)
    print("PASO 6: EJECUTAR ALGORITMO")
    print("=" * 70)

    executor = TestExecutor()
    executor.load_scenario(scenario_file)

    result = execute_algorithm(executor, scenario, algo_name)

    if not result:
        print("\n❌ No se pudo ejecutar el algoritmo")
        return

    path, algo_result = result

    # PASO 7: Generar visualización
    print("\n" + "=" * 70)
    print("PASO 7: GENERAR VISUALIZACIÓN")
    print("=" * 70)

    while True:
        options = [
            "Sí, generar visualización HTML",
            "No, solo ver en consola"
        ]
        choice = print_menu(options)

        if choice == 0:
            generate_visualization(executor, scenario_file, algo_name, path)
            break
        else:
            print("\n✅ Visualización no generada")
            break

    # PASO 8: Comparar con otros algoritmos
    print("\n" + "=" * 70)
    print("PASO 8: COMPARAR CON OTROS ALGORITMOS")
    print("=" * 70)

    print(f"\n¿Quieres ejecutar otros algoritmos para comparar?")
    options = ["Sí", "No"]
    choice = print_menu(options)

    if choice == 0:
        results = executor.execute_test()

        print("\n" + "=" * 70)
        print("📊 COMPARACIÓN DE ALGORITMOS")
        print("=" * 70)

        print(f"\n{'Algoritmo':<12} {'Éxito':<8} {'Movimientos':<15} {'Costo':<20} {'Explorados':<12}")
        print("-" * 70)

        for name, algo_res in results['algoritmos'].items():
            exito = "✅" if algo_res.get('exito') else "❌"
            movimientos = algo_res.get('movimientos', '-')
            costo = algo_res.get('costo', '-')
            costo_real = algo_res.get('costo_real')
            explorados = algo_res.get('estados_generados', '-')

            if costo_real:
                costo_str = f"{costo}/{costo_real}"
            else:
                costo_str = str(costo)

            print(f"{name:<12} {exito:<8} {str(movimientos):<15} {costo_str:<20} {str(explorados):<12}")

    print("\n" + "=" * 70)
    print("✅ SESIÓN COMPLETADA")
    print("=" * 70)
    print("\n¡Gracias por usar TacticalGrid!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Sesión interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
