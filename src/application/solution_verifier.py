"""Verificador de soluciones"""

from typing import Dict, List, Tuple, Optional
from src.game.state import GameState, Unit


class SolutionVerifier:
    """
    Verifica que una solución (camino o secuencia de acciones) sea válida.

    **Requisitos de validación**:
    1. ✓ Cada movimiento del camino es válido
    2. ✓ Ninguna unidad atraviesa obstáculos
    3. ✓ Costo reportado coincide con transiciones
    4. ✓ Estado final satisface condición objetivo
    5. ✓ No se generan estados inválidos

    **Documentación**:
    - Qué valida
    - Qué información del estado utiliza
    - Costo computacional
    """

    def __init__(self, scenario_data: Dict):
        """
        Inicializa verificador con escenario.

        Parámetros:
            scenario_data: Diccionario del escenario cargado
        """
        self.scenario = scenario_data
        self.terrain_types = scenario_data['tipos_terreno']
        self.terrain = scenario_data['terreno']
        self.rows = scenario_data['mapa']['filas']
        self.cols = scenario_data['mapa']['columnas']
        self.bases = {
            k: (v['fila'], v['columna'])
            for k, v in scenario_data['bases'].items()
        }

    def is_cell_transitable(self, row: int, col: int) -> bool:
        """Verifica si una celda es transitable."""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        terrain_type = self.terrain[row][col]
        return self.terrain_types[terrain_type].get('transitable', False)

    def verify_path(self, path: List[Tuple[int, int]]) -> Tuple[bool, List[str]]:
        """
        **Qué valida**: Que cada celda en el camino es transitable y conectada.

        **Información utilizada**:
        - Lista de posiciones del camino
        - Mapa de terrenos
        - Conectividad (movimientos de 4 direcciones)

        **Costo computacional**: O(n) donde n = longitud del camino

        Parámetros:
            path: Lista de posiciones [(fila, col), ...]

        Retorna:
            (es_válido, lista_de_errores)
        """
        errors = []

        if not path:
            errors.append("Camino vacío")
            return False, errors

        # Verificar cada posición
        for i, (row, col) in enumerate(path):
            # Verificar dentro de límites
            if not (0 <= row < self.rows and 0 <= col < self.cols):
                errors.append(f"Posición {i} ({row}, {col}) fuera del mapa")
                continue

            # Verificar transitable
            if not self.is_cell_transitable(row, col):
                terrain_type = self.terrain[row][col]
                errors.append(
                    f"Posición {i} ({row}, {col}) no es transitable "
                    f"(tipo: {terrain_type})"
                )

            # Verificar conectividad (paso anterior al siguiente)
            if i > 0:
                prev_row, prev_col = path[i - 1]
                # Manhattan distance debe ser 1
                dist = abs(row - prev_row) + abs(col - prev_col)
                if dist != 1:
                    errors.append(
                        f"Salto inválido: {path[i-1]} -> ({row}, {col}) "
                        f"(distancia {dist}, esperada 1)"
                    )

        return len(errors) == 0, errors

    def verify_cost(self, path: List[Tuple[int, int]], reported_cost: float) -> Tuple[bool, List[str]]:
        """
        **Qué valida**: Que el costo reportado coincide con costo real del camino.

        **Información utilizada**:
        - Camino (posiciones)
        - Costos de terrenos desde escenario
        - Costo reportado por algoritmo

        **Costo computacional**: O(n) donde n = longitud del camino

        Parámetros:
            path: Lista de posiciones
            reported_cost: Costo que reportó el algoritmo

        Retorna:
            (es_válido, lista_de_errores)
        """
        errors = []

        if len(path) < 2:
            # Camino de 1 posición (ya estoy en el objetivo)
            if reported_cost != 0:
                errors.append(
                    f"Costo debe ser 0 para camino de 1 posición, "
                    f"se reportó {reported_cost}"
                )
            return len(errors) == 0, errors

        # Calcular costo real
        real_cost = 0.0
        for i in range(len(path) - 1):
            current_row, current_col = path[i]
            next_row, next_col = path[i + 1]

            # Costo de la celda de destino
            terrain_type = self.terrain[next_row][next_col]
            if terrain_type not in self.terrain_types:
                errors.append(
                    f"Tipo de terreno desconocido en ({next_row}, {next_col}): {terrain_type}"
                )
                continue

            cost = self.terrain_types[terrain_type].get('costo', 1)
            real_cost += cost

        # Comparar
        if abs(real_cost - reported_cost) > 0.001:  # Tolerancia pequeña
            errors.append(
                f"Costo mismatch: reportado {reported_cost}, "
                f"calculado {real_cost}"
            )

        return len(errors) == 0, errors

    def verify_objective_satisfaction(self, initial_pos: Tuple[int, int],
                                     final_pos: Tuple[int, int],
                                     objective: Tuple[int, int]) -> Tuple[bool, List[str]]:
        """
        **Qué valida**: Que el estado final satisface el objetivo.

        **Información utilizada**:
        - Posición inicial
        - Posición final alcanzada
        - Objetivo requerido

        **Costo computacional**: O(1)

        Parámetros:
            initial_pos: Posición inicial
            final_pos: Posición final del camino
            objective: Posición objetivo requerida

        Retorna:
            (es_válido, lista_de_errores)
        """
        errors = []

        if final_pos != objective:
            errors.append(
                f"Objetivo no alcanzado: final {final_pos}, "
                f"esperado {objective}"
            )

        return len(errors) == 0, errors

    def verify_no_invalid_states(self, path: List[Tuple[int, int]]) -> Tuple[bool, List[str]]:
        """
        **Qué valida**: Que no se generan estados inválidos en el camino.

        **Estados inválidos**:
        - Posición fuera del mapa
        - Posición en obstáculo

        **Información utilizada**:
        - Camino
        - Mapa

        **Costo computacional**: O(n)

        Parámetros:
            path: Lista de posiciones

        Retorna:
            (es_válido, lista_de_errores)
        """
        errors = []

        for i, (row, col) in enumerate(path):
            if not (0 <= row < self.rows and 0 <= col < self.cols):
                errors.append(f"Posición {i} ({row}, {col}) fuera del mapa")

            if self.is_cell_transitable(row, col):
                # Válida
                continue
            else:
                terrain_type = self.terrain[row][col]
                errors.append(
                    f"Posición {i} ({row}, {col}) es inválida "
                    f"(tipo: {terrain_type})"
                )

        return len(errors) == 0, errors

    def verify_complete_solution(self, path: List[Tuple[int, int]],
                                reported_cost: float,
                                objective: Tuple[int, int]) -> Tuple[bool, Dict]:
        """
        Verifica completamente una solución.

        **Qué valida**:
        1. Camino es válido (conectado, transitable)
        2. Costo coincide
        3. Objetivo satisfecho
        4. Sin estados inválidos

        Parámetros:
            path: Lista de posiciones
            reported_cost: Costo reportado
            objective: Posición objetivo

        Retorna:
            (es_válido, reporte_detallado)
        """
        reporte = {
            'valid_path': False,
            'valid_cost': False,
            'objective_satisfied': False,
            'no_invalid_states': False,
            'overall_valid': False,
            'errors': []
        }

        if not path:
            reporte['errors'].append("Camino vacío")
            return False, reporte

        # 1. Validar camino
        path_ok, path_errors = self.verify_path(path)
        reporte['valid_path'] = path_ok
        reporte['errors'].extend(path_errors)

        if not path_ok:
            return False, reporte

        # 2. Validar costo
        cost_ok, cost_errors = self.verify_cost(path, reported_cost)
        reporte['valid_cost'] = cost_ok
        reporte['errors'].extend(cost_errors)

        # 3. Validar objetivo
        obj_ok, obj_errors = self.verify_objective_satisfaction(
            path[0], path[-1], objective
        )
        reporte['objective_satisfied'] = obj_ok
        reporte['errors'].extend(obj_errors)

        # 4. Validar sin estados inválidos
        states_ok, states_errors = self.verify_no_invalid_states(path)
        reporte['no_invalid_states'] = states_ok
        reporte['errors'].extend(states_errors)

        # Resultado final
        reporte['overall_valid'] = (path_ok and cost_ok and obj_ok and states_ok)

        return reporte['overall_valid'], reporte

    def format_report(self, reporte: Dict) -> str:
        """Formatea reporte de verificación para visualización."""
        lines = []
        lines.append("=" * 70)
        lines.append("VERIFICACIÓN DE SOLUCIÓN")
        lines.append("=" * 70)

        checks = [
            ("Camino válido", reporte['valid_path']),
            ("Costo correcto", reporte['valid_cost']),
            ("Objetivo satisfecho", reporte['objective_satisfied']),
            ("Sin estados inválidos", reporte['no_invalid_states']),
        ]

        for check_name, result in checks:
            status = "✅" if result else "❌"
            lines.append(f"{status} {check_name}")

        if reporte['errors']:
            lines.append("\nErrores encontrados:")
            for error in reporte['errors']:
                lines.append(f"  - {error}")
        else:
            lines.append("\n✅ Sin errores")

        overall = "✅ VÁLIDA" if reporte['overall_valid'] else "❌ INVÁLIDA"
        lines.append(f"\nResultado: {overall}")
        lines.append("=" * 70)

        return "\n".join(lines)
