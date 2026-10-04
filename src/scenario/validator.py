"""Validador de escenarios JSON según especificación PDF."""

from typing import Dict, List, Tuple


class ScenarioValidator:
    """
    Valida escenarios JSON según requisitos del PDF.

    Especialmente documenta:
    - Validación de estructura: Rows/columns positive and consistent
    - Validación de terrenos: All used terrains exist, transitable ones have positive cost
    - Validación de entidades: Bases, resource, units within map bounds
    - Validación de unidades: IDs unique, no units on non-transitable cells
    - Validación de turnos: Turn belongs to A or B
    - Validación de portador: Resource carrier exists
    """

    @staticmethod
    def validate_scenario(scenario: Dict) -> Tuple[bool, List[str]]:
        """
        Valida un escenario completo.

        Returns:
            (is_valid, error_messages): True si válido, lista de errores encontrados
        """
        errors = []

        # Validar estructura básica
        errors.extend(ScenarioValidator._validate_basic_structure(scenario))
        if errors:
            return False, errors

        # Validar mapa
        errors.extend(ScenarioValidator._validate_map(scenario))
        if errors:
            return False, errors

        # Validar terrenos
        errors.extend(ScenarioValidator._validate_terrain(scenario))
        if errors:
            return False, errors

        # Validar bases, recurso, unidades
        errors.extend(ScenarioValidator._validate_entities(scenario))
        if errors:
            return False, errors

        # Validar turno
        errors.extend(ScenarioValidator._validate_turn(scenario))
        if errors:
            return False, errors

        # Validar portador de recurso
        errors.extend(ScenarioValidator._validate_resource_carrier(scenario))
        if errors:
            return False, errors

        return len(errors) == 0, errors

    @staticmethod
    def _validate_basic_structure(scenario: Dict) -> List[str]:
        """Validar campos obligatorios."""
        required_fields = [
            'version', 'mapa', 'tipos_terreno', 'terreno', 'bases',
            'recurso', 'unidades', 'turno', 'juego', 'prueba'
        ]
        errors = []
        for field in required_fields:
            if field not in scenario:
                errors.append(f"Campo obligatorio faltante: '{field}'")
        return errors

    @staticmethod
    def _validate_map(scenario: Dict) -> List[str]:
        """
        Validar mapa: filas y columnas positivas y consistentes con matriz.

        Documentación:
        - Rows (filas) deben ser > 0
        - Columns (columnas) deben ser > 0
        - Matrix debe tener exactamente filas x columnas elementos
        - Cada fila debe tener exactamente 'columnas' elementos
        """
        errors = []
        mapa = scenario.get('mapa', {})
        filas = mapa.get('filas')
        columnas = mapa.get('columnas')
        terreno = scenario.get('terreno', [])

        if not isinstance(filas, int) or filas <= 0:
            errors.append(f"Filas debe ser entero positivo, se encontró: {filas}")

        if not isinstance(columnas, int) or columnas <= 0:
            errors.append(f"Columnas debe ser entero positivo, se encontró: {columnas}")

        if len(terreno) != filas:
            errors.append(f"Matriz terreno tiene {len(terreno)} filas, esperadas {filas}")

        for i, fila in enumerate(terreno):
            if len(fila) != columnas:
                errors.append(
                    f"Fila {i} de terreno tiene {len(fila)} elementos, "
                    f"esperados {columnas}"
                )

        return errors

    @staticmethod
    def _validate_terrain(scenario: Dict) -> List[str]:
        """
        Validar terrenos: todos los usados existen, los transitables tienen costo positivo.

        Documentación:
        - Todos los tipos en matriz terreno deben existir en tipos_terreno
        - Si transitable=true, costo debe ser > 0
        - Si transitable=false, costo puede ser cualquier valor
        """
        errors = []
        tipos_terreno = scenario.get('tipos_terreno', {})
        terreno = scenario.get('terreno', [])

        # Recopilar tipos usados
        tipos_usados = set()
        for fila in terreno:
            for celda in fila:
                tipos_usados.add(celda)

        # Validar que todos existan
        for tipo in tipos_usados:
            if tipo not in tipos_terreno:
                errors.append(f"Tipo de terreno '{tipo}' usado pero no definido")

        # Validar costos
        for tipo, config in tipos_terreno.items():
            costo = config.get('costo', 0)
            transitable = config.get('transitable', False)

            if transitable and costo <= 0:
                errors.append(
                    f"Tipo '{tipo}' es transitable pero costo no es positivo: {costo}"
                )

        return errors

    @staticmethod
    def _validate_entities(scenario: Dict) -> List[str]:
        """
        Validar bases, recurso y unidades están dentro del mapa.

        Documentación:
        - Base A y B deben estar dentro del mapa
        - Recurso debe estar dentro del mapa
        - Todas las unidades deben estar dentro del mapa
        - Ninguna unidad puede estar en celda no transitable
        - IDs de unidad deben ser únicos
        - Cada unidad pertenece a bando A o B
        """
        errors = []
        mapa = scenario.get('mapa', {})
        filas = mapa.get('filas', 0)
        columnas = mapa.get('columnas', 0)

        def in_bounds(fila: int, columna: int) -> bool:
            return 0 <= fila < filas and 0 <= columna < columnas

        # Validar bases
        bases = scenario.get('bases', {})
        for bando, pos in bases.items():
            fila, columna = pos.get('fila'), pos.get('columna')
            if not in_bounds(fila, columna):
                errors.append(f"Base {bando} está fuera del mapa: ({fila}, {columna})")

        # Validar recurso
        recurso = scenario.get('recurso', {})
        fila, columna = recurso.get('fila'), recurso.get('columna')
        if not in_bounds(fila, columna):
            errors.append(f"Recurso está fuera del mapa: ({fila}, {columna})")

        # Validar unidades
        unidades = scenario.get('unidades', [])
        unit_ids = set()
        tipos_terreno = scenario.get('tipos_terreno', {})
        terreno = scenario.get('terreno', [])

        for unit in unidades:
            unit_id = unit.get('id')
            bando = unit.get('bando')
            fila = unit.get('fila')
            columna = unit.get('columna')

            # ID único
            if unit_id in unit_ids:
                errors.append(f"ID de unidad duplicado: {unit_id}")
            unit_ids.add(unit_id)

            # Bando válido
            if bando not in ['A', 'B']:
                errors.append(f"Unidad {unit_id} tiene bando inválido: {bando}")

            # Dentro del mapa
            if not in_bounds(fila, columna):
                errors.append(f"Unidad {unit_id} está fuera del mapa: ({fila}, {columna})")
            else:
                # No en celda no-transitable
                terrain_type = terreno[fila][columna]
                if terrain_type in tipos_terreno:
                    if not tipos_terreno[terrain_type].get('transitable', False):
                        errors.append(
                            f"Unidad {unit_id} está en celda no transitable "
                            f"({fila}, {columna}) tipo '{terrain_type}'"
                        )

        return errors

    @staticmethod
    def _validate_turn(scenario: Dict) -> List[str]:
        """
        Validar turno: es A o B.

        Documentación:
        - turno debe ser "A" o "B"
        """
        errors = []
        turno = scenario.get('turno')
        if turno not in ['A', 'B']:
            errors.append(f"Turno debe ser 'A' o 'B', se encontró: {turno}")
        return errors

    @staticmethod
    def _validate_resource_carrier(scenario: Dict) -> List[str]:
        """
        Validar portador de recurso: si no es null, debe ser unidad existente.

        Documentación:
        - Si juego.portador_recurso no es null, debe coincidir con ID de unidad existente
        """
        errors = []
        juego = scenario.get('juego', {})
        portador = juego.get('portador_recurso')

        if portador is not None:
            unit_ids = {u.get('id') for u in scenario.get('unidades', [])}
            if portador not in unit_ids:
                errors.append(f"Portador de recurso '{portador}' no existe como unidad")

        return errors
