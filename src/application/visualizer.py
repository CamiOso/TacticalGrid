"""Generador de visualización HTML del mapa y búsqueda."""

from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path


class MapVisualizer:
    """
    Genera visualización HTML+Canvas del mapa y resultados de búsqueda.

    Muestra:
    - Mapa con tipos de terreno (colores diferentes)
    - Bases de cada equipo
    - Unidades
    - Recurso
    - Nodos explorados (búsqueda)
    - Camino encontrado
    """

    # Colores para terrenos
    TERRAIN_COLORS = {
        'camino': '#E8D5C4',      # Arena claro
        'pasto': '#7CB342',       # Verde
        'bosque': '#558B2F',      # Verde oscuro
        'montaña': '#9E9E9E',     # Gris
        'muro': '#263238',        # Negro
        'agua': '#0288D1',        # Azul
        'pantano': '#8D6E63',     # Marrón
    }

    def __init__(self, scenario_data: Dict, cell_size: int = 40):
        """
        Inicializa visualizador.

        Parámetros:
            scenario_data: Diccionario del escenario
            cell_size: Tamaño en píxeles de cada celda
        """
        self.scenario = scenario_data
        self.cell_size = cell_size
        self.rows = scenario_data['mapa']['filas']
        self.cols = scenario_data['mapa']['columnas']
        self.terrain = scenario_data['terreno']
        self.bases = scenario_data['bases']
        self.recurso = scenario_data['recurso']
        self.unidades = scenario_data['unidades']

    def _get_terrain_color(self, terrain_type: str) -> str:
        """Obtiene color para tipo de terreno."""
        return self.TERRAIN_COLORS.get(terrain_type, '#FFFFFF')

    def generate_html(self, explored_nodes: Optional[List[Tuple[int, int]]] = None,
                      path: Optional[List[Tuple[int, int]]] = None,
                      title: str = "TacticalGrid Visualization") -> str:
        """
        Genera HTML con visualización del mapa.

        Parámetros:
            explored_nodes: Lista de nodos explorados por búsqueda
            path: Camino encontrado
            title: Título de la página

        Retorna:
            HTML completo
        """
        width = self.cols * self.cell_size
        height = self.rows * self.cell_size

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #2196F3;
            padding-bottom: 10px;
        }}
        .info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .info-box {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #2196F3;
        }}
        .info-box h3 {{
            margin-top: 0;
            color: #2196F3;
        }}
        .info-box p {{
            margin: 5px 0;
            font-size: 14px;
        }}
        canvas {{
            border: 2px solid #333;
            background: white;
            display: block;
            margin: 20px 0;
        }}
        .legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 20px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            font-size: 13px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 2px;
            margin-right: 10px;
            border: 1px solid #999;
        }}
        .stats {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 {title}</h1>
        
        <div class="info">
            <div class="info-box">
                <h3>Mapa</h3>
                <p><strong>Dimensiones:</strong> {self.rows} × {self.cols}</p>
                <p><strong>Total celdas:</strong> {self.rows * self.cols}</p>
                <p><strong>Bases:</strong> {len(self.bases)}</p>
            </div>
            <div class="info-box">
                <h3>Unidades</h3>
                <p><strong>Total:</strong> {len(self.unidades)}</p>
"""
        for team in ['A', 'B']:
            team_units = [u for u in self.unidades if u['bando'] == team]
            html += f"                <p><strong>Team {team}:</strong> {len(team_units)} unidades</p>\n"

        html += f"""            </div>
        </div>

        <canvas id="mapCanvas" width="{width}" height="{height}"></canvas>

        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FFD700;"></div>
                <span>Explorados</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FF6B6B;"></div>
                <span>Camino</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FF0000; width: 30px; height: 30px;"></div>
                <span>Inicio</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #00FF00; width: 30px; height: 30px;"></div>
                <span>Objetivo</span>
            </div>
"""
        for terrain, color in self.TERRAIN_COLORS.items():
            html += f"""            <div class="legend-item">
                <div class="legend-color" style="background-color: {color};"></div>
                <span>{terrain.capitalize()}</span>
            </div>
"""

        html += """        </div>

        <div class="stats">
"""
        if explored_nodes:
            html += f"            <p><strong>Nodos explorados:</strong> {len(explored_nodes)}</p>\n"
        if path:
            html += f"            <p><strong>Camino encontrado:</strong> {len(path)-1} movimientos</p>\n"

        html += f"""        </div>
    </div>

    <script>
        const canvas = document.getElementById('mapCanvas');
        const ctx = canvas.getContext('2d');
        const cellSize = {self.cell_size};
        const rows = {self.rows};
        const cols = {self.cols};

        // Datos del mapa
        const terrain = {json.dumps(self.terrain)};
        const terrainColors = {json.dumps(self.TERRAIN_COLORS)};
        const bases = {json.dumps(self.bases)};
        const recurso = {json.dumps(self.recurso)};
        const unidades = {json.dumps(self.unidades)};
        const exploredNodes = {json.dumps(explored_nodes if explored_nodes else [])};
        const path = {json.dumps(path if path else [])};

        function drawMap() {{
            // Dibujar celdas de terreno
            for (let r = 0; r < rows; r++) {{
                for (let c = 0; c < cols; c++) {{
                    const terrainType = terrain[r][c];
                    const color = terrainColors[terrainType] || '#FFFFFF';
                    const x = c * cellSize;
                    const y = r * cellSize;
                    
                    ctx.fillStyle = color;
                    ctx.fillRect(x, y, cellSize, cellSize);
                    ctx.strokeStyle = '#DDD';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(x, y, cellSize, cellSize);
                }}
            }}

            // Dibujar nodos explorados
            ctx.fillStyle = 'rgba(255, 215, 0, 0.4)';
            exploredNodes.forEach(([r, c]) => {{
                const x = c * cellSize;
                const y = r * cellSize;
                ctx.fillRect(x, y, cellSize, cellSize);
            }});

            // Dibujar camino
            if (path.length > 0) {{
                ctx.strokeStyle = '#FF6B6B';
                ctx.lineWidth = 3;
                ctx.beginPath();
                for (let i = 0; i < path.length; i++) {{
                    const [r, c] = path[i];
                    const x = c * cellSize + cellSize / 2;
                    const y = r * cellSize + cellSize / 2;
                    if (i === 0) {{
                        ctx.moveTo(x, y);
                    }} else {{
                        ctx.lineTo(x, y);
                    }}
                }}
                ctx.stroke();
            }}

            // Dibujar recurso
            const rx = recurso['columna'] * cellSize + cellSize / 2;
            const ry = recurso['fila'] * cellSize + cellSize / 2;
            ctx.fillStyle = '#FFD700';
            ctx.beginPath();
            ctx.arc(rx, ry, cellSize / 4, 0, 2 * Math.PI);
            ctx.fill();
            ctx.strokeStyle = '#FF8C00';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Dibujar bases
            Object.entries(bases).forEach(([team, pos]) => {{
                const bx = pos['columna'] * cellSize;
                const by = pos['fila'] * cellSize;
                ctx.fillStyle = team === 'A' ? 'rgba(255, 0, 0, 0.3)' : 'rgba(0, 0, 255, 0.3)';
                ctx.fillRect(bx, by, cellSize, cellSize);
                ctx.strokeStyle = team === 'A' ? '#FF0000' : '#0000FF';
                ctx.lineWidth = 2;
                ctx.strokeRect(bx, by, cellSize, cellSize);
                ctx.fillStyle = team === 'A' ? '#FF0000' : '#0000FF';
                ctx.font = 'bold 12px Arial';
                ctx.fillText('Base ' + team, bx + 5, by + 15);
            }});

            // Dibujar unidades
            unidades.forEach(unit => {{
                const ux = unit['columna'] * cellSize + cellSize / 2;
                const uy = unit['fila'] * cellSize + cellSize / 2;
                const color = unit['bando'] === 'A' ? '#FF4444' : '#4444FF';
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(ux, uy, cellSize / 3, 0, 2 * Math.PI);
                ctx.fill();
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.fillStyle = '#FFF';
                ctx.font = 'bold 10px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(unit['id'], ux, uy);
            }});

            // Dibujar inicio y fin del camino
            if (path.length > 0) {{
                const [sr, sc] = path[0];
                const sx = sc * cellSize + cellSize / 2;
                const sy = sr * cellSize + cellSize / 2;
                ctx.fillStyle = '#FF0000';
                ctx.beginPath();
                ctx.arc(sx, sy, cellSize / 4, 0, 2 * Math.PI);
                ctx.fill();

                const [er, ec] = path[path.length - 1];
                const ex = ec * cellSize + cellSize / 2;
                const ey = er * cellSize + cellSize / 2;
                ctx.fillStyle = '#00FF00';
                ctx.beginPath();
                ctx.arc(ex, ey, cellSize / 4, 0, 2 * Math.PI);
                ctx.fill();
            }}
        }}

        drawMap();
    </script>
</body>
</html>
"""
        return html

    def save_html(self, filename: str, explored_nodes: Optional[List[Tuple[int, int]]] = None,
                  path: Optional[List[Tuple[int, int]]] = None) -> str:
        """
        Genera y guarda HTML en archivo.

        Parámetros:
            filename: Nombre del archivo (sin .html)
            explored_nodes: Nodos explorados
            path: Camino encontrado

        Retorna:
            Ruta del archivo creado
        """
        html = self.generate_html(explored_nodes, path)
        output_path = Path(filename).with_suffix('.html')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return str(output_path.absolute())
