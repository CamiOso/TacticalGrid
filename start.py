"""Punto de entrada único de TacticalGrid.

Carga uno o varios escenarios JSON y despacha la ejecución según el modo de cada
escenario (`prueba.modo`: "busqueda", "partida" o "adversarial").

Uso:
    python start.py                                   # ejecuta todos los escenarios de scenarios/
    python start.py scenarios/ejemplo_basico.json     # ejecuta un escenario concreto
    python start.py scenarios/ejemplo_basico.json --algoritmo BFS
    python start.py scenarios/terrenos_costosos.json --algoritmo A_ESTRELLA --heuristica distancia_bfs
    python start.py scenarios/divergencia_bfs_ucs.json --algoritmo BEAM --k 4
    python start.py scenarios/partida_simple.json --algoritmo ALFA_BETA --profundidad 2
    python start.py scenarios/adversarial_simple.json --algoritmo MINIMAX --profundidad 3

Sin el argumento `--algoritmo`, en consola interactiva se muestra un menú para que
el usuario elija. El JSON del escenario queda como sugerencia. `--no-preguntar`
evita el menú y usa la sugerencia del JSON (útil para automatización).
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario
from src.algorithms.search import bfs, dfs, ucs, a_star, beam_search
from src.algorithms.heuristics import (
    manhattan_distance, manhattan_weighted_by_terrain, zero_heuristic,
    crear_distancia_bfs,
)
from src.application.test_executor import TestExecutor
from src.application.solution_verifier import SolutionVerifier
from src.application.ascii_visualizer import ASCIIVisualizer

SCENARIOS_DIR = Path(__file__).parent / "scenarios"
MAX_TURNOS = 100

NOMBRES_BUSQUEDA = ("BFS", "DFS", "UCS", "A*", "BEAM")
NOMBRES_HEURISTICA = ("manhattan", "manhattan_pasos", "distancia_bfs", "zero")
NOMBRES_ADVERSARIAL = ("MINIMAX", "ALFA_BETA")

_ALIAS_BUSQUEDA = {
    "BFS": "BFS", "DFS": "DFS", "UCS": "UCS",
    "A*": "A_ESTRELLA", "ASTAR": "A_ESTRELLA", "A_ESTRELLA": "A_ESTRELLA",
    "BEAM": "BEAM", "BEAM_SEARCH": "BEAM",
}
_ALIAS_ADVERSARIAL = {
    "MINIMAX": False, "MINIMAX_PURO": False, "PURO": False,
    "ALFA_BETA": True, "ALFABETA": True, "ALFA-BETA": True, "PODA": True,
}


def normalizar_algoritmo_busqueda(nombre):
    """Devuelve la forma canónica ("BFS", "DFS", "UCS", "A_ESTRELLA", "BEAM")."""
    clave = str(nombre).strip().upper().replace(" ", "_")
    if clave not in _ALIAS_BUSQUEDA:
        raise ValueError(
            f"Algoritmo de búsqueda desconocido: {nombre!r}. Usa: {', '.join(NOMBRES_BUSQUEDA)}")
    return _ALIAS_BUSQUEDA[clave]


def normalizar_algoritmo_adversarial(nombre):
    """Traduce el algoritmo adversarial a usar_poda (True = alfa-beta, False = puro)."""
    clave = str(nombre).strip().upper().replace(" ", "_")
    if clave not in _ALIAS_ADVERSARIAL:
        raise ValueError(
            f"Algoritmo adversarial desconocido: {nombre!r}. Usa: {', '.join(NOMBRES_ADVERSARIAL)}")
    return _ALIAS_ADVERSARIAL[clave]


def _costo_minimo_transitable(scenario):
    """Menor costo de entrada entre los terrenos transitables del escenario."""
    minimo = float("inf")
    for config in scenario.terrain_types.values():
        if config.get("transitable", False):
            minimo = min(minimo, config.get("costo", float("inf")))
    return minimo if minimo != float("inf") else 1.0


def _resolver_heuristica(nombre, grafo, goal, costos):
    """Resuelve el nombre de heurística a una función h(estado) -> float."""
    canonico = str(nombre).strip().lower()
    if canonico == "distancia_bfs":
        min_cost = min(costos.values()) if costos else 1.0
        return crear_distancia_bfs(grafo, goal, min_cost)
    if canonico in ("manhattan", "manhattan_pasos"):
        return manhattan_distance
    if canonico == "zero":
        return zero_heuristic
    raise ValueError(
        f"Heurística desconocida: {nombre!r}. Usa: {', '.join(NOMBRES_HEURISTICA)}")


def _ejecutar_busqueda(executor, algoritmo="A_ESTRELLA", heuristica="manhattan", k=2):
    """Ejecuta la búsqueda del escenario cargado en el executor y la imprime."""
    import time
    sc = executor.scenario
    grafo = executor.create_graph_from_scenario()
    costos = executor.create_costs_from_scenario(grafo)
    unidad_id = sc.test_config.get("unidad_inicio")
    start = sc.get_unit_position(unidad_id)
    goal = sc.test_objective

    print(f"\n=== MODO BÚSQUEDA: {unidad_id} {start} -> {goal} ===")

    canonico = normalizar_algoritmo_busqueda(algoritmo)
    extras = ""
    if canonico == "A_ESTRELLA":
        extras = f" (heurística: {heuristica})"
    elif canonico == "BEAM":
        extras = f" (heurística: {heuristica}, k: {k})"
    print(f"Algoritmo elegido: {canonico}{extras}")

    t0 = time.perf_counter()
    if canonico == "BFS":
        resultado = bfs(grafo, start, goal)
    elif canonico == "DFS":
        resultado = dfs(grafo, start, goal)
    elif canonico == "UCS":
        resultado = ucs(grafo, start, goal, costos)
    elif canonico == "A_ESTRELLA":
        h = _resolver_heuristica(heuristica, grafo, goal, costos)
        resultado = a_star(grafo, start, goal, h, costos)
    else:  # BEAM
        h = _resolver_heuristica(heuristica, grafo, goal, costos)
        resultado = beam_search(grafo, start, goal, h, k=k, costs=costos)
    resultado.elapsed_ms = (time.perf_counter() - t0) * 1000.0

    print("\n--- Resultado ---")
    if resultado.path is None:
        print(json.dumps({"exito": False, "sin_ruta": True}, ensure_ascii=False, indent=2))
        return 0

    info = {
        "exito": True,
        "camino": resultado.path,
        "movimientos": len(resultado.path) - 1,
        "costo": resultado.cost,
        "generados": resultado.generated,
        "expandidos": resultado.expanded,
        "maximo_frontera": resultado.max_frontier,
        "tiempo_ms": round(resultado.elapsed_ms, 3),
    }
    print(json.dumps(info, ensure_ascii=False, indent=2))

    # Verificación independiente
    verifier = SolutionVerifier(sc.to_dict())
    es_valido, reporte = verifier.verify_complete_solution(resultado.path, resultado.cost, goal)
    print("\n--- Verificación independiente ---")
    print(f"[{'OK' if reporte['valid_path'] else 'ERROR'}] Camino válido")
    print(f"[{'OK' if reporte['valid_cost'] else 'ERROR'}] Costo correcto")
    print(f"[{'OK' if reporte['objective_satisfied'] else 'ERROR'}] Objetivo alcanzado")
    print(f"[{'OK' if reporte.get('no_invalid_states', True) else 'ERROR'}] Estados válidos")
    print(f"Resultado: {'VÁLIDA' if es_valido else 'INVÁLIDA'}")
    return 0


def _construir_estado(scenario):
    """Construye el GameState inicial para partida/adversarial."""
    from src.game.state import GameState, Unit

    unidades_a = scenario.get_units_by_team("A")
    unidades_b = scenario.get_units_by_team("B")
    if not unidades_a or not unidades_b:
        return None

    units = []
    for u in scenario.units:
        units.append(Unit(
            id=u["id"], team=u.get("bando", "A"), row=u["fila"], col=u["columna"],
            carries_resource=(scenario.resource_carrier == u["id"])))

    recurso = scenario.resource_position
    if isinstance(recurso, dict):
        recurso = (recurso["fila"], recurso["columna"])

    return GameState(
        scenario_data=scenario.to_dict(), units=units, resource_pos=recurso,
        resource_carrier=scenario.resource_carrier, current_turn=scenario.current_turn)


def _get_successors(state, is_maximizing=None):
    """Genera los sucesores de un GameState: [(estado, acción_str), ...]."""
    out = []
    for unit in state.get_units_by_team(state.current_turn):
        for action in state.get_valid_actions(unit.id):
            ns = state.copy()
            ns.apply_action(unit.id, action)
            out.append((ns, str(action)))
    return out


def _ejecutar_adversarial(scenario, profundidad=None, usar_poda=None):
    """Modo adversarial: evalúa el estado actual y muestra la acción elegida."""
    from src.algorithms.adversarial import minimax_with_action_full, alfabeta_with_action_full
    from src.game.utility import create_minimax_eval_function

    estado = _construir_estado(scenario)
    if estado is None:
        print("Error: se necesita al menos una unidad de cada bando.")
        return 1

    prueba = scenario.test_config or {}
    if profundidad is None:
        profundidad = prueba.get("profundidad") or scenario.max_minimax_depth
    if usar_poda is None:
        usar_poda = bool(prueba.get("usar_poda", True))

    print(f"\n=== MODO ADVERSARIAL (lanza {estado.current_turn}) ===")
    print(f"Profundidad: {profundidad} | Poda alfa-beta: {'sí' if usar_poda else 'no'}")

    util = create_minimax_eval_function("A", "balanced")
    if usar_poda:
        resultado = alfabeta_with_action_full(estado, profundidad, True, util, _get_successors)
    else:
        resultado = minimax_with_action_full(estado, profundidad, True, util, _get_successors)

    if resultado.best_action is None:
        print("No hay acciones legales para el bando que debe actuar.")
        return 1

    print(f"Acción elegida: {resultado.best_action}")
    print(f"Valor: {resultado.best_value:+.1f} | Generados: {resultado.nodes_generated} | "
          f"Evaluados: {resultado.nodes_evaluated} | Podas: {resultado.pruned} | "
          f"Profundidad efectiva: {resultado.depth_reached}")
    return 0


def _ejecutar_partida(scenario, profundidad=None, usar_poda=None):
    """Modo partida: simula la partida por turnos entre dos bandos."""
    from src.algorithms.adversarial import minimax_with_action_full, alfabeta_with_action_full
    from src.game.utility import create_minimax_eval_function
    from src.game.state import Action

    estado = _construir_estado(scenario)
    if estado is None:
        print("Error: se necesita al menos una unidad de cada bando.")
        return 1

    prueba = scenario.test_config or {}
    if profundidad is None:
        profundidad = prueba.get("profundidad") or scenario.max_minimax_depth
    if usar_poda is None:
        usar_poda = bool(prueba.get("usar_poda", True))

    print(f"\n=== MODO PARTIDA ===")
    print(f"Profundidad: {profundidad} | Poda alfa-beta: {'sí' if usar_poda else 'no'}")
    print("-" * 100)

    ejecutar = alfabeta_with_action_full if usar_poda else minimax_with_action_full

    turno = 1
    while not estado.is_terminal() and turno <= MAX_TURNOS:
        bando = estado.current_turn
        util = create_minimax_eval_function(bando, "balanced")
        resultado = ejecutar(estado, profundidad, True, util, _get_successors)
        if resultado.best_action is None:
            print(f"Turno {turno:02d}: {bando} sin acciones legales; se detiene.")
            break

        action_str = resultado.best_action
        aplicado = False
        for unit in estado.get_units_by_team(bando):
            try:
                accion = Action[action_str.split(".")[-1]]
            except KeyError:
                continue
            if accion in estado.get_valid_actions(unit.id):
                if estado.apply_action(unit.id, accion):
                    aplicado = True
                    break
        if not aplicado:
            print(f"Turno {turno:02d}: acción {action_str} no aplicable; se detiene.")
            break

        print(f"Turno {turno:02d} | {bando} -> {action_str} | Valor {resultado.best_value:+.1f} | "
              f"Nodos {resultado.nodes_generated} | Evaluados {resultado.nodes_evaluated} | "
              f"Podas {resultado.pruned}")
        turno += 1

    print("-" * 100)
    ganador = estado.get_winner()
    if ganador:
        print(f"PARTIDA FINALIZADA: gana {ganador} en {turno - 1} turnos.")
    else:
        print(f"PARTIDA EMPATADA: límite de {MAX_TURNOS} turnos sin ganador.")
    return 0


def _ejecutar_escenario(executor, algoritmo=None, heuristica=None, k=None, profundidad=None):
    """Despacha la ejecución según el modo del escenario cargado."""
    sc = executor.scenario
    modo = sc.test_mode
    prueba = sc.test_config or {}

    if modo == "busqueda":
        alg = algoritmo or prueba.get("algoritmo", "A_ESTRELLA")
        heur = heuristica or prueba.get("heuristica", "manhattan")
        ancho = k if k is not None else prueba.get("k", 2)
        return _ejecutar_busqueda(executor, alg, heur, ancho)

    usar_poda = None
    if algoritmo:
        usar_poda = normalizar_algoritmo_adversarial(algoritmo)
    prof = profundidad

    if modo == "adversarial":
        return _ejecutar_adversarial(sc, prof, usar_poda)
    if modo == "partida":
        return _ejecutar_partida(sc, prof, usar_poda)

    print(f"Error: modo desconocido {modo!r}.")
    return 1


def _elegir_busqueda_interactiva(prueba, entrada=input):
    """Menú numerado para elegir el algoritmo de búsqueda."""
    try:
        sugerido = normalizar_algoritmo_busqueda(prueba.get("algoritmo", "A_ESTRELLA"))
    except ValueError:
        sugerido = "A_ESTRELLA"
    opciones = ("BFS", "DFS", "UCS", "A_ESTRELLA", "BEAM")
    etiquetas = {
        "BFS": "BFS (anchura)", "DFS": "DFS (profundidad)", "UCS": "UCS (costo uniforme)",
        "A_ESTRELLA": "A* (heurística)", "BEAM": "Beam Search (haz)"}
    print("\nAlgoritmos disponibles:")
    for i, opcion in enumerate(opciones, 1):
        marca = "  <- sugerido por el JSON" if opcion == sugerido else ""
        print(f"  {i}) {etiquetas[opcion]}{marca}")
    while True:
        try:
            respuesta = entrada(f"Elige [1-{len(opciones)}, Enter = {sugerido}]: ").strip()
        except EOFError:
            return sugerido
        if not respuesta:
            return sugerido
        if respuesta.isdigit() and 1 <= int(respuesta) <= len(opciones):
            return opciones[int(respuesta) - 1]
        print("  Opción inválida.")


def _elegir_heuristica_interactiva(prueba, entrada=input):
    """Menú numerado para elegir la heurística de A*/Beam."""
    sugerida = prueba.get("heuristica", "manhattan")
    if sugerida not in NOMBRES_HEURISTICA:
        sugerida = "manhattan"
    opciones = ("manhattan", "manhattan_pasos", "distancia_bfs", "zero")
    etiquetas = {
        "manhattan": "manhattan (pasos)", "manhattan_pasos": "manhattan_pasos",
        "distancia_bfs": "distancia_bfs (rodeando muros)", "zero": "zero (equivale a UCS)"}
    print("\nHeurísticas disponibles:")
    for i, opcion in enumerate(opciones, 1):
        marca = "  <- sugerida por el JSON" if opcion == sugerida else ""
        print(f"  {i}) {etiquetas[opcion]}{marca}")
    while True:
        try:
            respuesta = entrada(f"Elige [1-{len(opciones)}, Enter = {sugerida}]: ").strip()
        except EOFError:
            return sugerida
        if not respuesta:
            return sugerida
        if respuesta.isdigit() and 1 <= int(respuesta) <= len(opciones):
            return opciones[int(respuesta) - 1]
        print("  Opción inválida.")


def _elegir_k_interactivo(prueba, entrada=input):
    """Pregunta el ancho del haz k para Beam Search."""
    sugerido = prueba.get("k", 2)
    if isinstance(sugerido, bool) or not isinstance(sugerido, int) or sugerido < 1:
        sugerido = 2
    while True:
        try:
            respuesta = entrada(f"Ancho del haz k [Enter = {sugerido}]: ").strip()
        except EOFError:
            return sugerido
        if not respuesta:
            return sugerido
        if respuesta.isdigit() and int(respuesta) >= 1:
            return int(respuesta)
        print("  k inválido.")


def construir_parser():
    """Parser de argumentos de la consola."""
    parser = argparse.ArgumentParser(
        prog="start.py",
        description="TacticalGrid: carga escenarios JSON y ejecuta el modo de cada 'prueba'.")
    parser.add_argument("ruta", nargs="?", default=None,
                        help="escenario JSON (por defecto: todos los de scenarios/)")
    parser.add_argument("--algoritmo", default=None,
                        help="búsqueda: BFS, DFS, UCS, A* o BEAM | jugar: MINIMAX (puro) o ALFA_BETA")
    parser.add_argument("--heuristica", default=None,
                        help="heurística de A*/Beam: manhattan, manhattan_pasos, distancia_bfs o zero")
    parser.add_argument("--k", type=int, default=None, help="ancho del haz para Beam Search")
    parser.add_argument("--profundidad", type=int, default=None,
                        help="profundidad de Minimax para partida/adversarial")
    parser.add_argument("--no-preguntar", action="store_true",
                        help="no mostrar el menú interactivo; usa la sugerencia del JSON")
    return parser


def main(argv=None):
    args = construir_parser().parse_args(argv)

    # Determinar qué escenarios ejecutar
    if args.ruta:
        archivos = [Path(args.ruta)]
    else:
        archivos = sorted(SCENARIOS_DIR.glob("*.json"))
        if not archivos:
            print("No se encontraron escenarios JSON en", SCENARIOS_DIR)
            return 1

    for archivo in archivos:
        print("=" * 70)
        print(f"Ejecutando: {archivo.name}")
        print("=" * 70)

        try:
            executor = TestExecutor()
            executor.load_scenario(archivo)
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
            print(f"❌ Escenario rechazado: {error}")
            continue

        sc = executor.scenario
        print(f"✅ Escenario válido: {sc.rows}x{sc.cols} | {len(sc.units)} unidad(es) | "
              f"turno {sc.current_turn} | modo {sc.test_mode}")

        # Visualización ASCII del mapa
        try:
            visualizer = ASCIIVisualizer(sc)
            visualizer.print_map()
            print()
        except Exception:
            pass

        prueba = sc.test_config or {}

        # Elegir algoritmo si aplica y no vino por bandera
        algoritmo = args.algoritmo
        heuristica = args.heuristica
        k = args.k
        hay_bandera_algo = algoritmo is not None
        preguntar = (not hay_bandera_algo and not args.no_preguntar and sys.stdin.isatty())

        # Normalizar para decidir si preguntar heurística/k
        canonico = None
        if algoritmo is not None and sc.test_mode == "busqueda":
            try:
                canonico = normalizar_algoritmo_busqueda(algoritmo)
            except ValueError:
                canonico = None

        puede_preguntar = not args.no_preguntar and sys.stdin.isatty()
        if sc.test_mode == "busqueda":
            if preguntar:
                algoritmo = _elegir_busqueda_interactiva(prueba)
                try:
                    canonico = normalizar_algoritmo_busqueda(algoritmo)
                except ValueError:
                    canonico = None
            else:
                try:
                    canonico = normalizar_algoritmo_busqueda(algoritmo or prueba.get("algoritmo", "A_ESTRELLA"))
                except ValueError:
                    canonico = "A_ESTRELLA"
            if canonico in ("A_ESTRELLA", "BEAM") and heuristica is None and puede_preguntar:
                heuristica = _elegir_heuristica_interactiva(prueba)
            if canonico == "BEAM" and k is None and puede_preguntar:
                k = _elegir_k_interactivo(prueba)

        try:
            resultado = _ejecutar_escenario(
                executor, algoritmo=algoritmo, heuristica=heuristica, k=k,
                profundidad=args.profundidad)
        except ValueError as error:
            print(f"❌ Error: {error}")
            continue

        if resultado != 0:
            continue

    print("\n" + "=" * 70)
    print("✅ Ejecución completada")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
