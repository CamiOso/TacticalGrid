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
        self.scenario_data = None  # Guardar los datos raw para Minimax/GameState
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
        self.scenario_data = scenario_data  # Guardar para GameState/Minimax
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

        Requiere que el escenario defina funciones de evaluación
        y generación de sucesores para el dominio del juego.

        Retorna:
            Dict con resultados de evaluación (valor, acción, métricas)
        """
        if not self.scenario:
            raise RuntimeError("Escenario no cargado.")

        test_config = self.scenario.test_config
        if test_config['modo'] != 'adversarial':
            raise ValueError(f"Test mode debe ser 'adversarial', se encontró '{test_config['modo']}'")

        from src.game.state import GameState, Unit
        from src.algorithms.adversarial import minimax_with_action, alfabeta_with_action
        from src.game.utility import create_minimax_eval_function

        try:
            # Crear estado inicial del juego
            units = []
            for unit_data in self.scenario.units:
                units.append(Unit(
                    id=unit_data['id'],
                    team=unit_data.get('bando', 'A'),
                    row=unit_data['fila'],
                    col=unit_data['columna'],
                    carries_resource=False
                ))

            resource_pos = self.scenario.resource_position
            if isinstance(resource_pos, dict):
                resource_pos = (resource_pos['fila'], resource_pos['columna'])

            initial_state = GameState(
                scenario_data=self.scenario_data,
                units=units,
                resource_pos=resource_pos,
                resource_carrier=None,
                current_turn='A'
            )

            # Crear función de utilidad
            utility_func = create_minimax_eval_function(team='A', strategy='balanced')

            # Función para generar sucesores
            def get_successors(state: GameState, is_maximizing: bool = None) -> List[Tuple]:
                """Genera todos los sucesores posibles de un estado."""
                successors = []
                for unit in state.get_units_by_team(state.current_turn):
                    for action in state.get_valid_actions(unit.id):
                        next_state = state.copy()
                        next_state.apply_action(unit.id, action)
                        successors.append((next_state, str(action)))
                return successors

            # Ejecutar Minimax y Alfa-Beta
            profundidad = test_config.get('profundidad', 3)

            results = {
                'modo': 'adversarial',
                'estado_inicial': str(initial_state),
                'profundidad': profundidad,
                'algoritmos': {}
            }

            # Minimax
            try:
                resultado_minimax = minimax_with_action(
                    initial_state, profundidad, True, utility_func, get_successors
                )
                results['algoritmos']['Minimax'] = {
                    'exito': resultado_minimax.best_action is not None,
                    'valor': resultado_minimax.best_value,
                    'accion': str(resultado_minimax.best_action) if resultado_minimax.best_action else None,
                    'nodos_evaluados': resultado_minimax.nodes_evaluated
                }
            except Exception as e:
                results['algoritmos']['Minimax'] = {'error': str(e)}

            # Alfa-Beta
            try:
                resultado_alfabeta = alfabeta_with_action(
                    initial_state, profundidad, True, utility_func, get_successors
                )
                results['algoritmos']['Alfa-Beta'] = {
                    'exito': resultado_alfabeta.best_action is not None,
                    'valor': resultado_alfabeta.best_value,
                    'accion': str(resultado_alfabeta.best_action) if resultado_alfabeta.best_action else None,
                    'nodos_evaluados': resultado_alfabeta.nodes_evaluated
                }
            except Exception as e:
                results['algoritmos']['Alfa-Beta'] = {'error': str(e)}

            return results

        except Exception as e:
            return {
                'modo': 'adversarial',
                'error': f'Error en prueba adversarial: {str(e)}'
            }

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

        elif results['modo'] == 'adversarial':
            output.append(f"\nConfiguración:")
            output.append(f"  Profundidad: {results.get('profundidad', '-')}")
            output.append(f"  Estado inicial: {results.get('estado_inicial', '-')}")

            if 'error' in results:
                output.append(f"\n❌ Error: {results['error']}")
            else:
                output.append(f"\n{'Algoritmo':<15} {'Éxito':<8} {'Valor':<15} {'Acción':<20}")
                output.append("-" * 60)

                for algo_name, algo_result in results['algoritmos'].items():
                    if 'error' in algo_result:
                        output.append(f"{algo_name:<15} {'❌':<8} {'Error':<15} {algo_result['error']:<20}")
                    else:
                        exito = "✅" if algo_result.get('exito') else "❌"
                        valor = algo_result.get('valor', '-')
                        accion = algo_result.get('accion', 'None')
                        output.append(f"{algo_name:<15} {exito:<8} {str(valor):<15} {str(accion):<20}")

        output.append("\n" + "=" * 70)
        return "\n".join(output)
