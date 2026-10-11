"""Agentes que trabajan con escenarios JSON cargados dinámicamente."""

from pathlib import Path
from typing import Optional, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scenario.loader import ScenarioLoader
from src.scenario.validator import ScenarioValidator
from src.scenario.scenario import Scenario
from src.algorithms.search import bfs, dfs, ucs, a_star, beam_search
from src.algorithms.heuristics import manhattan_distance
from src.application.ascii_visualizer import ASCIIVisualizer


class ScenarioAgent:
    """Agente base que funciona con escenarios JSON."""

    def __init__(self, scenario_path: Path):
        """Inicializa el agente con un escenario."""
        self.scenario_path = Path(scenario_path)

        # Cargar y validar escenario
        self.scenario_data = ScenarioLoader.load(self.scenario_path)
        is_valid, errors = ScenarioValidator.validate_scenario(self.scenario_data)

        if not is_valid:
            raise ValueError(f"Escenario inválido: {errors}")

        self.scenario = Scenario(self.scenario_data)
        self.visualizer = ASCIIVisualizer(self.scenario)

    def _create_graph_from_scenario(self):
        """Crea un grafo a partir del escenario."""
        graph = {}

        for row in range(self.scenario.rows):
            for col in range(self.scenario.cols):
                terrain_type = self.scenario.get_terrain_type(row, col)

                if not self.scenario.terrain_types[terrain_type]['transitable']:
                    continue  # No incluir celdas intransitables

                neighbors = []
                # 4 direcciones
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = row + dr, col + dc

                    if 0 <= nr < self.scenario.rows and 0 <= nc < self.scenario.cols:
                        neighbor_terrain = self.scenario.get_terrain_type(nr, nc)

                        if self.scenario.terrain_types[neighbor_terrain]['transitable']:
                            neighbors.append((nr, nc))

                graph[(row, col)] = neighbors

        return graph

    def _create_costs_from_scenario(self, graph):
        """Crea diccionario de costos a partir del escenario."""
        costs = {}

        for row in range(self.scenario.rows):
            for col in range(self.scenario.cols):
                terrain_type = self.scenario.get_terrain_type(row, col)

                if not self.scenario.terrain_types[terrain_type]['transitable']:
                    continue

                neighbors = graph.get((row, col), [])

                for nr, nc in neighbors:
                    neighbor_terrain = self.scenario.get_terrain_type(nr, nc)
                    edge_cost = self.scenario.terrain_types[neighbor_terrain]['costo']
                    costs[((row, col), (nr, nc))] = edge_cost

        return costs

    def get_unit_position(self, unit_id: str) -> Optional[Tuple[int, int]]:
        """Obtiene la posición de una unidad."""
        for unit in self.scenario.units:
            if unit['id'] == unit_id:
                return (unit['fila'], unit['columna'])
        return None

    def search(self, unit_id: str, goal: Tuple[int, int], algorithm: str = 'bfs'):
        """Ejecuta búsqueda para una unidad desde su posición actual a un objetivo."""
        start = self.get_unit_position(unit_id)

        if start is None:
            raise ValueError(f"Unidad {unit_id} no encontrada")

        graph = self._create_graph_from_scenario()
        costs = self._create_costs_from_scenario(graph)

        # Seleccionar algoritmo
        if algorithm == 'bfs':
            result = bfs(graph, start, goal)
        elif algorithm == 'dfs':
            result = dfs(graph, start, goal)
        elif algorithm == 'ucs':
            result = ucs(graph, start, goal, costs)
        elif algorithm == 'a_star':
            result = a_star(graph, start, goal, manhattan_distance, costs)
        elif algorithm == 'beam_search':
            result = beam_search(graph, start, goal, manhattan_distance, k=4, costs=costs)
        else:
            raise ValueError(f"Algoritmo desconocido: {algorithm}")

        return result

    def print_info(self):
        """Imprime información del escenario del agente."""
        self.visualizer.print_scenario_info()

    def visualize_map(self):
        """Visualiza el mapa."""
        self.visualizer.print_map()
        self.visualizer.print_legend()


class BFSAgent(ScenarioAgent):
    """Agente que usa BFS para búsqueda."""

    def search(self, unit_id: str, goal: Tuple[int, int]):
        """Búsqueda con BFS."""
        return super().search(unit_id, goal, algorithm='bfs')

    def move_to_goal(self, unit_id: str, goal: Tuple[int, int]):
        """Busca camino y visualiza resultado con BFS."""
        result = self.search(unit_id, goal)
        self.visualizer.print_complete_visualization(
            path=result.path,
            cost=result.cost,
            explored=result.explored,
            algorithm_name=f"BFS: {unit_id} → {goal}"
        )
        return result


class DFSAgent(ScenarioAgent):
    """Agente que usa DFS para búsqueda."""

    def search(self, unit_id: str, goal: Tuple[int, int]):
        """Búsqueda con DFS."""
        return super().search(unit_id, goal, algorithm='dfs')

    def move_to_goal(self, unit_id: str, goal: Tuple[int, int]):
        """Busca camino y visualiza resultado con DFS."""
        result = self.search(unit_id, goal)
        self.visualizer.print_complete_visualization(
            path=result.path,
            cost=result.cost,
            explored=result.explored,
            algorithm_name=f"DFS: {unit_id} → {goal}"
        )
        return result


class SmartAgent(ScenarioAgent):
    """Agente que usa A* para búsqueda inteligente."""

    def search(self, unit_id: str, goal: Tuple[int, int]):
        """Búsqueda con A*."""
        return super().search(unit_id, goal, algorithm='a_star')

    def move_to_goal(self, unit_id: str, goal: Tuple[int, int]):
        """Busca camino y visualiza resultado con A*."""
        result = self.search(unit_id, goal)
        self.visualizer.print_complete_visualization(
            path=result.path,
            cost=result.cost,
            explored=result.explored,
            algorithm_name=f"A*: {unit_id} → {goal}"
        )
        return result


class EfficientAgent(ScenarioAgent):
    """Agente que usa Beam Search con restricciones de memoria."""

    def __init__(self, scenario_path: Path, k: int = 4):
        """Inicializa con parámetro k de Beam Search."""
        super().__init__(scenario_path)
        self.k = k

    def search(self, unit_id: str, goal: Tuple[int, int]):
        """Búsqueda con Beam Search."""
        start = self.get_unit_position(unit_id)

        if start is None:
            raise ValueError(f"Unidad {unit_id} no encontrada")

        graph = self._create_graph_from_scenario()
        costs = self._create_costs_from_scenario(graph)

        result = beam_search(graph, start, goal, manhattan_distance, k=self.k, costs=costs)
        return result

    def move_to_goal(self, unit_id: str, goal: Tuple[int, int]):
        """Busca camino y visualiza resultado con Beam Search."""
        result = self.search(unit_id, goal)
        self.visualizer.print_complete_visualization(
            path=result.path,
            cost=result.cost,
            explored=result.explored,
            algorithm_name=f"Beam Search (k={self.k}): {unit_id} → {goal}"
        )
        return result


if __name__ == "__main__":
    # Ejemplo de uso
    scenario_path = Path(__file__).parent.parent.parent / "scenarios" / "ejemplo_basico.json"

    print("\n" + "="*70)
    print("🤖 DEMOSTRACIÓN DE AGENTES CON ESCENARIOS JSON")
    print("="*70)

    # BFS Agent
    print("\n🟢 AGENTE CON BFS")
    bfs_agent = BFSAgent(scenario_path)
    bfs_agent.print_info()
    bfs_agent.move_to_goal("A1", (3, 3))

    # Smart Agent
    print("\n🔵 AGENTE CON A*")
    smart_agent = SmartAgent(scenario_path)
    smart_agent.move_to_goal("A1", (3, 3))

    # Efficient Agent
    print("\n⚪ AGENTE CON BEAM SEARCH (k=4)")
    efficient_agent = EfficientAgent(scenario_path, k=4)
    efficient_agent.move_to_goal("A1", (3, 3))
