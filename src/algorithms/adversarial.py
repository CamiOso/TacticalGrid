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
    """Resultado de búsqueda adversarial."""

    def __init__(self, best_value: int, best_action: Optional[str] = None,
                 nodes_evaluated: int = 0):
        self.best_value = best_value
        self.best_action = best_action
        self.nodes_evaluated = nodes_evaluated

    def __repr__(self):
        action_str = f", action={self.best_action}" if self.best_action else ""
        return f"AdversarialResult(value={self.best_value}{action_str}, nodes={self.nodes_evaluated})"


def minimax(state: dict, depth: int, is_maximizing: bool,
            eval_func: Callable, get_successors: Callable) -> Tuple[int, int]:
    """
    Algoritmo Minimax para búsqueda adversarial.

    Encuentra el mejor movimiento asumiendo que el adversario juega óptimamente.

    Args:
        state: Estado actual del juego (diccionario con game_state, moves, etc.)
        depth: Profundidad máxima de búsqueda
        is_maximizing: True si es turno de MAX (maximizar), False para MIN (minimizar)
        eval_func: Función que evalúa estados terminales
        get_successors: Función que devuelve [(estado, acción), ...]

    Returns:
        (valor_minimax, nodos_evaluados)
    """
    nodes_evaluated = 1

    # Caso base: profundidad = 0 o estado terminal
    if depth == 0 or state.get('is_terminal', False):
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
    Algoritmo Alfa-Beta: Minimax con poda.

    Más eficiente que Minimax al descartar ramas que no afectarán la decisión.

    Args:
        state: Estado actual del juego
        depth: Profundidad máxima de búsqueda
        is_maximizing: True si es turno de MAX, False para MIN
        alpha: Mejor valor encontrado por MAX hasta ahora
        beta: Mejor valor encontrado por MIN hasta ahora
        eval_func: Función que evalúa estados terminales
        get_successors: Función que devuelve [(estado, acción), ...]

    Returns:
        (valor_alfabeta, nodos_evaluados)
    """
    nodes_evaluated = 1

    # Caso base
    if depth == 0 or state.get('is_terminal', False):
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
