"""Interfaz gráfica Tkinter de TacticalGrid.

Una ventana con tres pestañas (Búsqueda, Adversarial y Partida) que carga un
escenario JSON de `scenarios/`, lo dibuja en un Canvas y ejecuta sobre él el modo
elegido, mostrando el tablero, el camino y las métricas.

Purpose:           permitir observar y experimentar con la inteligencia del
                   sistema de forma gráfica (requisito "interfaz y visualización"),
                   sin dependencias externas: solo Tkinter de la biblioteca estándar.
Preconditions:     ejecutar como `python -m src.ui.gui` desde la raíz del proyecto,
                   con el paquete `src` importable.
Postconditions:    abre la ventana; cada pestaña ejecuta búsqueda/adversarial/partida
                   sobre el escenario seleccionado y actualiza el Canvas y el panel
                   de resultados. No modifica archivos del escenario.
Complexity:        la del modo elegido (búsqueda: la del algoritmo; adversarial y
                   partida: O(b^d) por decisión). El dibujo del tablero es O(f*c).
AI usage:          Yes
AI intervention:   la IA escribió el archivo y esta documentación.
Student validation: verificado arrancando la ventana y recorriendo las tres pestañas.
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario
from src.algorithms.search import bfs, dfs, ucs, a_star, beam_search
from src.algorithms.heuristics import (
    manhattan_distance, manhattan_weighted_by_terrain, zero_heuristic,
    crear_distancia_bfs,
)

CELL = 28  # tamaño en píxeles de cada celda del tablero

# Paleta de colores por tipo de terreno (agnóstica al nombre: se colorea por defecto).
TERRAIN_COLORS = {
    "camino": "#e8d8a8",
    "pasto": "#a8d878",
    "bosque": "#5a8f3c",
    "pantano": "#6b8fa3",
    "agua": "#7fb3d5",
}
DEFAULT_TERRAIN = "#d8d8d8"
WALL_COLOR = "#3a3a3a"
BASE_A_COLOR = "#4caf50"
BASE_B_COLOR = "#e91e63"
RESOURCE_COLOR = "#ffd600"
UNIT_A_COLOR = "#2196f3"
UNIT_B_COLOR = "#f44336"

NOMBRES_BUSQUEDA = ("BFS", "DFS", "UCS", "A_ESTRELLA", "BEAM")
NOMBRES_HEURISTICA = ("manhattan", "manhattan_weighted", "distancia_bfs", "zero")


def _costo_minimo(costos):
    return min(costos.values()) if costos else 1.0


def _costo_del_camino(path, costos):
    """Costo real de un camino; BFS/DFS optimizan pasos, no costo."""
    if not path or len(path) < 2:
        return 0
    return sum(costos.get((path[i], path[i + 1]), 1)
               for i in range(len(path) - 1))


def _resolver_heuristica(nombre, grafo, goal, costos):
    if nombre == "distancia_bfs":
        return crear_distancia_bfs(grafo, goal, _costo_minimo(costos))
    if nombre == "manhattan_weighted":
        def h(a, b):
            return manhattan_weighted_by_terrain(a, b, min_cost=_costo_minimo(costos))
        return h
    if nombre == "zero":
        return zero_heuristic
    return manhattan_distance


class TacticalGridApp(tk.Tk):
    """Ventana principal de la interfaz gráfica."""

    def __init__(self):
        super().__init__()
        self.title("TacticalGrid — Sistemas Inteligentes I")
        self.geometry("1080x720")

        self.scenario: Scenario | None = None
        self.scenario_data = None
        self.executor = None

        self._build_widgets()
        self._cargar_escenarios()

    # ---------------------------------------------------------------- UI ----
    def _build_widgets(self):
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")

        ttk.Label(top, text="Escenario:").pack(side="left")
        self.combo_escenarios = ttk.Combobox(top, state="readonly", width=40)
        self.combo_escenarios.pack(side="left", padx=6)
        self.combo_escenarios.bind("<<ComboboxSelected>>", self._on_select)

        ttk.Button(top, text="Abrir archivo...", command=self._abrir_archivo).pack(side="left", padx=4)
        ttk.Button(top, text="Recargar", command=self._recargar).pack(side="left", padx=4)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self._build_busqueda_tab()
        self._build_adversarial_tab()
        self._build_partida_tab()

        self.status = ttk.Label(self, text="Cargue un escenario para comenzar.",
                                padding=4, relief="sunken", anchor="w")
        self.status.pack(fill="x")

    def _build_busqueda_tab(self):
        tab = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(tab, text="Búsqueda")

        controls = ttk.Frame(tab)
        controls.pack(fill="x", pady=4)
        ttk.Label(controls, text="Algoritmo:").pack(side="left")
        self.cmb_algo = ttk.Combobox(controls, state="readonly", width=14,
                                     values=["BFS", "DFS", "UCS", "A*", "BEAM"])
        self.cmb_algo.set("A*")
        self.cmb_algo.pack(side="left", padx=6)
        ttk.Label(controls, text="Heurística:").pack(side="left")
        self.cmb_heur = ttk.Combobox(controls, state="readonly", width=16,
                                     values=["manhattan", "manhattan_weighted", "distancia_bfs", "zero"])
        self.cmb_heur.set("manhattan")
        self.cmb_heur.pack(side="left", padx=6)
        ttk.Label(controls, text="k (Beam):").pack(side="left")
        self.spin_k = ttk.Spinbox(controls, from_=1, to=64, width=5)
        self.spin_k.set(2)
        self.spin_k.pack(side="left", padx=6)
        ttk.Button(controls, text="Ejecutar búsqueda", command=self._ejecutar_busqueda).pack(side="left", padx=6)

        self.canvas_busqueda = tk.Canvas(tab, bg="#ffffff")
        self.canvas_busqueda.pack(side="left", fill="both", expand=True)
        self.txt_busqueda = tk.Text(tab, width=44, wrap="word")
        self.txt_busqueda.pack(side="right", fill="y")

    def _build_adversarial_tab(self):
        tab = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(tab, text="Adversarial")

        controls = ttk.Frame(tab)
        controls.pack(fill="x", pady=4)
        ttk.Label(controls, text="Algoritmo:").pack(side="left")
        self.cmb_adv_algo = ttk.Combobox(controls, state="readonly", width=14,
                                         values=["MINIMAX", "ALFA_BETA"])
        self.cmb_adv_algo.set("ALFA_BETA")
        self.cmb_adv_algo.pack(side="left", padx=6)
        ttk.Label(controls, text="Profundidad:").pack(side="left")
        self.spin_adv_depth = ttk.Spinbox(controls, from_=1, to=10, width=5)
        self.spin_adv_depth.set(2)
        self.spin_adv_depth.pack(side="left", padx=6)
        ttk.Button(controls, text="Evaluar acción", command=self._ejecutar_adversarial).pack(side="left", padx=6)

        self.canvas_adversarial = tk.Canvas(tab, bg="#ffffff")
        self.canvas_adversarial.pack(side="left", fill="both", expand=True)
        self.txt_adversarial = tk.Text(tab, width=44, wrap="word")
        self.txt_adversarial.pack(side="right", fill="y")

    def _build_partida_tab(self):
        tab = ttk.Frame(self.notebook, padding=6)
        self.notebook.add(tab, text="Partida")

        controls = ttk.Frame(tab)
        controls.pack(fill="x", pady=4)
        ttk.Label(controls, text="Profundidad:").pack(side="left")
        self.spin_part_depth = ttk.Spinbox(controls, from_=1, to=10, width=5)
        self.spin_part_depth.set(2)
        self.spin_part_depth.pack(side="left", padx=6)
        ttk.Button(controls, text="Jugar partida", command=self._ejecutar_partida).pack(side="left", padx=6)

        self.canvas_partida = tk.Canvas(tab, bg="#ffffff")
        self.canvas_partida.pack(side="left", fill="both", expand=True)
        self.txt_partida = tk.Text(tab, width=44, wrap="word")
        self.txt_partida.pack(side="right", fill="y")

    # ------------------------------------------------------- escenarios ----
    def _cargar_escenarios(self):
        self._rutas_escenarios = sorted(
            (Path(__file__).parent.parent.parent / "scenarios").glob("*.json"))
        self.combo_escenarios["values"] = [p.name for p in self._rutas_escenarios]
        if self._rutas_escenarios:
            self.combo_escenarios.current(0)
            self._cargar(self._rutas_escenarios[0])

    def _on_select(self, _event=None):
        idx = self.combo_escenarios.current()
        if 0 <= idx < len(self._rutas_escenarios):
            self._cargar(self._rutas_escenarios[idx])

    def _abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar escenario JSON",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")])
        if ruta:
            self._cargar(Path(ruta))

    def _recargar(self):
        if self.scenario_data is not None:
            self._cargar(Path(self.combo_escenarios.get() and
                              self._rutas_escenarios[self.combo_escenarios.current()]))

    def _cargar(self, ruta: Path):
        try:
            data = ScenarioLoader.load(ruta)
            sc = Scenario(data)
        except Exception as e:
            messagebox.showerror("Escenario inválido", str(e))
            return
        self.scenario_data = data
        self.scenario = sc
        from src.application.test_executor import TestExecutor
        self.executor = TestExecutor()
        self.executor.load_scenario(ruta)
        self.status.config(
            text=f"{sc.rows}x{sc.cols} | {len(sc.units)} unidades | modo {sc.test_mode}")
        self._dibujar_todos()

    # ----------------------------------------------------------- dibujo ----
    def _terreno_color(self, tipo, transitable):
        if not transitable:
            return WALL_COLOR
        return TERRAIN_COLORS.get(tipo, DEFAULT_TERRAIN)

    def _dibujar_tablero(self, canvas, camino=None):
        canvas.delete("all")
        sc = self.scenario
        if sc is None:
            return
        self._canvas = canvas
        self._camino = camino
        for r in range(sc.rows):
            for c in range(sc.cols):
                tipo = sc.get_terrain_type(r, c)
                info = sc.terrain_types[tipo]
                color = self._terreno_color(tipo, info.get("transitable", False))
                x0, y0, x1, y1 = self._cell_rect(r, c)
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#cccccc")

        # Bases
        for bando, (r, c) in sc.bases.items():
            color = BASE_A_COLOR if bando == "A" else BASE_B_COLOR
            x0, y0, x1, y1 = self._cell_rect(r, c)
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#000000")
            canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=bando,
                               fill="white", font=("Helvetica", 10, "bold"))

        # Recurso
        r, c = sc.resource_position
        x0, y0, x1, y1 = self._cell_rect(r, c)
        canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="◆",
                           fill=RESOURCE_COLOR, font=("Helvetica", 14, "bold"))

        # Unidades
        for u in sc.units:
            r, c = u["fila"], u["columna"]
            color = UNIT_A_COLOR if u.get("bando") == "A" else UNIT_B_COLOR
            x0, y0, x1, y1 = self._cell_rect(r, c)
            canvas.create_oval(x0 + 3, y0 + 3, x1 - 3, y1 - 3, fill=color, outline="white")
            canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=u["id"],
                               fill="white", font=("Helvetica", 8, "bold"))

        # Camino
        if camino:
            for r, c in camino[1:-1]:
                x0, y0, x1, y1 = self._cell_rect(r, c)
                canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="*",
                                   fill="#0000cc", font=("Helvetica", 12, "bold"))

    def _cell_rect(self, r, c):
        return c * CELL, r * CELL, (c + 1) * CELL, (r + 1) * CELL

    def _dibujar_todos(self):
        self._dibujar_tablero(self.canvas_busqueda)
        self._dibujar_tablero(self.canvas_adversarial)
        self._dibujar_tablero(self.canvas_partida)
        for txt in (self.txt_busqueda, self.txt_adversarial, self.txt_partida):
            txt.delete("1.0", "end")

    # ----------------------------------------------------------- modos ----
    def _grafo_y_costos(self):
        grafo = self.executor.create_graph_from_scenario()
        costos = self.executor.create_costs_from_scenario(grafo)
        return grafo, costos

    def _ejecutar_busqueda(self):
        if self.scenario is None:
            messagebox.showwarning("Sin escenario", "Cargue un escenario primero.")
            return
        sc = self.scenario
        prueba = sc.test_config or {}
        unidad_id = prueba.get("unidad_inicio") or sc.units[0]["id"]
        start = sc.get_unit_position(unidad_id)
        goal = sc.test_objective

        grafo, costos = self._grafo_y_costos()
        algo = self.cmb_algo.get()
        heur = self.cmb_heur.get()
        k = int(self.spin_k.get())

        import time
        t0 = time.perf_counter()
        if algo == "BFS":
            res = bfs(grafo, start, goal)
        elif algo == "DFS":
            res = dfs(grafo, start, goal)
        elif algo == "UCS":
            res = ucs(grafo, start, goal, costos)
        elif algo == "BEAM":
            h = _resolver_heuristica(heur, grafo, goal, costos)
            res = beam_search(grafo, start, goal, h, k=k, costs=costos)
        else:  # A*
            h = _resolver_heuristica(heur, grafo, goal, costos)
            res = a_star(grafo, start, goal, h, costos)
        res.elapsed_ms = (time.perf_counter() - t0) * 1000.0

        texto = f"=== Búsqueda: {algo} ===\n"
        texto += f"Unidad: {unidad_id} {start} -> {goal}\n"
        if algo in ("A*", "BEAM"):
            texto += f"Heurística: {heur}\n"
        if algo == "BEAM":
            texto += f"k: {k}\n"
        if res.path is None:
            texto += "\nSin ruta.\n"
        else:
            costo = res.cost if algo not in ("BFS", "DFS") else _costo_del_camino(res.path, costos)
            texto += (f"\nMovimientos: {len(res.path)-1}\n"
                      f"Costo: {costo}\n"
                      f"Generados: {res.generated}\n"
                      f"Expandidos: {res.expanded}\n"
                      f"Frontera máx: {res.max_frontier}\n"
                      f"Tiempo: {res.elapsed_ms:.2f} ms\n")
        self._mostrar_texto(self.txt_busqueda, texto)
        self._dibujar_tablero(self.canvas_busqueda, camino=res.path)

    def _estado_inicial(self):
        from src.game.state import GameState, Unit
        sc = self.scenario
        units = [Unit(u["id"], u.get("bando", "A"), u["fila"], u["columna"],
                      carries_resource=(sc.resource_carrier == u["id"]))
                 for u in sc.units]
        recurso = sc.resource_position
        return GameState(
            scenario_data=sc.to_dict(), units=units, resource_pos=recurso,
            resource_carrier=sc.resource_carrier, current_turn=sc.current_turn)

    def _get_successors(self, state, is_maximizing=None):
        out = []
        for unit in state.get_units_by_team(state.current_turn):
            for action in state.get_valid_actions(unit.id):
                ns = state.copy()
                ns.apply_action(unit.id, action)
                out.append((ns, f"{unit.id}.{action.name}"))
        return out

    def _ejecutar_adversarial(self):
        if self.scenario is None:
            messagebox.showwarning("Sin escenario", "Cargue un escenario primero.")
            return
        from src.algorithms.adversarial import minimax_with_action_full, alfabeta_with_action_full
        from src.game.utility import create_minimax_eval_function

        estado = self._estado_inicial()
        con_poda = self.cmb_adv_algo.get() == "ALFA_BETA"
        prof = int(self.spin_adv_depth.get())
        util = create_minimax_eval_function("A", "balanced")
        fn = alfabeta_with_action_full if con_poda else minimax_with_action_full
        res = fn(estado, prof, True, util, self._get_successors)

        texto = (f"=== Adversarial: {'Alfa-beta' if con_poda else 'Minimax'} ===\n"
                 f"Profundidad: {prof}\n"
                 f"Acción elegida: {res.best_action}\n"
                 f"Valor: {res.best_value:+.1f}\n"
                 f"Generados: {res.nodes_generated}\n"
                 f"Evaluados: {res.nodes_evaluated}\n"
                 f"Podas: {res.pruned}\n"
                 f"Prof. efectiva: {res.depth_reached}\n")
        self._mostrar_texto(self.txt_adversarial, texto)
        self._dibujar_tablero(self.canvas_adversarial)

    def _ejecutar_partida(self):
        if self.scenario is None:
            messagebox.showwarning("Sin escenario", "Cargue un escenario primero.")
            return
        from src.algorithms.adversarial import alfabeta_with_action_full
        from src.game.utility import create_minimax_eval_function

        estado = self._estado_inicial()
        prof = int(self.spin_part_depth.get())
        lineas = [f"=== Partida (profundidad {prof}) ==="]
        MAX_TURNOS = 100
        turno = 1
        ganador = None
        try:
            while not estado.is_terminal() and turno <= MAX_TURNOS:
                bando = estado.current_turn
                util = create_minimax_eval_function(bando, "balanced")
                res = alfabeta_with_action_full(estado, prof, True, util, self._get_successors)
                if res.best_action is None:
                    lineas.append(f"T{turno:02d}: {bando} sin acciones.")
                    break
                from src.game.state import Action
                try:
                    unidad_id, accion_nombre = res.best_action.split(".", 1)
                    accion = Action[accion_nombre]
                except (ValueError, KeyError):
                    lineas.append(f"T{turno:02d}: acción no aplicable.")
                    break
                if not estado.apply_action(unidad_id, accion):
                    lineas.append(f"T{turno:02d}: acción no aplicable.")
                    break
                lineas.append(f"T{turno:02d} {bando} {res.best_action} val={res.best_value:+.0f}")
                turno += 1
            ganador = estado.get_winner()
            lineas.append("" if ganador else "")
            lineas.append(f"Resultado: {'gana ' + ganador if ganador else 'empate'}")
        except Exception as e:
            lineas.append(f"Error: {e}")
        self._mostrar_texto(self.txt_partida, "\n".join(lineas))
        self._dibujar_tablero(self.canvas_partida)

    def _mostrar_texto(self, widget, texto):
        widget.delete("1.0", "end")
        widget.insert("1.0", texto)


def main():
    app = TacticalGridApp()
    app.mainloop()


if __name__ == "__main__":
    main()
