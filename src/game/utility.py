"""Función de utilidad para evaluación de estados en búsqueda adversarial."""

from src.game.state import GameState
from typing import Callable


class UtilityFunction:
    """
    Define cómo evaluar la "bondad" de un estado para un equipo.

    **Propósito**: Permitir que Minimax pueda comparar estados y elegir
    el mejor movimiento. Sin esto, Minimax no puede decidir qué hacer.

    **Consideraciones al diseñar**:
    - ¿Qué factores importan? (distancia, recursos, control)
    - ¿Cuánto pesa cada factor?
    - ¿Qué valor para ganar/perder?

    **Documentación obligatoria según PDF**:
    - Qué intenta estimar la función
    - Qué información del estado utiliza
    - Cuál es su costo computacional
    - Cómo cambiaría el comportamiento si se modifican pesos
    """

    @staticmethod
    def simple_distance_based(state: GameState, team: str) -> float:
        """
        Función simple: solo considera distancia al recurso.

        **Qué intenta estimar**: Cuánto progreso hace un equipo hacia ganar.

        **Información del estado que utiliza**:
        - Posición de todas las unidades del equipo
        - Posición del recurso (o unidad que lo lleva)
        - Posición de la base del equipo

        **Costo computacional**: O(n) donde n = número de unidades

        **Fórmula**:
        - Si equipo ganó: +1000
        - Si equipo perdió: -1000
        - Si lleva recurso: -distancia_a_base * 10
        - Si no lleva: -distancia_a_recurso * 5

        **Limitaciones**:
        - No considera bloqueos
        - No valúa control del territorio
        - Simplista pero funcional
        """
        # Verificar condiciones terminales
        winner = state.get_winner()
        if winner == team:
            return 1000.0
        elif winner is not None:  # El otro equipo ganó
            return -1000.0

        utility = 0.0
        resource_pos = state.get_resource_position()
        base_pos = state.bases[team]

        # Si alguna unidad del equipo lleva el recurso
        for unit in state.get_units_by_team(team):
            if unit.carries_resource:
                dist_to_base = abs(unit.row - base_pos[0]) + abs(unit.col - base_pos[1])
                return float(500 - (dist_to_base * 10))

        # Si no lleva, evalúa proximidad al recurso
        min_dist_to_resource = float('inf')
        for unit in state.get_units_by_team(team):
            dist = abs(unit.row - resource_pos[0]) + abs(unit.col - resource_pos[1])
            min_dist_to_resource = min(min_dist_to_resource, dist)

        if min_dist_to_resource == float('inf'):
            return 0.0

        return float(100 - (min_dist_to_resource * 5))

    @staticmethod
    def balanced_strategy(state: GameState, team: str) -> float:
        """
        Función equilibrada: considera recurso, posición, defensa.

        **Qué intenta estimar**: Balance entre ofensiva (ir por recurso)
        y defensiva (proteger base del adversario).

        **Información del estado que utiliza**:
        - Posiciones de unidades propias y adversarias
        - Quién tiene el recurso
        - Distancias a base propia y adversaria

        **Costo computacional**: O(n²) - compara todas las unidades

        **Estrategia**:
        1. Ganar (llevar recurso a base): peso máximo
        2. Ofensa (ir por recurso): peso alto
        3. Defensa (bloquear adversario): peso medio
        4. Posición (control territorial): peso bajo
        """
        # Verificar ganador
        winner = state.get_winner()
        if winner == team:
            return 5000.0
        elif winner is not None:
            return -5000.0

        utility = 0.0
        resource_pos = state.get_resource_position()
        own_base = state.bases[team]
        enemy_team = "B" if team == "A" else "A"
        enemy_base = state.bases[enemy_team]

        # Componente 1: Llevar recurso (ofensiva)
        for unit in state.get_units_by_team(team):
            if unit.carries_resource:
                dist_to_own_base = abs(unit.row - own_base[0]) + abs(unit.col - own_base[1])
                utility += 2000.0 - (dist_to_own_base * 20.0)

        # Componente 2: Ir por recurso (si nadie lo lleva)
        if not state.resource_carrier:
            for unit in state.get_units_by_team(team):
                dist_to_resource = abs(unit.row - resource_pos[0]) + abs(unit.col - resource_pos[1])
                utility += 500.0 - (dist_to_resource * 8.0)

        # Componente 3: Defensa (evitar que enemigo gane)
        for enemy_unit in state.get_units_by_team(enemy_team):
            if enemy_unit.carries_resource:
                dist_to_enemy_base = abs(enemy_unit.row - enemy_base[0]) + abs(enemy_unit.col - enemy_base[1])
                utility += 100.0 * float(dist_to_enemy_base)

        # Componente 4: Control territorial (posición estratégica)
        for unit in state.get_units_by_team(team):
            dist_to_center = abs(unit.row - state.rows // 2) + abs(unit.col - state.cols // 2)
            utility += 50.0 - float(dist_to_center)

        return utility

    @staticmethod
    def aggressive_offense(state: GameState, team: str) -> float:
        """
        Función agresiva: máxima prioridad al recurso.

        **Estrategia**: Juego ofensivo puro - ir por el recurso sin importar defensa.
        """
        winner = state.get_winner()
        if winner == team:
            return 10000.0
        elif winner is not None:
            return -10000.0

        utility = 0.0
        resource_pos = state.get_resource_position()
        own_base = state.bases[team]

        # Objetivo primario: llevar recurso
        for unit in state.get_units_by_team(team):
            if unit.carries_resource:
                dist = abs(unit.row - own_base[0]) + abs(unit.col - own_base[1])
                return float(3000.0 - (dist * 30.0))

        # Objetivo secundario: ir por recurso
        min_dist = float('inf')
        for unit in state.get_units_by_team(team):
            dist = abs(unit.row - resource_pos[0]) + abs(unit.col - resource_pos[1])
            min_dist = min(min_dist, dist)

        if min_dist == float('inf'):
            return 0.0

        return float(1000.0 - (min_dist * 15.0))


def create_minimax_eval_function(team: str, strategy: str = "balanced") -> Callable:
    """
    Factory function para crear función de evaluación para Minimax.

    Parámetros:
        team: Equipo que va a usar esta función ("A" o "B")
        strategy: Tipo de estrategia ("simple", "balanced", "aggressive")

    Retorna:
        Función que toma GameState y retorna float (valor de utilidad)
    """
    strategies = {
        "simple": UtilityFunction.simple_distance_based,
        "balanced": UtilityFunction.balanced_strategy,
        "aggressive": UtilityFunction.aggressive_offense,
    }

    if strategy not in strategies:
        raise ValueError(f"Estrategia desconocida: {strategy}")

    strategy_func = strategies[strategy]

    def eval_func(state: GameState) -> float:
        """Evalúa el estado desde la perspectiva del equipo."""
        return strategy_func(state, team)

    return eval_func
