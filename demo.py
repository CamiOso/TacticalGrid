"""Demostración completa del proyecto TacticalGrid."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario
from src.application.test_executor import TestExecutor
from src.application.solution_verifier import SolutionVerifier
from src.application.visualizer import MapVisualizer


def demo():
    """Demostración completa: carga → búsqueda → verificación → visualización."""
    
    print("\n" + "=" * 80)
    print(" 🎮 DEMOSTRACIÓN COMPLETA - TacticalGrid")
    print("=" * 80 + "\n")

    # ========== PASO 1: Cargar Escenario ==========
    print("📁 PASO 1: Cargar Escenario JSON")
    print("-" * 80)
    
    scenario_file = Path(__file__).parent / "scenarios" / "divergencia_bfs_ucs.json"
    print(f"Cargando: {scenario_file.name}")
    
    scenario_data = ScenarioLoader.load(scenario_file)
    scenario = Scenario(scenario_data)
    
    print(f"✅ Escenario cargado")
    print(f"   Mapa: {scenario.rows}×{scenario.cols}")
    print(f"   Unidades: {len(scenario.units)}")
    print(f"   Bases: {list(scenario.bases.keys())}")
    print(f"   Recurso: {scenario.resource_position}")

    # ========== PASO 2: Ejecutar Búsqueda ==========
    print("\n📊 PASO 2: Ejecutar Búsqueda (BFS vs UCS)")
    print("-" * 80)
    
    executor = TestExecutor()
    executor.load_scenario(scenario_file)
    results = executor.execute_test()
    
    print(f"\n{'Algoritmo':<15} {'Éxito':<8} {'Movimientos':<15} {'Costo':<15}")
    print("-" * 53)
    
    for algo_name, algo_result in results['algoritmos'].items():
        if algo_result.get('exito'):
            movimientos = algo_result.get('movimientos', '-')
            costo_info = algo_result.get('costo', '-')
            costo_real = algo_result.get('costo_real')
            
            if costo_real:
                costo_str = f"{costo_info}/{costo_real}"
            else:
                costo_str = str(costo_info)
            
            print(f"{algo_name:<15} ✅ {movimientos:<15} {costo_str:<15}")

    # ========== PASO 3: Verificar Soluciones ==========
    print("\n✓ PASO 3: Verificar Soluciones")
    print("-" * 80)
    
    verifier = SolutionVerifier(scenario_data)
    
    for algo_name in ['BFS', 'UCS']:
        if algo_name in results['algoritmos']:
            algo_result = results['algoritmos'][algo_name]
            if algo_result.get('exito'):
                path = algo_result['ruta']
                cost = algo_result['costo']
                objective = results['objetivo']
                
                is_valid, reporte = verifier.verify_complete_solution(path, cost, objective)
                
                status = "✅ VÁLIDA" if is_valid else "❌ INVÁLIDA"
                print(f"\n{algo_name}: {status}")
                print(f"  - Camino válido: {reporte['valid_path']}")
                print(f"  - Costo correcto: {reporte['valid_cost']}")
                print(f"  - Objetivo alcanzado: {reporte['objective_satisfied']}")

    # ========== PASO 4: Generar Visualizaciones ==========
    print("\n🎨 PASO 4: Generar Visualizaciones HTML")
    print("-" * 80)
    
    visualizer = MapVisualizer(scenario_data, cell_size=50)
    
    for algo_name in ['BFS', 'UCS']:
        if algo_name in results['algoritmos']:
            algo_result = results['algoritmos'][algo_name]
            if algo_result.get('exito'):
                path = algo_result['ruta']
                path_list = [list(p) for p in path]
                
                output_file = f"demo_{algo_name.lower()}.html"
                html_path = visualizer.save_html(
                    output_file,
                    explored_nodes=None,
                    path=path_list
                )
                
                print(f"\n✅ {algo_name}")
                print(f"   HTML: {Path(html_path).name}")
                print(f"   Abre en navegador para ver visualización")

    # ========== ANÁLISIS FINAL ==========
    print("\n📈 ANÁLISIS FINAL")
    print("-" * 80)
    
    bfs_result = results['algoritmos']['BFS']
    ucs_result = results['algoritmos']['UCS']
    
    if bfs_result.get('exito') and ucs_result.get('exito'):
        bfs_moves = bfs_result['movimientos']
        bfs_cost = bfs_result.get('costo_real', bfs_result['costo'])
        ucs_moves = ucs_result['movimientos']
        ucs_cost = ucs_result['costo']
        
        print(f"\nEste escenario demuestra la DIVERGENCIA entre BFS y UCS:")
        print(f"\nBFS (minimiza pasos):")
        print(f"  - Movimientos: {bfs_moves}")
        print(f"  - Costo real: {bfs_cost}")
        print(f"\nUCS (minimiza costo):")
        print(f"  - Movimientos: {ucs_moves}")
        print(f"  - Costo: {ucs_cost}")
        print(f"\n💡 Conclusión:")
        print(f"  BFS eligió ruta corta pero CARA")
        print(f"  UCS eligió ruta larga pero BARATA")
        print(f"  Diferencia de costo: {abs(bfs_cost - ucs_cost)} ({abs(bfs_cost - ucs_cost) / ucs_cost * 100:.0f}%)")

    print("\n" + "=" * 80)
    print(" ✅ DEMOSTRACIÓN COMPLETADA")
    print("=" * 80)
    print("\n📂 Archivos generados:")
    print("   - demo_bfs.html")
    print("   - demo_ucs.html")
    print("\n🌐 Abre los archivos HTML en tu navegador para ver visualizaciones interactivas")
    print()


if __name__ == "__main__":
    try:
        demo()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
