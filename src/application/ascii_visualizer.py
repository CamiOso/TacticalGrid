"""Visualización ASCII robusta para el mapa y soluciones de búsqueda."""

from pathlib import Path
from typing import List, Tuple, Optional, Dict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scenario.scenario import Scenario
from src.algorithms.search import SearchResult


class ASCIIVisualizer:
    """Visualiza escenarios y soluciones en formato ASCII para terminal."""

    # Caracteres para terrenos
    TERRAIN_CHARS = {
        'camino': '·',      # Punto para camino
        'pasto': '~',       # Onda para pasto
        'agua': '≈',        # Agua
        'muro': '█',        # Bloque sólido para muro
        'default': '?'      # Desconocido
    }

    # Colores ANSI
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'gray': '\033[90m',
    }

    def __init__(self, scenario: Scenario):
        """Inicializa el visualizador con un escenario."""
        self.scenario = scenario
        self.rows = scenario.rows
        self.cols = scenario.cols

    def _colorize(self, text: str, color: str) -> str:
        """Añade color ANSI a un texto."""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def _get_terrain_char(self, terrain_type: str) -> str:
        """Obtiene el carácter para un tipo de terreno."""
        return self.TERRAIN_CHARS.get(terrain_type, self.TERRAIN_CHARS['default'])

    def draw_base_map(self) -> List[List[str]]:
        """Crea una matriz visual del mapa sin caminos ni unidades."""
        grid = []
        for row in range(self.rows):
            grid_row = []
            for col in range(self.cols):
                terrain_type = self.scenario.get_terrain_type(row, col)
                char = self._get_terrain_char(terrain_type)

                # Colorear según tipo de terreno
                if not self.scenario.terrain_types[terrain_type]['transitable']:
                    colored = self._colorize(char, 'red')  # Muros en rojo
                else:
                    colored = self._colorize(char, 'cyan')  # Terreno transitable en cyan

                grid_row.append(colored)
            grid.append(grid_row)

        return grid

    def draw_with_units(self) -> List[List[str]]:
        """Crea mapa con unidades, recurso y bases."""
        grid = self.draw_base_map()

        # Dibujar bases
        for equipo, pos in self.scenario.bases.items():
            row, col = pos
            if 0 <= row < self.rows and 0 <= col < self.cols:
                color = 'green' if equipo == 'A' else 'magenta'
                grid[row][col] = self._colorize(f'[{equipo}]', color)

        # Dibujar recurso
        if self.scenario.resource_position:
            r, c = self.scenario.resource_position
            if 0 <= r < self.rows and 0 <= c < self.cols:
                grid[r][c] = self._colorize('◆', 'yellow')

        # Dibujar unidades
        for unit_data in self.scenario.units:
            row, col = unit_data['fila'], unit_data['columna']
            if 0 <= row < self.rows and 0 <= col < self.cols:
                unit_id = unit_data['id']
                bando = unit_data.get('bando', unit_data.get('equipo', 'A'))
                color = 'green' if bando == 'A' else 'magenta'
                grid[row][col] = self._colorize(unit_id, color)

        return grid

    def draw_with_path(self, path: List[Tuple[int, int]]) -> List[List[str]]:
        """Crea mapa con unidades y el camino encontrado."""
        grid = self.draw_with_units()

        # Marcar camino (excepto inicio y final)
        if len(path) > 0:
            for i, (row, col) in enumerate(path):
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    if i == 0:
                        # Inicio del camino
                        grid[row][col] = self._colorize('S', 'green')
                    elif i == len(path) - 1:
                        # Fin del camino
                        grid[row][col] = self._colorize('E', 'yellow')
                    else:
                        # Camino intermedio
                        grid[row][col] = self._colorize('*', 'blue')

        return grid

    def render_grid(self, grid: List[List[str]]) -> str:
        """Convierte una grilla en string para imprimir."""
        lines = []

        # Encabezado con números de columna
        header = "   "
        for col in range(self.cols):
            header += f"{col:2d} "
        lines.append(header)

        # Línea separadora
        separator = "   " + "─" * (self.cols * 3)
        lines.append(separator)

        # Filas
        for row in range(self.rows):
            line = f"{row:2d} │ "
            line += " ".join(grid[row])
            line += " │"
            lines.append(line)

        # Línea separadora inferior
        lines.append(separator)

        return "\n".join(lines)

    def print_map(self):
        """Imprime el mapa con unidades."""
        grid = self.draw_with_units()
        print(self.render_grid(grid))

    def print_path(self, path: List[Tuple[int, int]]):
        """Imprime el mapa con el camino encontrado."""
        grid = self.draw_with_path(path)
        print(self.render_grid(grid))

    def print_legend(self):
        """Imprime la leyenda de símbolos."""
        print("\n📋 LEYENDA:")
        print(f"  {self._colorize('█', 'red')}     = Muro (intransitable)")
        print(f"  {self._colorize('·', 'cyan')}     = Camino (transitable)")
        print(f"  {self._colorize('~', 'cyan')}     = Pasto (transitable)")
        print(f"  {self._colorize('[A]', 'green')} = Base equipo A")
        print(f"  {self._colorize('[B]', 'magenta')} = Base equipo B")
        print(f"  {self._colorize('◆', 'yellow')} = Recurso")
        print(f"  {self._colorize('A1', 'green')} = Unidad equipo A")
        print(f"  {self._colorize('B1', 'magenta')} = Unidad equipo B")
        print(f"  {self._colorize('S', 'green')}  = Inicio del camino")
        print(f"  {self._colorize('*', 'blue')}  = Camino intermedio")
        print(f"  {self._colorize('E', 'yellow')} = Fin del camino")
        print()

    def print_scenario_info(self):
        """Imprime información del escenario."""
        print("\n" + "="*70)
        print(f"📍 INFORMACIÓN DEL ESCENARIO")
        print("="*70)
        print(f"  Dimensiones: {self.rows}×{self.cols}")
        print(f"  Unidades: {len(self.scenario.units)}")
        for unit in self.scenario.units:
            pos = (unit['fila'], unit['columna'])
            bando = unit.get('bando', unit.get('equipo', 'A'))
            print(f"    - {unit['id']} (Bando {bando}): {pos}")

        print(f"  Recurso: {self.scenario.resource_position}")
        print(f"  Base A: {self.scenario.bases.get('A', 'N/A')}")
        print(f"  Base B: {self.scenario.bases.get('B', 'N/A')}")
        print(f"  Objetivo: {self.scenario.test_objective}")
        print()

    def print_path_details(self, path: List[Tuple[int, int]], cost: int, explored: int):
        """Imprime detalles del camino encontrado."""
        print("\n" + "="*70)
        print(f"📊 RESULTADO DE LA BÚSQUEDA")
        print("="*70)
        print(f"  ✅ Camino encontrado: {'Sí' if path else 'No'}")
        if path:
            print(f"  📏 Pasos: {len(path) - 1}")
            print(f"  💰 Costo: {cost}")
            print(f"  🔍 Nodos explorados: {explored}")
            print(f"  📍 Secuencia de movimientos:")
            for i, (row, col) in enumerate(path):
                if i < len(path) - 1:
                    print(f"     {i}: ({row}, {col})", end="")
                    if i < len(path) - 1:
                        next_row, next_col = path[i + 1]
                        if next_row < row:
                            print(" → ↑ (arriba)")
                        elif next_row > row:
                            print(" → ↓ (abajo)")
                        elif next_col < col:
                            print(" → ← (izquierda)")
                        elif next_col > col:
                            print(" → → (derecha)")
                else:
                    print(f"     {i}: ({row}, {col}) ✓")
        print()

    def print_complete_visualization(self, path: Optional[List[Tuple[int, int]]] = None,
                                    cost: int = 0, explored: int = 0,
                                    algorithm_name: str = "Búsqueda"):
        """Imprime visualización completa del escenario."""
        print("\n" + "="*70)
        print(f"🗺️  VISUALIZACIÓN: {algorithm_name}")
        print("="*70 + "\n")

        self.print_scenario_info()

        if path:
            self.print_path(path)
        else:
            self.print_map()

        self.print_legend()

        if path:
            self.print_path_details(path, cost, explored)


def visualize_scenario_from_file(scenario_path: Path, search_result: Optional[SearchResult] = None,
                                 algorithm_name: str = "Búsqueda"):
    """Función de conveniencia para visualizar desde archivo."""
    from src.scenario.loader import ScenarioLoader

    scenario_data = ScenarioLoader.load(scenario_path)
    scenario = Scenario(scenario_data)

    visualizer = ASCIIVisualizer(scenario)

    if search_result and search_result.path:
        visualizer.print_complete_visualization(
            path=search_result.path,
            cost=search_result.cost,
            explored=search_result.explored,
            algorithm_name=algorithm_name
        )
    else:
        visualizer.print_complete_visualization(algorithm_name=algorithm_name)


if __name__ == "__main__":
    # Ejemplo
    scenario_path = Path(__file__).parent.parent.parent / "scenarios" / "ejemplo_basico.json"
    visualize_scenario_from_file(scenario_path)
