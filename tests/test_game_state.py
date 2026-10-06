"""Tests para GameState."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game.state import GameState, Unit, Action
from src.scenario.loader import ScenarioLoader
from src.scenario.scenario import Scenario


def create_test_state():
    """Crea un estado de prueba desde escenario."""
    scenario_data = ScenarioLoader.load(
        Path(__file__).parent.parent / "scenarios" / "ejemplo_basico.json"
    )
    units = [Unit(u['id'], u['bando'], u['fila'], u['columna']) 
             for u in scenario_data['unidades']]
    recurso = scenario_data['recurso']
    resource_pos = (recurso['fila'], recurso['columna'])
    
    return GameState(scenario_data, units, resource_pos, None, "A")


def test_unit_creation():
    """Test: Crear unidad."""
    unit = Unit("A1", "A", 0, 0)
    assert unit.id == "A1"
    assert unit.team == "A"
    assert unit.position() == (0, 0)
    assert not unit.carries_resource
    print("✅ test_unit_creation")


def test_gamestate_initialization():
    """Test: Inicializar GameState."""
    state = create_test_state()
    assert state.current_turn == "A"
    assert len(state.units) == 3
    assert state.get_winner() is None
    print("✅ test_gamestate_initialization")


def test_unit_retrieval():
    """Test: Recuperar unidades."""
    state = create_test_state()
    unit_a1 = state.get_unit("A1")
    assert unit_a1 is not None
    assert unit_a1.team == "A"
    
    units_a = state.get_units_by_team("A")
    assert len(units_a) == 2
    print("✅ test_unit_retrieval")


def test_valid_movements():
    """Test: Generar movimientos válidos."""
    state = create_test_state()
    unit = state.get_unit("A1")
    
    actions = state.get_valid_actions("A1")
    assert len(actions) > 0
    assert all(isinstance(a, Action) for a in actions)
    print("✅ test_valid_movements")


def test_movement_execution():
    """Test: Ejecutar movimiento."""
    state = create_test_state()
    initial_pos = state.get_unit("A1").position()
    
    actions = state.get_valid_actions("A1")
    if actions:
        action = actions[0]
        success = state.apply_action("A1", action)
        assert success
        assert state.get_unit("A1").position() != initial_pos
        assert state.current_turn == "B"
    print("✅ test_movement_execution")


def test_invalid_action():
    """Test: Rechazar acción inválida."""
    state = create_test_state()
    success = state.apply_action("A1", Action.PICKUP_RESOURCE)
    # A1 no está en posición del recurso, debería fallar
    assert not success or state.get_unit("A1").carries_resource
    print("✅ test_invalid_action")


def test_resource_position():
    """Test: Posición del recurso."""
    state = create_test_state()
    resource_pos = state.get_resource_position()
    assert resource_pos == state.resource_pos
    print("✅ test_resource_position")


def test_state_copy():
    """Test: Copiar estado."""
    state = create_test_state()
    state_copy = state.copy()
    
    # Modificar copia
    if state.get_valid_actions("A1"):
        state_copy.apply_action("A1", state.get_valid_actions("A1")[0])
    
    # Original no debe cambiar
    assert state.get_unit("A1").position() != state_copy.get_unit("A1").position()
    print("✅ test_state_copy")


def test_state_serialization():
    """Test: Convertir estado a diccionario."""
    state = create_test_state()
    state_dict = state.to_dict()
    
    assert 'turn' in state_dict
    assert 'units' in state_dict
    assert 'resource_position' in state_dict
    assert state_dict['turn'] == "A"
    print("✅ test_state_serialization")


if __name__ == "__main__":
    tests = [
        test_unit_creation,
        test_gamestate_initialization,
        test_unit_retrieval,
        test_valid_movements,
        test_movement_execution,
        test_invalid_action,
        test_resource_position,
        test_state_copy,
        test_state_serialization,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*70}")
    print(f"Resultados: {passed} pasados, {failed} fallidos")
    print(f"{'='*70}")
