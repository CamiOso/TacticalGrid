"""Tests de adaptación del sistema a cambios dinámicos."""

import pytest
import json
from pathlib import Path
from copy import deepcopy

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario
from src.scenario.validator import ScenarioValidator
from src.application.test_executor import TestExecutor


class TestAdaptacionCostos:
    """Verifica que el sistema se adapta a cambios de costos."""

    def load_scenario(self, filename: str):
        """Carga un escenario."""
        path = Path(__file__).parent.parent / "scenarios" / filename
        return ScenarioLoader.load(path)

    def test_cambiar_costo_terreno(self):
        """Cambiar costo de un terreno debe reflejar en resultados."""
        scenario_data = self.load_scenario("divergencia_bfs_ucs.json")

        # Costo original de pasto
        costo_original = scenario_data['tipos_terreno']['pasto']['costo']
        assert costo_original == 5

        # Cambiar costo a 10
        scenario_data['tipos_terreno']['pasto']['costo'] = 10

        # Validar que sigue siendo válido
        is_valid, errors = ScenarioValidator.validate_scenario(scenario_data)
        assert is_valid, f"Escenario inválido después de cambiar costo: {errors}"

    def test_costo_refleja_en_busqueda(self):
        """Cambiar costo debe cambiar resultado de búsqueda."""
        scenario_data = self.load_scenario("divergencia_bfs_ucs.json")
        scenario_original = Scenario(scenario_data)

        # Ejecutar búsqueda original
        executor_original = TestExecutor()
        executor_original.scenario = scenario_original
        graph_original = executor_original.create_graph_from_scenario()
        costs_original = executor_original.create_costs_from_scenario(graph_original)

        # Cambiar costo de pasto de 5 a 1 (más barato)
        scenario_data_modificado = deepcopy(scenario_data)
        scenario_data_modificado['tipos_terreno']['pasto']['costo'] = 1

        scenario_modificado = Scenario(scenario_data_modificado)

        # Ejecutar búsqueda modificada
        executor_modificado = TestExecutor()
        executor_modificado.scenario = scenario_modificado
        graph_modificado = executor_modificado.create_graph_from_scenario()
        costs_modificado = executor_modificado.create_costs_from_scenario(graph_modificado)

        # Verificar que los costos cambiaron
        pasto_edges_original = [
            (edge, cost)
            for edge, cost in costs_original.items()
            if cost == 5
        ]
        pasto_edges_modificado = [
            (edge, cost)
            for edge, cost in costs_modificado.items()
            if cost == 1
        ]

        # Debería haber aristas de pasto con costo 1 ahora
        assert len(pasto_edges_modificado) > 0, "No se reflejó cambio de costo"


class TestAdaptacionPosiciones:
    """Verifica que el sistema se adapta a cambios de posición."""

    def load_scenario(self, filename: str):
        """Carga un escenario."""
        path = Path(__file__).parent.parent / "scenarios" / filename
        return ScenarioLoader.load(path)

    def test_cambiar_posicion_unidad(self):
        """Cambiar posición de unidad debe seguir siendo válido."""
        scenario_data = self.load_scenario("ejemplo_basico.json")

        # Posición original
        unidad_original = scenario_data['unidades'][0]
        fila_original = unidad_original['fila']
        columna_original = unidad_original['columna']

        # Mover a posición diferente (que sea transitable)
        scenario_data['unidades'][0]['fila'] = 2
        scenario_data['unidades'][0]['columna'] = 1

        # Validar
        is_valid, errors = ScenarioValidator.validate_scenario(scenario_data)
        assert is_valid, f"Escenario inválido: {errors}"

        # Nueva posición debe ser diferente
        assert scenario_data['unidades'][0]['fila'] != fila_original
        assert scenario_data['unidades'][0]['columna'] != columna_original

    def test_mover_unidad_a_terreno_valido(self):
        """Mover unidad a terreno transitable debe ser válido."""
        scenario_data = self.load_scenario("ejemplo_basico.json")
        scenario = Scenario(scenario_data)

        # Buscar una posición transitable válida
        nueva_fila = None
        nueva_columna = None
        for r in range(scenario.rows):
            for c in range(scenario.cols):
                terreno = scenario.get_terrain_type(r, c)
                if scenario.terrain_types[terreno]['transitable']:
                    nueva_fila = r
                    nueva_columna = c
                    break
            if nueva_fila is not None:
                break

        assert nueva_fila is not None, "No se encontró posición transitable"

        # Mover
        scenario_data['unidades'][0]['fila'] = nueva_fila
        scenario_data['unidades'][0]['columna'] = nueva_columna

        # Validar
        is_valid, errors = ScenarioValidator.validate_scenario(scenario_data)
        assert is_valid, f"Escenario inválido: {errors}"


class TestAdaptacionObjetivo:
    """Verifica que el sistema se adapta a cambios de objetivo."""

    def load_scenario(self, filename: str):
        """Carga un escenario."""
        path = Path(__file__).parent.parent / "scenarios" / filename
        return ScenarioLoader.load(path)

    def test_cambiar_objetivo_prueba(self):
        """Cambiar objetivo debe ser válido."""
        scenario_data = self.load_scenario("divergencia_bfs_ucs.json")
        scenario = Scenario(scenario_data)

        # Objetivo original
        objetivo_original = scenario_data['prueba']['objetivo']

        # Cambiar objetivo a posición diferente (en terreno válido)
        nuevo_objetivo = {'fila': 2, 'columna': 2}
        terreno = scenario.get_terrain_type(nuevo_objetivo['fila'], nuevo_objetivo['columna'])
        es_transitable = scenario.terrain_types[terreno]['transitable']
        assert es_transitable, "Nuevo objetivo no está en terreno transitable"

        scenario_data['prueba']['objetivo'] = nuevo_objetivo

        # Validar
        is_valid, errors = ScenarioValidator.validate_scenario(scenario_data)
        assert is_valid, f"Escenario inválido: {errors}"

        # Verificar que cambió
        assert scenario_data['prueba']['objetivo'] != objetivo_original


class TestAdaptacionComplejos:
    """Tests complejos de múltiples cambios."""

    def load_scenario(self, filename: str):
        """Carga un escenario."""
        path = Path(__file__).parent.parent / "scenarios" / filename
        return ScenarioLoader.load(path)

    def test_cambios_multiples_simultaneos(self):
        """Cambiar múltiples parámetros simultáneamente."""
        scenario_data = self.load_scenario("ejemplo_basico.json")

        # 1. Cambiar costo de terreno
        scenario_data['tipos_terreno']['camino']['costo'] = 2

        # 2. Cambiar posición de unidad (a terreno transitable)
        scenario_data['unidades'][0]['fila'] = 0
        scenario_data['unidades'][0]['columna'] = 3

        # 3. Cambiar objetivo (a terreno transitable)
        scenario_data['prueba']['objetivo'] = {'fila': 2, 'columna': 3}

        # Validar que todo sigue siendo válido
        is_valid, errors = ScenarioValidator.validate_scenario(scenario_data)
        assert is_valid, f"Escenario con múltiples cambios es inválido: {errors}"

    def test_ejecutar_busqueda_con_cambios(self):
        """Ejecutar búsqueda en escenario modificado."""
        scenario_data = self.load_scenario("divergencia_bfs_ucs.json")

        # Cambiar costo de pasto a 1 (mucho más barato)
        scenario_data['tipos_terreno']['pasto']['costo'] = 1

        # Validar
        is_valid, errors = ScenarioValidator.validate_scenario(scenario_data)
        assert is_valid, f"Escenario modificado es inválido: {errors}"

        # Ejecutar búsqueda
        from copy import deepcopy
        executor = TestExecutor()
        executor.scenario = Scenario(deepcopy(scenario_data))
        try:
            results = executor.execute_test()
            assert 'algoritmos' in results
            assert len(results['algoritmos']) > 0
        except Exception as e:
            pytest.fail(f"Error al ejecutar búsqueda en escenario modificado: {e}")


class TestFlexibilidadSistema:
    """Tests de flexibilidad general del sistema."""

    def load_scenario(self, filename: str):
        """Carga un escenario."""
        path = Path(__file__).parent.parent / "scenarios" / filename
        return ScenarioLoader.load(path)

    def test_cargar_multiple_escenarios(self):
        """Sistema debe soportar cargar múltiples escenarios."""
        scenarios = [
            "divergencia_bfs_ucs.json",
            "ejemplo_basico.json",
            "terrenos_costosos.json",
        ]

        for scenario_file in scenarios:
            data = self.load_scenario(scenario_file)
            scenario = Scenario(data)

            assert scenario.rows > 0
            assert scenario.cols > 0
            assert len(scenario.units) > 0

    def test_cambiar_y_recargar(self):
        """Cambiar parámetro y recargar debe funcionar."""
        from copy import deepcopy

        scenario_data = self.load_scenario("divergencia_bfs_ucs.json")

        # Cambio 1 (copia independiente)
        scenario_data1 = deepcopy(scenario_data)
        scenario_data1['tipos_terreno']['pasto']['costo'] = 10
        scenario1 = Scenario(scenario_data1)
        assert scenario1.get_terrain_cost('pasto') == 10

        # Cambio 2 (copia independiente)
        scenario_data2 = deepcopy(scenario_data)
        scenario_data2['tipos_terreno']['pasto']['costo'] = 2
        scenario2 = Scenario(scenario_data2)
        assert scenario2.get_terrain_cost('pasto') == 2

        # Las instancias deben tener valores diferentes
        assert scenario1.get_terrain_cost('pasto') != scenario2.get_terrain_cost('pasto')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
