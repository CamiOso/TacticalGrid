"""Algoritmos de búsqueda adversarial: Minimax y Alfa-Beta."""

from typing import Tuple, Callable, Optional, List


class GameState:
    """Representa un estado de juego para búsqueda adversarial."""

    def __init__(self, value: int, is_terminal: bool = False):
        self.value = value
        self.is_terminal = is_terminal

    def __repr__(self):
        return f"GameState(value={self.value}, terminal={self.is_terminal})"


class AdversarialResult:
    """Resultado de búsqueda adversarial.

    Atributos:
        best_value: Valor minimax/alfa-beta del estado analizado.
        best_action: Acción recomendada (o None si no hay sucesores).
        nodes_evaluated: Nodos en los que se calculó la utilidad.
        nodes_generated: Nodos totales generados durante la exploración.
        pruned: Ramas evitadas por la poda alfa-beta (solo alfa-beta).
        depth_reached: Profundidad efectiva alcanzada en la búsqueda.
    """

    def __init__(self, best_value: int, best_action: Optional[str] = None,
                 nodes_evaluated: int = 0, nodes_generated: int = 0,
                 pruned: int = 0, depth_reached: int = 0):
        self.best_value = best_value
        self.best_action = best_action
        self.nodes_evaluated = nodes_evaluated
        self.nodes_generated = nodes_generated
        self.pruned = pruned
        self.depth_reached = depth_reached

    def __repr__(self):
        action_str = f", action={self.best_action}" if self.best_action else ""
        return (f"AdversarialResult(value={self.best_value}{action_str}, "
                f"evaluated={self.nodes_evaluated}, generated={self.nodes_generated}, "
                f"pruned={self.pruned})")


def minimax(state: dict, depth: int, is_maximizing: bool,
            eval_func: Callable, get_successors: Callable) -> Tuple[int, int]:
    """
    Algoritmo Minimax para búsqueda adversarial.

    **Propósito**: Encontrar el mejor movimiento para MAX asumiendo que MIN
    (el adversario) también juega óptimamente. No hay sorpresas.

    **Estrategia fundamental**:
    - MAX intenta MAXIMIZAR el valor
    - MIN intenta MINIMIZAR el valor
    - Ambos juegan de forma óptima (conocen los valores finales)

    **Información del estado que utiliza**:
    - Estado actual del juego
    - Función de evaluación eval_func(estado) para nodos terminales
    - Función de generación de sucesores get_successors(estado, is_maximizing)
    - Profundidad actual y máxima permitida

    **Costo Computacional**:
    - Tiempo: O(b^d) donde b=factor de ramificación, d=profundidad
    - Espacio: O(b*d) para la pila de recursión
    - En ajedrez: profundidad 8 = ~10^19 nodos (impracticable)

    **Garantía**: ✓ Encuentra el movimiento ÓPTIMO (teóricamente perfecto)
    asumiendo que el adversario también juega óptimamente.

    **Limitación**: Exponencialmente lento. Impracticable en juegos con
    gran factor de ramificación sin límite de profundidad.

    **MAX vs MIN no son "inteligencias" distintas**:
    Son simplemente roles en el árbol: MAX maximiza, MIN minimiza.
    Ambos siguen la misma lógica: elegir la mejor opción según su objetivo.

    **Ejemplo en Tic-Tac-Toe**:
    - MAX (nosotros) quiere ganar (+10)
    - MIN (adversario) quiere ganar para él (-10)
    - Draw = 0
    Si MAX puede forzar un draw contra un MIN óptimo, minimax retorna 0.

    Args:
        state: Estado actual del juego (diccionario con game_state, moves, etc.)
        depth: Profundidad máxima de búsqueda
        is_maximizing: True si es turno de MAX (maximizar), False para MIN (minimizar)
        eval_func: Función que evalúa estados terminales f(state) -> valor
        get_successors: Función que devuelve [(estado_siguiente, acción), ...]

    Returns:
        (valor_minimax, nodos_evaluados)

    Purpose:           calcular el valor Minimax de un estado asumiendo juego
                       óptimo de ambos bandos (MAX maximiza, MIN minimiza).
    Preconditions:     estado con is_terminal definible; eval_func y get_successors
                       provistas; profundidad >= 0.
    Postconditions:    devuelve el valor óptimo y el conteo de nodos evaluados;
                       no modifica el estado.
    Complexity:        O(b^d) en tiempo, O(b*d) en espacio.
    AI usage:          Yes
    AI intervention:   se consultó IA para revisar la recursión MAX/MIN.
    Student validation: se verificó con tests/test_adversarial.py (Tic-Tac-Toe).
    """
    nodes_evaluated = 1

    # Caso base: profundidad = 0 o estado terminal
    is_terminal = (state.get('is_terminal', False) if isinstance(state, dict)
                   else state.is_terminal())
    if depth == 0 or is_terminal:
        return eval_func(state), nodes_evaluated

    if is_maximizing:
        # MAX intenta maximizar
        max_eval = float('-inf')
        successors = get_successors(state, is_maximizing=True)

        for successor_state, _ in successors:
            eval_val, nodes = minimax(successor_state, depth - 1, False,
                                      eval_func, get_successors)
            max_eval = max(max_eval, eval_val)
            nodes_evaluated += nodes

        return max_eval, nodes_evaluated
    else:
        # MIN intenta minimizar
        min_eval = float('inf')
        successors = get_successors(state, is_maximizing=False)

        for successor_state, _ in successors:
            eval_val, nodes = minimax(successor_state, depth - 1, True,
                                      eval_func, get_successors)
            min_eval = min(min_eval, eval_val)
            nodes_evaluated += nodes

        return min_eval, nodes_evaluated


def alfabeta(state: dict, depth: int, is_maximizing: bool,
             alpha: float, beta: float,
             eval_func: Callable, get_successors: Callable) -> Tuple[int, int]:
    """
    Algoritmo Alfa-Beta: Minimax con poda (optimización).

    **Propósito**: Producir EXACTAMENTE el mismo resultado que Minimax pero
    evaluando MUCHO menos nodos mediante PODA (descartar ramas innecesarias).

    **Mejora sobre Minimax**:
    - Mantiene ventana [alpha, beta] de valores posibles
    - Si descubre que una rama no puede afectar la decisión, la ignora
    - Mismo resultado, ~5-17.5× menos nodos (depende del orden)

    **Información del estado que utiliza**:
    - Todo lo de Minimax, más:
    - alpha: Mejor valor que MAX puede garantizar hasta ahora
    - beta: Mejor valor que MIN puede garantizar hasta ahora

    **Condiciones de Poda**:
    - Para MAX: si encontramos valor > beta, MIN nunca elegirá este nodo
    - Para MIN: si encontramos valor < alpha, MAX nunca lo permitiría

    **Costo Computacional**:
    - Mejor caso: O(b^(d/2)) - se multiplica la profundidad alcanzable
    - Peor caso: O(b^d) - sin poda (si el orden es malo)
    - Esperado: O(b^(3d/4)) - depende del orden de evaluación

    **Optimalidad**: ✓ IDÉNTICA a Minimax - produce exactamente el mismo resultado,
    solo más rápido. Sin "sorpresas" ni aproximaciones.

    **Punto clave - No modifica la decisión**:
    Cambiar el orden de generación de acciones puede cambiar qué nodos se
    evalúan, pero Alfa-Beta SIEMPRE retorna la misma decisión óptima.
    Si Minimax dice "mover en posición X", Alfa-Beta también dirá lo mismo.

    Args:
        state: Estado actual del juego
        depth: Profundidad máxima de búsqueda
        is_maximizing: True si es turno de MAX, False para MIN
        alpha: Mejor valor encontrado por MAX hasta ahora (iniciar con -inf)
        beta: Mejor valor encontrado por MIN hasta ahora (iniciar con +inf)
        eval_func: Función que evalúa estados terminales
        get_successors: Función que devuelve [(estado, acción), ...] en orden

    Returns:
        (valor_alfabeta, nodos_evaluados): Idéntico al de Minimax

    Purpose:           producir el mismo valor que Minimax evaluando menos nodos
                       mediante la ventana [alpha, beta] y la poda.
    Preconditions:     alpha = -inf y beta = +inf en la raíz; mismas entradas que
                       Minimax (estado, profundidad, eval_func, get_successors).
    Postconditions:    devuelve el mismo valor que Minimax y menos (o igual) nodos
                       evaluados; no modifica el estado.
    Complexity:        O(b^(d/2)) en el mejor caso, O(b^d) en el peor.
    AI usage:          Yes
    AI intervention:   se consultó IA para la condición de poda beta <= alpha.
    Student validation: se verificó la equivalencia con Minimax en tests/test_adversarial.py.
    """
    nodes_evaluated = 1

    # Caso base
    is_terminal = (state.get('is_terminal', False) if isinstance(state, dict)
                   else state.is_terminal())
    if depth == 0 or is_terminal:
        return eval_func(state), nodes_evaluated

    if is_maximizing:
        # MAX intenta maximizar
        max_eval = float('-inf')
        successors = get_successors(state, is_maximizing=True)

        for successor_state, _ in successors:
            eval_val, nodes = alfabeta(successor_state, depth - 1, False,
                                       alpha, beta, eval_func, get_successors)
            max_eval = max(max_eval, eval_val)
            nodes_evaluated += nodes
            alpha = max(alpha, eval_val)

            # Poda beta: si MAX encontró algo mejor que lo que MIN permitirá, parar
            if beta <= alpha:
                break

        return max_eval, nodes_evaluated
    else:
        # MIN intenta minimizar
        min_eval = float('inf')
        successors = get_successors(state, is_maximizing=False)

        for successor_state, _ in successors:
            eval_val, nodes = alfabeta(successor_state, depth - 1, True,
                                       alpha, beta, eval_func, get_successors)
            min_eval = min(min_eval, eval_val)
            nodes_evaluated += nodes
            beta = min(beta, eval_val)

            # Poda alfa: si MIN encontró algo mejor que lo que MAX permitirá, parar
            if beta <= alpha:
                break

        return min_eval, nodes_evaluated


def minimax_with_action(state: dict, depth: int, is_maximizing: bool,
                        eval_func: Callable,
                        get_successors: Callable) -> AdversarialResult:
    """
    Minimax que también devuelve la mejor acción.

    Args:
        state: Estado actual del juego
        depth: Profundidad máxima
        is_maximizing: True si es turno de MAX
        eval_func: Función de evaluación
        get_successors: Función para generar sucesores

    Returns:
        AdversarialResult con valor, acción y nodos evaluados
    """
    if is_maximizing:
        best_value = float('-inf')
        best_action = None
        total_nodes = 1

        successors = get_successors(state, is_maximizing=True)
        for successor_state, action in successors:
            value, nodes = minimax(successor_state, depth - 1, False,
                                   eval_func, get_successors)
            total_nodes += nodes

            if value > best_value:
                best_value = value
                best_action = action

        return AdversarialResult(best_value, best_action, total_nodes)
    else:
        best_value = float('inf')
        best_action = None
        total_nodes = 1

        successors = get_successors(state, is_maximizing=False)
        for successor_state, action in successors:
            value, nodes = minimax(successor_state, depth - 1, True,
                                   eval_func, get_successors)
            total_nodes += nodes

            if value < best_value:
                best_value = value
                best_action = action

        return AdversarialResult(best_value, best_action, total_nodes)


def alfabeta_with_action(state: dict, depth: int, is_maximizing: bool,
                         eval_func: Callable,
                         get_successors: Callable) -> AdversarialResult:
    """
    Alfa-Beta que también devuelve la mejor acción.

    Args:
        state: Estado actual del juego
        depth: Profundidad máxima
        is_maximizing: True si es turno de MAX
        eval_func: Función de evaluación
        get_successors: Función para generar sucesores

    Returns:
        AdversarialResult con valor, acción y nodos evaluados
    """
    if is_maximizing:
        best_value = float('-inf')
        best_action = None
        total_nodes = 1
        alpha = float('-inf')
        beta = float('inf')

        successors = get_successors(state, is_maximizing=True)
        for successor_state, action in successors:
            value, nodes = alfabeta(successor_state, depth - 1, False,
                                    alpha, beta, eval_func, get_successors)
            total_nodes += nodes

            if value > best_value:
                best_value = value
                best_action = action
                alpha = max(alpha, value)

            if beta <= alpha:
                break

        return AdversarialResult(best_value, best_action, total_nodes)
    else:
        best_value = float('inf')
        best_action = None
        total_nodes = 1
        alpha = float('-inf')
        beta = float('inf')

        successors = get_successors(state, is_maximizing=False)
        for successor_state, action in successors:
            value, nodes = alfabeta(successor_state, depth - 1, True,
                                    alpha, beta, eval_func, get_successors)
            total_nodes += nodes

            if value < best_value:
                best_value = value
                best_action = action
                beta = min(beta, value)

            if beta <= alpha:
                break

        return AdversarialResult(best_value, best_action, total_nodes)


def minimax_full(state, depth: int, is_maximizing: bool,
                 eval_func: Callable, get_successors: Callable) -> dict:
    """Minimax que retorna métricas completas: generados/evaluados/profundidad.

    Retorna un diccionario {'value', 'evaluated', 'generated', 'depth'}.
    """
    is_terminal = (state.get('is_terminal', False) if isinstance(state, dict)
                   else state.is_terminal())

    if depth == 0 or is_terminal:
        return {'value': eval_func(state), 'evaluated': 1, 'generated': 1, 'depth': 0}

    successors = get_successors(state, is_maximizing=is_maximizing)
    generated = 1  # el propio nodo
    evaluated = 0
    max_depth = 0

    if is_maximizing:
        best = float('-inf')
        for successor_state, _ in successors:
            child = minimax_full(successor_state, depth - 1, False, eval_func, get_successors)
            best = max(best, child['value'])
            generated += child['generated']
            evaluated += child['evaluated']
            max_depth = max(max_depth, 1 + child['depth'])
        if not successors:
            return {'value': eval_func(state), 'evaluated': 1, 'generated': generated, 'depth': 0}
        return {'value': best, 'evaluated': evaluated, 'generated': generated, 'depth': max_depth}
    else:
        best = float('inf')
        for successor_state, _ in successors:
            child = minimax_full(successor_state, depth - 1, True, eval_func, get_successors)
            best = min(best, child['value'])
            generated += child['generated']
            evaluated += child['evaluated']
            max_depth = max(max_depth, 1 + child['depth'])
        if not successors:
            return {'value': eval_func(state), 'evaluated': 1, 'generated': generated, 'depth': 0}
        return {'value': best, 'evaluated': evaluated, 'generated': generated, 'depth': max_depth}


def alfabeta_full(state, depth: int, is_maximizing: bool,
                  alpha: float, beta: float,
                  eval_func: Callable, get_successors: Callable) -> dict:
    """Alfa-beta que retorna métricas completas incluyendo nodos podados.

    Retorna un diccionario {'value', 'evaluated', 'generated', 'pruned', 'depth'}.
    """
    is_terminal = (state.get('is_terminal', False) if isinstance(state, dict)
                   else state.is_terminal())

    if depth == 0 or is_terminal:
        return {'value': eval_func(state), 'evaluated': 1, 'generated': 1,
                'pruned': 0, 'depth': 0}

    successors = get_successors(state, is_maximizing=is_maximizing)
    generated = 1
    evaluated = 0
    pruned = 0
    max_depth = 0

    if is_maximizing:
        best = float('-inf')
        for i, (successor_state, _) in enumerate(successors):
            child = alfabeta_full(successor_state, depth - 1, False, alpha, beta,
                                  eval_func, get_successors)
            best = max(best, child['value'])
            generated += child['generated']
            evaluated += child['evaluated']
            pruned += child['pruned']
            max_depth = max(max_depth, 1 + child['depth'])
            alpha = max(alpha, child['value'])
            if beta <= alpha:
                # las ramas restantes de este nodo no se generan ni exploran
                pruned += len(successors) - (i + 1)
                break
        if not successors:
            return {'value': eval_func(state), 'evaluated': 1, 'generated': generated,
                    'pruned': pruned, 'depth': 0}
        return {'value': best, 'evaluated': evaluated, 'generated': generated,
                'pruned': pruned, 'depth': max_depth}
    else:
        best = float('inf')
        for i, (successor_state, _) in enumerate(successors):
            child = alfabeta_full(successor_state, depth - 1, True, alpha, beta,
                                  eval_func, get_successors)
            best = min(best, child['value'])
            generated += child['generated']
            evaluated += child['evaluated']
            pruned += child['pruned']
            max_depth = max(max_depth, 1 + child['depth'])
            beta = min(beta, child['value'])
            if beta <= alpha:
                pruned += len(successors) - (i + 1)
                break
        if not successors:
            return {'value': eval_func(state), 'evaluated': 1, 'generated': generated,
                    'pruned': pruned, 'depth': 0}
        return {'value': best, 'evaluated': evaluated, 'generated': generated,
                'pruned': pruned, 'depth': max_depth}


def minimax_with_action_full(state, depth: int, is_maximizing: bool,
                             eval_func: Callable,
                             get_successors: Callable) -> AdversarialResult:
    """Minimax que retorna AdversarialResult con métricas completas."""
    successors = get_successors(state, is_maximizing=is_maximizing)

    if is_maximizing:
        best_value = float('-inf')
        best_action = None
        total_generated = 1
        total_evaluated = 0
        max_depth = 0
        for successor_state, action in successors:
            child = minimax_full(successor_state, depth - 1, False, eval_func, get_successors)
            total_generated += child['generated']
            total_evaluated += child['evaluated']
            max_depth = max(max_depth, 1 + child['depth'])
            if child['value'] > best_value:
                best_value = child['value']
                best_action = action
        return AdversarialResult(best_value, best_action, total_evaluated,
                                 total_generated, 0, max_depth)
    else:
        best_value = float('inf')
        best_action = None
        total_generated = 1
        total_evaluated = 0
        max_depth = 0
        for successor_state, action in successors:
            child = minimax_full(successor_state, depth - 1, True, eval_func, get_successors)
            total_generated += child['generated']
            total_evaluated += child['evaluated']
            max_depth = max(max_depth, 1 + child['depth'])
            if child['value'] < best_value:
                best_value = child['value']
                best_action = action
        return AdversarialResult(best_value, best_action, total_evaluated,
                                 total_generated, 0, max_depth)


def alfabeta_with_action_full(state, depth: int, is_maximizing: bool,
                              eval_func: Callable,
                              get_successors: Callable) -> AdversarialResult:
    """Alfa-beta que retorna AdversarialResult con métricas completas."""
    successors = get_successors(state, is_maximizing=is_maximizing)
    alpha = float('-inf')
    beta = float('inf')

    if is_maximizing:
        best_value = float('-inf')
        best_action = None
        total_generated = 1
        total_evaluated = 0
        total_pruned = 0
        max_depth = 0
        for i, (successor_state, action) in enumerate(successors):
            child = alfabeta_full(successor_state, depth - 1, False, alpha, beta,
                                  eval_func, get_successors)
            total_generated += child['generated']
            total_evaluated += child['evaluated']
            total_pruned += child['pruned']
            max_depth = max(max_depth, 1 + child['depth'])
            if child['value'] > best_value:
                best_value = child['value']
                best_action = action
                alpha = max(alpha, child['value'])
            if beta <= alpha:
                total_pruned += len(successors) - (i + 1)
                break
        return AdversarialResult(best_value, best_action, total_evaluated,
                                 total_generated, total_pruned, max_depth)
    else:
        best_value = float('inf')
        best_action = None
        total_generated = 1
        total_evaluated = 0
        total_pruned = 0
        max_depth = 0
        for i, (successor_state, action) in enumerate(successors):
            child = alfabeta_full(successor_state, depth - 1, True, alpha, beta,
                                  eval_func, get_successors)
            total_generated += child['generated']
            total_evaluated += child['evaluated']
            total_pruned += child['pruned']
            max_depth = max(max_depth, 1 + child['depth'])
            if child['value'] < best_value:
                best_value = child['value']
                best_action = action
                beta = min(beta, child['value'])
            if beta <= alpha:
                total_pruned += len(successors) - (i + 1)
                break
        return AdversarialResult(best_value, best_action, total_evaluated,
                                 total_generated, total_pruned, max_depth)
