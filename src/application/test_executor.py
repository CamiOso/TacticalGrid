"""Ejecutor de pruebas basadas en escenarios JSON."""

from pathlib import Path
from typing import Dict, List, Tuple
from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario
from src.algorithms.search import bfs, dfs, ucs, a_star
from src.algorithms.adversarial import minimax_with_action, alfabeta_with_action
from src.algorithms.heuristics import manhattan_distance
from src.game.state import Action


def _action_from_str(action_str: str) -> Action:
    """Convierte la representación 'Action.MOVE_UP' a la enumeración Action."""
    mapping = {a.name: a for a in Action}
    name = action_str.split('.')[-1].strip()
    return mapping.get(name, Action.MOVE_UP)


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
                    'estados_generados': result.generated,
                    'estados_expandidos': result.expanded,
                    'maximo_frontera': result.max_frontier,
                }

                if result.path:
                    algo_result['movimientos'] = len(result.path) - 1

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
        from src.algorithms.adversarial import (
            minimax_with_action_full, alfabeta_with_action_full,
        )
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
                resource_carrier=self.scenario.resource_carrier,
                current_turn=self.scenario.current_turn,
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

            # Ejecutar Minimax y Alfa-Beta.
            # La profundidad proviene de prueba.profundidad o del campo de juego.
            profundidad = test_config.get(
                'profundidad', self.scenario.max_minimax_depth)

            results = {
                'modo': 'adversarial',
                'estado_inicial': str(initial_state),
                'profundidad': profundidad,
                'algoritmos': {}
            }

            # Minimax
            try:
                r = minimax_with_action_full(
                    initial_state, profundidad, True, utility_func, get_successors
                )
                results['algoritmos']['Minimax'] = {
                    'exito': r.best_action is not None,
                    'valor': r.best_value,
                    'accion': str(r.best_action) if r.best_action else None,
                    'nodos_generados': r.nodes_generated,
                    'nodos_evaluados': r.nodes_evaluated,
                    'nodos_podados': r.pruned,
                    'profundidad_alcanzada': r.depth_reached,
                }
            except Exception as e:
                results['algoritmos']['Minimax'] = {'error': str(e)}

            # Alfa-Beta
            try:
                r = alfabeta_with_action_full(
                    initial_state, profundidad, True, utility_func, get_successors
                )
                results['algoritmos']['Alfa-Beta'] = {
                    'exito': r.best_action is not None,
                    'valor': r.best_value,
                    'accion': str(r.best_action) if r.best_action else None,
                    'nodos_generados': r.nodes_generated,
                    'nodos_evaluados': r.nodes_evaluated,
                    'nodos_podados': r.pruned,
                    'profundidad_alcanzada': r.depth_reached,
                }
            except Exception as e:
                results['algoritmos']['Alfa-Beta'] = {'error': str(e)}

            return results

        except Exception as e:
            return {
                'modo': 'adversarial',
                'error': f'Error en prueba adversarial: {str(e)}'
            }

    def execute_partida_test(self, max_turns: int = 20) -> Dict:
        """
        Ejecuta una partida por turnos (modo partida).

        Cada bando elige su acción con alfa-beta sobre el estado actual, desde la
        perspectiva de su propio bando. La partida termina cuando un bando gana
        (lleva el recurso a su base) o se alcanza el límite de turnos.

        Retorna:
            Dict con la secuencia de turnos y el resultado.
        """
        if not self.scenario:
            raise RuntimeError("Escenario no cargado.")

        test_config = self.scenario.test_config
        if test_config['modo'] != 'partida':
            raise ValueError(
                f"Test mode debe ser 'partida', se encontró '{test_config['modo']}'")

        import time
        from src.game.state import GameState, Unit
        from src.algorithms.adversarial import alfabeta_with_action_full
        from src.game.utility import create_minimax_eval_function

        try:
            units = []
            for unit_data in self.scenario.units:
                units.append(Unit(
                    id=unit_data['id'],
                    team=unit_data.get('bando', 'A'),
                    row=unit_data['fila'],
                    col=unit_data['columna'],
                    carries_resource=(
                        self.scenario.resource_carrier == unit_data['id']
                    ),
                ))

            resource_pos = self.scenario.resource_position
            if isinstance(resource_pos, dict):
                resource_pos = (resource_pos['fila'], resource_pos['columna'])

            state = GameState(
                scenario_data=self.scenario_data,
                units=units,
                resource_pos=resource_pos,
                resource_carrier=self.scenario.resource_carrier,
                current_turn=self.scenario.current_turn,
            )

            depth = test_config.get('profundidad', self.scenario.max_minimax_depth)

            def get_successors(s: GameState, is_maximizing: bool = None):
                out = []
                for unit in s.get_units_by_team(s.current_turn):
                    for action in s.get_valid_actions(unit.id):
                        ns = s.copy()
                        ns.apply_action(unit.id, action)
                        out.append((ns, str(action)))
                return out

            turns = []
            ganador = None
            motivo_fin = 'limite_turnos'

            for turno in range(max_turns):
                if state.is_terminal():
                    ganador = state.get_winner()
                    motivo_fin = 'ganador' if ganador else 'bloqueo'
                    break

                team = state.current_turn
                eval_func = create_minimax_eval_function(team=team, strategy='balanced')

                start_t = time.perf_counter()
                result = alfabeta_with_action_full(
                    state, depth, True, eval_func, get_successors)
                elapsed = time.perf_counter() - start_t

                if result.best_action is None:
                    motivo_fin = 'sin_acciones'
                    break

                # Aplicar la acción elegida
                applied = False
                for unit in state.get_units_by_team(team):
                    valid = [str(a) for a in state.get_valid_actions(unit.id)]
                    if str(result.best_action) in valid:
                        if state.apply_action(unit.id, _action_from_str(result.best_action)):
                            applied = True
                            break
                if not applied:
                    motivo_fin = 'accion_invalida'
                    break

                turns.append({
                    'turno': turno + 1,
                    'bando': team,
                    'accion': str(result.best_action),
                    'valor': result.best_value,
                    'nodos_generados': result.nodes_generated,
                    'nodos_evaluados': result.nodes_evaluated,
                    'nodos_podados': result.pruned,
                    'tiempo_ms': round(elapsed * 1000, 3),
                })

            return {
                'modo': 'partida',
                'profundidad': depth,
                'max_turnos': max_turns,
                'turnos_jugados': len(turns),
                'ganador': ganador or state.get_winner(),
                'motivo_fin': motivo_fin,
                'secuencia': turns,
            }

        except Exception as e:
            return {'modo': 'partida', 'error': f'Error en partida: {str(e)}'}

    def execute_test(self) -> Dict:
        """
        Ejecuta la prueba especificada en el escenario.

        Detecta automáticamente el modo (búsqueda, adversarial o partida) y
        ejecuta el tipo de prueba correspondiente.

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
        elif test_mode == 'partida':
            return self.execute_partida_test()
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
                output.append(
                    f"\n{'Algoritmo':<12} {'Éxito':<8} {'Valor':<12} {'Generados':<10} "
                    f"{'Evaluados':<10} {'Podados':<9} {'Prof.':<7} {'Acción':<20}")
                output.append("-" * 90)

                for algo_name, algo_result in results['algoritmos'].items():
                    if 'error' in algo_result:
                        output.append(
                            f"{algo_name:<12} {'❌':<8} {'Error':<12} {algo_result['error']:<20}")
                    else:
                        exito = "✅" if algo_result.get('exito') else "❌"
                        valor = algo_result.get('valor', '-')
                        gen = algo_result.get('nodos_generados', '-')
                        ev = algo_result.get('nodos_evaluados', '-')
                        pod = algo_result.get('nodos_podados', '-')
                        prof = algo_result.get('profundidad_alcanzada', '-')
                        accion = algo_result.get('accion', 'None')
                        output.append(
                            f"{algo_name:<12} {exito:<8} {str(valor):<12} {str(gen):<10} "
                            f"{str(ev):<10} {str(pod):<9} {str(prof):<7} {str(accion):<20}"
                        )

        elif results['modo'] == 'partida':
            output.append(f"\nConfiguración:")
            output.append(f"  Profundidad: {results.get('profundidad', '-')}")
            output.append(f"  Máximo de turnos: {results.get('max_turnos', '-')}")

            if 'error' in results:
                output.append(f"\n❌ Error: {results['error']}")
            else:
                output.append(f"\nTurnos jugados: {results.get('turnos_jugados', '-')}")
                output.append(f"Ganador: {results.get('ganador', '-')}")
                output.append(f"Motivo de fin: {results.get('motivo_fin', '-')}")
                output.append(
                    f"\n{'Turno':<7} {'Bando':<7} {'Acción':<20} {'Valor':<12} "
                    f"{'Gen':<7} {'Eval':<7} {'Pod':<7} {'Tiempo(ms)':<12}")
                output.append("-" * 85)

                for t in results.get('secuencia', []):
                    output.append(
                        f"{t['turno']:<7} {t['bando']:<7} {t['accion']:<20} "
                        f"{str(t['valor']):<12} {str(t['nodos_generados']):<7} "
                        f"{str(t['nodos_evaluados']):<7} {str(t['nodos_podados']):<7} "
                        f"{str(t['tiempo_ms']):<12}"
                    )

        output.append("\n" + "=" * 70)
        return "\n".join(output)
