"""Tests para validación y carga de escenarios JSON."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scenario.validator import ScenarioValidator
from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario


def test_scenario_structure():
    """Test: Validar estructura básica correcta."""
    scenario = {
        "version": "1.0",
        "mapa": {"filas": 3, "columnas": 3},
        "tipos_terreno": {
            "camino": {"costo": 1, "transitable": True},
            "muro": {"costo": 0, "transitable": False}
        },
        "terreno": [
            ["camino", "camino", "camino"],
            ["camino", "muro", "camino"],
            ["camino", "camino", "camino"]
        ],
        "bases": {
            "A": {"fila": 0, "columna": 0},
            "B": {"fila": 2, "columna": 2}
        },
        "recurso": {"fila": 1, "columna": 1},
        "unidades": [
            {"id": "A1", "bando": "A", "tipo": "estandar", "fila": 0, "columna": 0},
            {"id": "B1", "bando": "B", "tipo": "estandar", "fila": 2, "columna": 2}
        ],
        "turno": "A",
        "juego": {"portador_recurso": None, "profundidad_maxima_minimax": 4},
        "prueba": {"modo": "busqueda", "unidad_inicio": "A1", "objetivo": {"fila": 2, "columna": 2}}
    }

    is_valid, errors = ScenarioValidator.validate_scenario(scenario)
    assert is_valid, f"Escenario válido debería pasar: {errors}"


def test_missing_required_field():
    """Test: Rechazar escenario sin campo obligatorio."""
    scenario = {
        "version": "1.0",
        # Falta 'mapa'
        "tipos_terreno": {}
    }

    is_valid, errors = ScenarioValidator.validate_scenario(scenario)
    assert not is_valid, "Debería rechazar escenario incompleto"
    assert any("mapa" in e for e in errors), "Error debería mencionar campo faltante"


def test_negative_map_dimensions():
    """Test: Rechazar dimensiones negativas del mapa."""
    scenario = {
        "version": "1.0",
        "mapa": {"filas": -1, "columnas": 3},
        "tipos_terreno": {},
        "terreno": [["camino"]],
        "bases": {},
        "recurso": {"fila": 0, "columna": 0},
        "unidades": [],
        "turno": "A",
        "juego": {},
        "prueba": {}
    }

    is_valid, errors = ScenarioValidator.validate_scenario(scenario)
    assert not is_valid, "Debería rechazar filas negativas"


def test_inconsistent_matrix():
    """Test: Rechazar matriz con dimensiones inconsistentes."""
    scenario = {
        "version": "1.0",
        "mapa": {"filas": 2, "columnas": 3},
        "tipos_terreno": {"camino": {"costo": 1, "transitable": True}},
        "terreno": [
            ["camino", "camino"],  # Solo 2 elementos, debería tener 3
            ["camino", "camino", "camino"]
        ],
        "bases": {"A": {"fila": 0, "columna": 0}},
        "recurso": {"fila": 0, "columna": 0},
        "unidades": [],
        "turno": "A",
        "juego": {},
        "prueba": {}
    }

    is_valid, errors = ScenarioValidator.validate_scenario(scenario)
    assert not is_valid, "Debería rechazar matriz inconsistente"


def test_undefined_terrain_type():
    """Test: Rechazar tipos de terreno no definidos."""
    scenario = {
        "version": "1.0",
        "mapa": {"filas": 1, "columnas": 1},
        "tipos_terreno": {"camino": {"costo": 1, "transitable": True}},
        "terreno": [["bosque"]],  # bosque no está definido
        "bases": {},
        "recurso": {"fila": 0, "columna": 0},
        "unidades": [],
        "turno": "A",
        "juego": {},
        "prueba": {}
    }

    is_valid, errors = ScenarioValidator.validate_scenario(scenario)
    assert not is_valid, "Debería rechazar tipo de terreno no definido"


def test_non_positive_cost_for_transitable():
    """Test: Rechazar terreno transitable con costo no positivo."""
    scenario = {
        "version": "1.0",
        "mapa": {"filas": 1, "columnas": 1},
        "tipos_terreno": {
            "agua": {"costo": 0, "transitable": True}  # Transitable pero costo 0
        },
        "terreno": [["agua"]],
        "bases": {},
        "recurso": {"fila": 0, "columna": 0},
        "unidades": [],
        "turno": "A",
        "juego": {},
        "prueba": {}
    }

    is_valid, errors = ScenarioValidator.validate_scenario(scenario)
    assert not is_valid, "Debería rechazar costo no positivo para transitable"


def test_entity_out_of_bounds():
    """Test: Rechazar bases/unidades fuera del mapa."""
    scenario = {
        "version": "1.0",
        "mapa": {"filas": 2, "columnas": 2},
        "tipos_terreno": {"camino": {"costo": 1, "transitable": True}},
        "terreno": [
            ["camino", "camino"],
            ["camino", "camino"]
        ],
        "bases": {"A": {"fila": 5, "columna": 5}},  # Fuera de rango
        "recurso": {"fila": 0, "columna": 0},
        "unidades": [],
        "turno": "A",
        "juego": {},
        "prueba": {}
    }

    is_valid, errors = ScenarioValidator.validate_scenario(scenario)
    assert not is_valid, "Debería rechazar base fuera del mapa"


def test_unit_on_non_transitable():
    """Test: Rechazar unidad en celda no transitable."""
    scenario = {
        "version": "1.0",
        "mapa": {"filas": 2, "columnas": 2},
        "tipos_terreno": {
            "camino": {"costo": 1, "transitable": True},
            "muro": {"costo": 0, "transitable": False}
        },
        "terreno": [
            ["camino", "muro"],
            ["camino", "camino"]
        ],
        "bases": {"A": {"fila": 0, "columna": 0}},
        "recurso": {"fila": 0, "columna": 0},
        "unidades": [
            {"id": "A1", "bando": "A", "tipo": "estandar", "fila": 0, "columna": 1}
        ],
        "turno": "A",
        "juego": {},
        "prueba": {}
    }

    is_valid, errors = ScenarioValidator.validate_scenario(scenario)
    assert not is_valid, "Debería rechazar unidad en muro"


def test_duplicate_unit_ids():
    """Test: Rechazar IDs de unidad duplicados."""
    scenario = {
        "version": "1.0",
        "mapa": {"filas": 2, "columnas": 2},
        "tipos_terreno": {"camino": {"costo": 1, "transitable": True}},
        "terreno": [["camino", "camino"], ["camino", "camino"]],
        "bases": {"A": {"fila": 0, "columna": 0}},
        "recurso": {"fila": 1, "columna": 1},
        "unidades": [
            {"id": "A1", "bando": "A", "tipo": "estandar", "fila": 0, "columna": 0},
            {"id": "A1", "bando": "A", "tipo": "estandar", "fila": 0, "columna": 1}
        ],
        "turno": "A",
        "juego": {},
        "prueba": {}
    }

    is_valid, errors = ScenarioValidator.validate_scenario(scenario)
    assert not is_valid, "Debería rechazar IDs duplicados"


def test_invalid_turn():
    """Test: Rechazar turno inválido."""
    scenario = {
        "version": "1.0",
        "mapa": {"filas": 1, "columnas": 1},
        "tipos_terreno": {"camino": {"costo": 1, "transitable": True}},
        "terreno": [["camino"]],
        "bases": {},
        "recurso": {"fila": 0, "columna": 0},
        "unidades": [],
        "turno": "C",  # Inválido
        "juego": {},
        "prueba": {}
    }

    is_valid, errors = ScenarioValidator.validate_scenario(scenario)
    assert not is_valid, "Debería rechazar turno inválido"


def test_invalid_resource_carrier():
    """Test: Rechazar portador de recurso que no existe."""
    scenario = {
        "version": "1.0",
        "mapa": {"filas": 1, "columnas": 1},
        "tipos_terreno": {"camino": {"costo": 1, "transitable": True}},
        "terreno": [["camino"]],
        "bases": {},
        "recurso": {"fila": 0, "columna": 0},
        "unidades": [{"id": "A1", "bando": "A", "tipo": "estandar", "fila": 0, "columna": 0}],
        "turno": "A",
        "juego": {"portador_recurso": "A2"},  # A2 no existe
        "prueba": {}
    }

    is_valid, errors = ScenarioValidator.validate_scenario(scenario)
    assert not is_valid, "Debería rechazar portador inexistente"


def test_scenario_loader():
    """Test: Cargar escenario desde JSON."""
    scenario_path = Path(__file__).parent.parent / "scenarios" / "ejemplo_basico.json"
    if not scenario_path.exists():
        print(f"⚠ Saltando test_scenario_loader: archivo no encontrado {scenario_path}")
        return

    scenario = ScenarioLoader.load(scenario_path)
    assert scenario is not None, "Debería cargar escenario"
    assert scenario['mapa']['filas'] == 4
    assert len(scenario['unidades']) == 3


def test_scenario_object():
    """Test: Acceder a propiedades de objeto Scenario."""
    scenario_path = Path(__file__).parent.parent / "scenarios" / "ejemplo_basico.json"
    if not scenario_path.exists():
        print(f"⚠ Saltando test_scenario_object: archivo no encontrado {scenario_path}")
        return

    data = ScenarioLoader.load(scenario_path)
    scenario = Scenario(data)

    assert scenario.rows == 4
    assert scenario.cols == 4
    assert scenario.current_turn == "A"
    assert scenario.resource_position == (2, 2)
    assert scenario.get_base("A") == (0, 0)
    assert scenario.get_base("B") == (3, 3)
    assert len(scenario.units) == 3
    assert scenario.get_unit("A1") is not None


if __name__ == "__main__":
    tests = [
        ("test_scenario_structure", test_scenario_structure),
        ("test_missing_required_field", test_missing_required_field),
        ("test_negative_map_dimensions", test_negative_map_dimensions),
        ("test_inconsistent_matrix", test_inconsistent_matrix),
        ("test_undefined_terrain_type", test_undefined_terrain_type),
        ("test_non_positive_cost_for_transitable", test_non_positive_cost_for_transitable),
        ("test_entity_out_of_bounds", test_entity_out_of_bounds),
        ("test_unit_on_non_transitable", test_unit_on_non_transitable),
        ("test_duplicate_unit_ids", test_duplicate_unit_ids),
        ("test_invalid_turn", test_invalid_turn),
        ("test_invalid_resource_carrier", test_invalid_resource_carrier),
        ("test_scenario_loader", test_scenario_loader),
        ("test_scenario_object", test_scenario_object),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✅ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠ {test_name}: {e}")

    print(f"\n{'='*70}")
    print(f"Resultados: {passed} pasados, {failed} fallidos")
    print(f"{'='*70}")
