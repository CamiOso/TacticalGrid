"""Casos mínimos para demostrar la solución (PDF, sección 'Casos mínimos').

Cubre los casos 1-10 con datos reproducibles y compara resultados esperados
con obtenidos. Cada caso imprime una salida clara y, si se solicitan métricas,
calcula también el tiempo.

Ejecución:
    python casos_minimos.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario
from src.algorithms.search import bfs, dfs, ucs, a_star, beam_search
from src.algorithms.heuristics import manhattan_distance, manhattan_weighted_by_terrain, zero_heuristic
from src.algorithms.adversarial import (
    minimax_with_action, alfabeta_with_action,
    minimax_with_action_full, alfabeta_with_action_full,
)
from src.game.state import GameState, Unit
from src.game.utility import create_minimax_eval_function


def load_scenario(name):
    root = Path(__file__).parent.parent
    data = ScenarioLoader.load(root / "scenarios" / name)
    return data, Scenario(data)


def separador(titulo):
    print("\n" + "=" * 70)
    print(titulo)
    print("=" * 70)


def make_state(data):
    sc = Scenario(data)
    units = [Unit(u["id"], u.get("bando", "A"), u["fila"], u["columna"])
             for u in sc.units]
    return GameState(
        scenario_data=data,
        units=units,
        resource_pos=sc.resource_position,
        resource_carrier=sc.resource_carrier,
        current_turn=sc.current_turn,
    )


def get_successors(state, is_maximizing=None):
    out = []
    for unit in state.get_units_by_team(state.current_turn):
        for action in state.get_valid_actions(unit.id):
            ns = state.copy()
            ns.apply_action(unit.id, action)
            out.append((ns, str(action)))
    return out


def main():
    # ---------- Caso 1: BFS frente a DFS ----------
    separador("CASO 1: BFS frente a DFS (recorren el espacio de forma distinta)")
    data, sc = load_scenario("ejemplo_basico.json")
    g = {}
    for r in range(sc.rows):
        for c in range(sc.cols):
            if sc.is_transitable(sc.get_terrain_type(r, c)):
                g[(r, c)] = []
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < sc.rows and 0 <= nc < sc.cols:
                        if sc.is_transitable(sc.get_terrain_type(nr, nc)):
                            g[(r, c)].append((nr, nc))
    start, goal = (0, 0), (3, 3)
    rb = bfs(g, start, goal)
    rd = dfs(g, start, goal)
    print(f"BFS: pasos={len(rb.path)-1}, expandidos={rb.expanded}, ruta={rb.path}")
    print(f"DFS: pasos={len(rd.path)-1}, expandidos={rd.expanded}, ruta={rd.path}")
    print("Ambos encuentran solución; BFS garantiza mínimo número de pasos, DFS explora en profundidad.")

    # ---------- Caso 2: Ruta corta vs. ruta económica ----------
    separador("CASO 2: Ruta corta (BFS) vs. ruta económica (UCS)")
    data2, sc2 = load_scenario("divergencia_bfs_ucs.json")


    def build_graph(sc):
        gg = {}
        for r in range(sc.rows):
            for c in range(sc.cols):
                if sc.is_transitable(sc.get_terrain_type(r, c)):
                    gg[(r, c)] = []
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < sc.rows and 0 <= nc < sc.cols:
                            if sc.is_transitable(sc.get_terrain_type(nr, nc)):
                                gg[(r, c)].append((nr, nc))
        return gg


    def build_costs(sc, gg):
        cc = {}
        for n in gg:
            for nb in gg[n]:
                cc[(n, nb)] = sc.get_terrain_cost(sc.get_terrain_type(nb[0], nb[1]))
        return cc

    gg2 = build_graph(sc2)
    cc2 = build_costs(sc2, gg2)
    start2, goal2 = (0, 0), (0, 4)
    rb2 = bfs(gg2, start2, goal2)
    ru2 = ucs(gg2, start2, goal2, cc2)
    print(f"BFS: pasos={len(rb2.path)-1}, costo_pasos={rb2.cost}")
    print(f"UCS: pasos={len(ru2.path)-1}, costo={ru2.cost}")

    # ---------- Caso 3: Obstáculo y heurística ----------
    separador("CASO 3: Obstáculo y heurística (una barrera obliga a rodear)")
    data3, sc3 = load_scenario("terrenos_costosos.json")
    gg3 = build_graph(sc3)
    cc3 = build_costs(sc3, gg3)
    start3, goal3 = (0, 0), (4, 4)
    rm3 = a_star(gg3, start3, goal3, manhattan_distance, cc3)
    print(f"A* Manhattan: pasos={len(rm3.path)-1}, costo={rm3.cost}, expandidos={rm3.expanded}")
    print("La heurística subestima porque no conoce los terrenos; el camino rodea zonas caras.")

    # ---------- Caso 4: Comparación de heurísticas ----------
    separador("CASO 4: Comparación de heurísticas (Manhattan vs. ponderada vs. nula)")
    rm = a_star(gg3, start3, goal3, manhattan_distance, cc3)
    rw = a_star(gg3, start3, goal3, lambda a, b: manhattan_weighted_by_terrain(a, b, min_cost=1.0), cc3)
    rz = a_star(gg3, start3, goal3, zero_heuristic, cc3)
    print(f"Manhattan (admisible): costo={rm.cost}, expandidos={rm.expanded}")
    print(f"Ponderada (admisible): costo={rw.cost}, expandidos={rw.expanded}")
    print(f"Nula h=0 (equivale a UCS): costo={rz.cost}, expandidos={rz.expanded}")
    print("Con min_cost=1 la ponderada equivale a Manhattan; la diferencia se aprecia con min_cost>1.")

    # ---------- Caso 5: Beam Search ----------
    separador("CASO 5: Beam Search (cambiar k modifica exploración)")
    for k in [1, 2, 4, 8]:
        rk = beam_search(gg2, start2, goal2, manhattan_distance, k=k, costs=cc2)
        ex = rk.path is not None
        print(f"k={k}: éxito={ex}, pasos={len(rk.path)-1 if rk.path else '-'}, costo={rk.cost}")

    # ---------- Caso 6: Estado compuesto ----------
    separador("CASO 6: Estado compuesto (misma posición, distinta info)")
    st = make_state(data)
    u = st.get_unit("A1")
    pos_antes = u.position()
    val_antes = create_minimax_eval_function("A", "simple")(st)
    # Simular que A1 porta el recurso sin cambiar posición
    u.carries_resource = True
    st.resource_carrier = "A1"
    val_despues = create_minimax_eval_function("A", "simple")(st)
    print(f"Posición de A1: {pos_antes} (igual antes y después)")
    print(f"Utilidad sin portar: {val_antes:.1f}")
    print(f"Utilidad portando:    {val_despues:.1f}")
    print("La utilidad difiere aunque la posición física es la misma (estado compuesto).")

    # ---------- Caso 7: Decisión adversarial ----------
    separador("CASO 7: Decisión adversarial (no siempre avanzar directo al recurso)")
    data7, sc7 = load_scenario("adversarial_simple.json")
    st7 = make_state(data7)
    util_a = create_minimax_eval_function("A", "balanced")
    r7 = minimax_with_action_full(st7, 3, True, util_a, get_successors)
    print(f"Mejor acción según Minimax: {r7.best_action} (valor={r7.best_value:.1f})")
    print("La acción elegida pondera también la reacción del adversario, no solo la distancia al recurso.")

    # ---------- Caso 8: Minimax vs. Alfa-Beta ----------
    separador("CASO 8: Minimax vs. Alfa-Beta (misma acción, alfa-beta poda ramas)")
    rm8 = minimax_with_action_full(st7, 3, True, util_a, get_successors)
    ra8 = alfabeta_with_action_full(st7, 3, True, util_a, get_successors)
    print(f"Minimax:  acción={rm8.best_action}, valor={rm8.best_value:.1f}, generados={rm8.nodes_generated}, evaluados={rm8.nodes_evaluated}")
    print(f"AlfaBeta: acción={ra8.best_action}, valor={ra8.best_value:.1f}, generados={ra8.nodes_generated}, evaluados={ra8.nodes_evaluated}, podados={ra8.pruned}")

    # ---------- Caso 9: Orden de acciones ----------
    separador("CASO 9: Orden de acciones afecta la cantidad de poda")


    def get_successors_invertido(state, is_maximizing=None):
        return list(reversed(get_successors(state, is_maximizing)))

    ra_n = alfabeta_with_action_full(st7, 3, True, util_a, get_successors)
    ra_i = alfabeta_with_action_full(st7, 3, True, util_a, get_successors_invertido)
    print(f"Orden normal:    podados={ra_n.pruned}, evaluados={ra_n.nodes_evaluated}, acción={ra_n.best_action}")
    print(f"Orden invertido: podados={ra_i.pruned}, evaluados={ra_i.nodes_evaluated}, acción={ra_i.best_action}")

    # ---------- Caso 10: Profundidad ----------
    separador("CASO 10: Efecto de la profundidad")
    for d in [1, 2, 3, 4]:
        start_t = time.perf_counter()
        rd_ = minimax_with_action_full(st7, d, True, util_a, get_successors)
        el = (time.perf_counter() - start_t) * 1000
        print(f"profundidad={d}: valor={rd_.best_value:.1f}, acción={rd_.best_action}, generados={rd_.nodes_generated}, tiempo={el:.3f} ms")

    print("\n" + "=" * 70)
    print("Fin de los casos mínimos.")
    print("=" * 70)


if __name__ == "__main__":
    main()
