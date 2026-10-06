"""Ejecutor de pruebas basadas en escenarios JSON."""

from pathlib import Path
from typing import Dict, List, Tuple
from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario
from src.algorithms.search import bfs, dfs, ucs, a_star
from src.algorithms.adversarial import minimax_with_action, alfabeta_with_action
from src.algorithms.heuristics import manhattan_distance


class TestExecutor:
    """
    Ejecuta pruebas de búsqueda y adversariales basadas en escenarios JSON.

    Modos soportados:
    - "busqueda": Ejecuta algoritmos de búsqueda (BFS, DFS, UCS, A*)
    - "adversarial": Ejecuta Minimax o Alfa-Beta sobre un estado inicial
    """

    def __init__(self):
        """Inicializa el ejecutor."""
        self.scenario = None
        self.results = []

    def load_scenario(self, scenario_path: str | Path) -> Scenario:
        """
        Carga un escenario JSON.

        Parámetros:
            scenario_path: Ruta al archivo JSON

        Retorna:
            Objeto Scenario cargado y validado
        """
        scenario_data = ScenarioLoader.load(scenario_path)
        self.scenario = Scenario(scenario_data)
        return self.scenario

    def create_graph_from_scenario(self) -> Dict:
        """
        Convierte el escenario en grafo de adyacencia.

        Cada celda transitable es un nodo, conectada con vecinos adyacentes
        (arriba, abajo, izquierda, derecha).

        Retorna:
            Dict {(fila, col): [vecinos]}
        """
        if not self.scenario:
            raise RuntimeError("Escenario no cargado. Llamar load_scenario() primero.")

        graph = {}
        rows = self.scenario.rows
        cols = self.scenario.cols
        terrain_types = self.scenario.terrain_types

        for r in range(rows):
            for c in range(cols):
                terrain = self.scenario.get_terrain_type(r, c)
                if terrain_types[terrain]['transitable']:
                    graph[(r, c)] = []
                    # Vecinos: arriba, abajo, izq, der
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            neighbor_terrain = self.scenario.get_terrain_type(nr, nc)
                            if terrain_types[neighbor_terrain]['transitable']:
                                graph[(r, c)].append((nr, nc))

        return graph

    def create_costs_from_scenario(self, graph: Dict) -> Dict:
        """
        Extrae diccionario de costos desde el escenario.

        Para cada arista (nodo, vecino), el costo es el del terreno del destino.

        Parámetros:
            graph: Grafo de adyacencia

        Retorna:
            Dict {(nodo, vecino): costo}
        """
        if not self.scenario:
            raise RuntimeError("Escenario no cargado.")

        costs = {}
        terrain_types = self.scenario.terrain_types

        for node in graph:
            for neighbor in graph[node]:
                neighbor_terrain = self.scenario.get_terrain_type(neighbor[0], neighbor[1])
                cost = terrain_types[neighbor_terrain]['costo']
                costs[(node, neighbor)] = cost

        return costs

    def execute_search_test(self) -> Dict:
        """
        Ejecuta una prueba de búsqueda según configuración en scenario.prueba.

        Retorna:
            Dict con resultados de todos los algoritmos
        """
        if not self.scenario:
            raise RuntimeError("Escenario no cargado.")

        test_config = self.scenario.test_config
        if test_config['modo'] != 'busqueda':
            raise ValueError(f"Test mode debe ser 'busqueda', se encontró '{test_config['modo']}'")

        # Obtener configuración
        unit_id = test_config.get('unidad_inicio')
        goal = self.scenario.test_objective  # Usa la propiedad que convierte a tupla

        if not unit_id:
            raise ValueError("unidad_inicio es requerido para modo búsqueda")

        start = self.scenario.get_unit_position(unit_id)
        if not start:
            raise ValueError(f"Unidad '{unit_id}' no existe")

        # Crear grafo y costos
        graph = self.create_graph_from_scenario()
        costs = self.create_costs_from_scenario(graph)

        results = {
            'modo': 'busqueda',
            'unidad_inicio': unit_id,
            'posicion_inicio': start,
            'objetivo': goal,
            'algoritmos': {}
        }

        # Ejecutar algoritmos
        algorithms = [
            ('BFS', lambda: bfs(graph, start, goal)),
            ('DFS', lambda: dfs(graph, start, goal)),
            ('UCS', lambda: ucs(graph, start, goal, costs)),
            ('A*', lambda: a_star(graph, start, goal, manhattan_distance, costs)),
        ]

        for algo_name, algo_func in algorithms:
            try:
                result = algo_func()
                algo_result = {
                    'exito': result.path is not None,
                    'ruta': result.path if result.path else [],
                    'costo': result.cost if result.path else float('inf'),
                    'estados_generados': result.explored,
                }

                if result.path:
                    algo_result['movimientos'] = len(result.path) - 1
                    algo_result['maximo_frontera'] = result.explored

                    # Para BFS/DFS que no usan costos, calcular costo real de la ruta
                    if algo_name in ['BFS', 'DFS']:
                        costo_real = 0
                        for i in range(len(result.path) - 1):
                            edge = (result.path[i], result.path[i + 1])
                            costo_real += costs.get(edge, 1)
                        algo_result['costo_real'] = costo_real

                results['algoritmos'][algo_name] = algo_result
            except Exception as e:
                results['algoritmos'][algo_name] = {
                    'exito': False,
                    'error': str(e)
                }

        return results

    def execute_adversarial_test(self) -> Dict:
        """
        Ejecuta una prueba adversarial (Minimax/Alfa-Beta).

        Nota: Requiere que el escenario defina funciones de evaluación
        y generación de sucesores apropiadas para su dominio específico.

        Retorna:
            Dict con resultados de evaluación
        """
        if not self.scenario:
            raise RuntimeError("Escenario no cargado.")

        test_config = self.scenario.test_config
        if test_config['modo'] != 'adversarial':
            raise ValueError(f"Test mode debe ser 'adversarial', se encontró '{test_config['modo']}'")

        results = {
            'modo': 'adversarial',
            'error': 'Modo adversarial requiere dominio específico con eval_func y get_successors'
        }

        return results

    def execute_test(self) -> Dict:
        """
        Ejecuta la prueba especificada en el escenario.

        Detecta automáticamente el modo (búsqueda o adversarial) y ejecuta
        el tipo de prueba correspondiente.

        Retorna:
            Dict con resultados
        """
        if not self.scenario:
            raise RuntimeError("Escenario no cargado.")

        test_mode = self.scenario.test_mode

        if test_mode == 'busqueda':
            return self.execute_search_test()
        elif test_mode == 'adversarial':
            return self.execute_adversarial_test()
        else:
            raise ValueError(f"Modo de prueba desconocido: {test_mode}")

    def format_results(self, results: Dict) -> str:
        """
        Formatea resultados para visualización.

        Parámetros:
            results: Diccionario de resultados

        Retorna:
            String formateado para imprimir
        """
        output = []
        output.append("=" * 70)
        output.append(f"RESULTADOS: {results['modo'].upper()}")
        output.append("=" * 70)

        if results['modo'] == 'busqueda':
            output.append(f"\nConfiguración:")
            output.append(f"  Unidad: {results['unidad_inicio']}")
            output.append(f"  Inicio: {results['posicion_inicio']}")
            output.append(f"  Objetivo: {results['objetivo']}")

            output.append(f"\n{'Algoritmo':<15} {'Éxito':<8} {'Movimientos':<15} {'Costo':<15} {'Explorados':<12}")
            output.append("-" * 65)

            for algo_name, algo_result in results['algoritmos'].items():
                exito = "✅" if algo_result.get('exito') else "❌"
                movimientos = algo_result.get('movimientos', '-')

                # Mostrar costo real para BFS/DFS, costo del algoritmo para UCS/A*
                if 'costo_real' in algo_result:
                    costo_str = f"{algo_result['costo']}/{algo_result['costo_real']}"
                else:
                    costo_str = str(algo_result.get('costo', '-'))

                explorados = algo_result.get('estados_generados', '-')

                output.append(f"{algo_name:<15} {exito:<8} {str(movimientos):<15} {costo_str:<15} {str(explorados):<12}")

        output.append("\n" + "=" * 70)
        return "\n".join(output)
