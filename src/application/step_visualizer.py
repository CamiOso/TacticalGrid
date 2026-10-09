"""Visualizador interactivo paso a paso."""

from pathlib import Path
from typing import Dict, List
from src.application.search_tracker import SearchTracker


class StepVisualizer:
    """Genera HTML interactivo para ver búsqueda paso a paso."""

    TERRAIN_COLORS = {
        'camino': '#90EE90',      # Verde claro
        'pasto': '#FFD700',       # Dorado
        'bosque': '#228B22',      # Verde oscuro
        'montaña': '#A9A9A9',     # Gris
        'agua': '#4169E1',        # Azul
        'muro': '#000000',        # Negro
    }

    def __init__(self, scenario_data: Dict, cell_size: int = 40):
        self.scenario = scenario_data
        self.cell_size = cell_size
        self.rows = scenario_data['mapa']['filas']
        self.cols = scenario_data['mapa']['columnas']
        self.terrain = scenario_data['terreno']
        self.terrain_types = scenario_data['tipos_terreno']
        self.bases = {
            k: (v['fila'], v['columna'])
            for k, v in scenario_data['bases'].items()
        }

    def generate_html(self, tracker: SearchTracker, algo_name: str) -> str:
        """Genera HTML interactivo con controles de paso."""
        steps = tracker.get_all_steps()
        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Búsqueda Paso a Paso - {algo_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #2196F3;
            padding-bottom: 10px;
        }}
        .controls {{
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }}
        button {{
            padding: 10px 15px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        button:hover {{
            background: #0b7dda;
        }}
        button:disabled {{
            background: #ccc;
            cursor: not-allowed;
        }}
        input[type="range"] {{
            flex: 1;
            min-width: 200px;
            height: 6px;
        }}
        .step-info {{
            margin: 15px 0;
            padding: 10px;
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
            border-radius: 4px;
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
            margin: 20px 0;
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
            margin-right: 8px;
            border: 1px solid #999;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }}
        .stat-box {{
            background: #f0f0f0;
            padding: 10px;
            border-radius: 4px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Búsqueda Paso a Paso: {algo_name}</h1>

        <div class="controls">
            <button id="btnFirst">⏮️ Inicio</button>
            <button id="btnPrev">⬅️ Anterior</button>
            <input type="range" id="slider" min="0" max="{len(steps)-1}" value="0">
            <button id="btnNext">Siguiente ➡️</button>
            <button id="btnLast">Fin ⏭️</button>
            <span id="stepCounter">Paso 1 de {len(steps)}</span>
        </div>

        <div class="step-info">
            <strong>Paso actual:</strong> <span id="stepInfo">Inicio</span>
        </div>

        <div class="stats">
            <div class="stat-box">
                <strong>Nodos explorados:</strong><br><span id="explored">0</span>
            </div>
            <div class="stat-box">
                <strong>Frontera actual:</strong><br><span id="frontier">0</span>
            </div>
            <div class="stat-box">
                <strong>Camino actual:</strong><br><span id="pathLength">0</span>
            </div>
        </div>

        <canvas id="canvas" width="{canvas_width}" height="{canvas_height}"></canvas>

        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #90EE90;"></div>
                Camino
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFD700;"></div>
                Pasto
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #228B22;"></div>
                Bosque
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFA500;"></div>
                Nodos explorados
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF6B6B;"></div>
                Frontera
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF0000;"></div>
                Camino actual
            </div>
        </div>
    </div>

    <script>
        const steps = {self._get_steps_json(steps)};
        const scenario = {self._get_scenario_json()};
        let currentStep = 0;

        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const slider = document.getElementById('slider');
        const stepCounter = document.getElementById('stepCounter');
        const stepInfo = document.getElementById('stepInfo');

        function drawMap(stepIndex) {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const step = steps[stepIndex];

            // Dibujar terreno
            for (let r = 0; r < scenario.rows; r++) {{
                for (let c = 0; c < scenario.cols; c++) {{
                    const terrain = scenario.terrain[r][c];
                    const color = scenario.terrainColors[terrain] || '#CCCCCC';

                    ctx.fillStyle = color;
                    ctx.fillRect(c * {self.cell_size}, r * {self.cell_size}, {self.cell_size}, {self.cell_size});
                    ctx.strokeStyle = '#ccc';
                    ctx.lineWidth = 0.5;
                    ctx.strokeRect(c * {self.cell_size}, r * {self.cell_size}, {self.cell_size}, {self.cell_size});
                }}
            }}

            // Dibujar nodos explorados (fondo naranja)
            ctx.fillStyle = 'rgba(255, 165, 0, 0.3)';
            for (const pos of step.explored) {{
                const [r, c] = pos;
                ctx.fillRect(c * {self.cell_size}, r * {self.cell_size}, {self.cell_size}, {self.cell_size});
            }}

            // Dibujar frontera (borde rojo)
            ctx.strokeStyle = '#FF6B6B';
            ctx.lineWidth = 2;
            for (const pos of step.frontier) {{
                const [r, c] = pos;
                ctx.strokeRect(c * {self.cell_size} + 2, r * {self.cell_size} + 2, {self.cell_size - 4}, {self.cell_size - 4});
            }}

            // Dibujar bases
            for (const [team, pos] of Object.entries(scenario.bases)) {{
                const [r, c] = pos;
                ctx.fillStyle = team === 'A' ? '#FF0000' : '#0000FF';
                ctx.fillRect(c * {self.cell_size} + 5, r * {self.cell_size} + 5, {self.cell_size - 10}, {self.cell_size - 10});
            }}

            // Dibujar camino actual en rojo
            if (step.path && step.path.length > 0) {{
                ctx.strokeStyle = '#FF0000';
                ctx.lineWidth = 3;
                ctx.beginPath();
                const [startR, startC] = step.path[0];
                ctx.moveTo(startC * {self.cell_size} + {self.cell_size // 2}, startR * {self.cell_size} + {self.cell_size // 2});

                for (let i = 1; i < step.path.length; i++) {{
                    const [r, c] = step.path[i];
                    ctx.lineTo(c * {self.cell_size} + {self.cell_size // 2}, r * {self.cell_size} + {self.cell_size // 2});
                }}
                ctx.stroke();

                // Dibujar nodo actual
                const [r, c] = step.path[step.path.length - 1];
                ctx.fillStyle = '#00FF00';
                ctx.beginPath();
                ctx.arc(c * {self.cell_size} + {self.cell_size // 2}, r * {self.cell_size} + {self.cell_size // 2}, 8, 0, 2 * Math.PI);
                ctx.fill();
            }}

            // Actualizar info
            currentStep = stepIndex;
            stepCounter.textContent = `Paso ${{stepIndex + 1}} de ${{steps.length}}`;
            stepInfo.textContent = `Expandiendo nodo: ${{step.node}}`;
            document.getElementById('explored').textContent = step.explored.length;
            document.getElementById('frontier').textContent = step.frontier.length;
            document.getElementById('pathLength').textContent = step.path ? step.path.length - 1 : 0;
            slider.value = stepIndex;
        }}

        document.getElementById('btnFirst').onclick = () => drawMap(0);
        document.getElementById('btnPrev').onclick = () => currentStep > 0 && drawMap(currentStep - 1);
        document.getElementById('btnNext').onclick = () => currentStep < steps.length - 1 && drawMap(currentStep + 1);
        document.getElementById('btnLast').onclick = () => drawMap(steps.length - 1);
        slider.oninput = (e) => drawMap(parseInt(e.target.value));

        // Dibuja el primer paso
        drawMap(0);
    </script>
</body>
</html>
"""
        return html

    def _get_steps_json(self, steps: List) -> str:
        """Convierte steps a JSON."""
        import json
        simplified = []
        for step in steps:
            simplified.append({
                'node': list(step['node']) if isinstance(step['node'], tuple) else step['node'],
                'path': [list(p) if isinstance(p, tuple) else p for p in step['path']],
                'explored': [list(p) if isinstance(p, tuple) else p for p in step['explored']],
                'frontier': [list(p) if isinstance(p, tuple) else p for p in step.get('frontier', [])]
            })
        return json.dumps(simplified)

    def _get_scenario_json(self) -> str:
        """Convierte scenario a JSON para JavaScript."""
        import json
        return json.dumps({
            'rows': self.rows,
            'cols': self.cols,
            'terrain': self.terrain,
            'terrainColors': self.TERRAIN_COLORS,
            'bases': {k: list(v) for k, v in self.bases.items()}
        })

    def save_html(self, tracker: SearchTracker, algo_name: str, filename: str = None) -> str:
        """Guarda HTML a archivo."""
        if filename is None:
            filename = f"paso_a_paso_{algo_name.lower().replace('*', 'star')}.html"

        html = self.generate_html(tracker, algo_name)
        filepath = Path(__file__).parent.parent.parent / filename
        filepath.write_text(html, encoding='utf-8')

        return str(filepath)
