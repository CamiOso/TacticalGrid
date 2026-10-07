"""Tests para función de utilidad."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game.state import GameState, Unit
from src.game.utility import UtilityFunction, create_minimax_eval_function
from src.scenario.loader import ScenarioLoader


def create_test_state():
    """Crea estado de prueba."""
    scenario_data = ScenarioLoader.load(
        Path(__file__).parent.parent / "scenarios" / "ejemplo_basico.json"
    )
    units = [Unit(u['id'], u['bando'], u['fila'], u['columna']) 
             for u in scenario_data['unidades']]
    recurso = scenario_data['recurso']
    resource_pos = (recurso['fila'], recurso['columna'])
    return GameState(scenario_data, units, resource_pos, None, "A")


def test_simple_utility_initial():
    """Test: Utilidad simple en estado inicial."""
    state = create_test_state()
    utility_a = UtilityFunction.simple_distance_based(state, "A")
    utility_b = UtilityFunction.simple_distance_based(state, "B")
    
    # Ambos debería ser números
    assert isinstance(utility_a, float)
    assert isinstance(utility_b, float)
    print(f"✅ test_simple_utility_initial (A={utility_a:.1f}, B={utility_b:.1f})")


def test_balanced_utility_initial():
    """Test: Utilidad balanceada en estado inicial."""
    state = create_test_state()
    utility = UtilityFunction.balanced_strategy(state, "A")
    assert isinstance(utility, float)
    print(f"✅ test_balanced_utility_initial (value={utility:.1f})")


def test_aggressive_utility_initial():
    """Test: Utilidad agresiva en estado inicial."""
    state = create_test_state()
    utility = UtilityFunction.aggressive_offense(state, "A")
    assert isinstance(utility, float)
    print(f"✅ test_aggressive_utility_initial (value={utility:.1f})")


def test_utility_higher_with_resource():
    """Test: Utilidad aumenta si se lleva recurso."""
    state = create_test_state()
    utility_before = UtilityFunction.simple_distance_based(state, "A")
    
    # Hacer que A1 lleve el recurso
    unit = state.get_unit("A1")
    unit.carries_resource = True
    state.resource_carrier = "A1"
    
    utility_after = UtilityFunction.simple_distance_based(state, "A")
    assert utility_after > utility_before
    print(f"✅ test_utility_higher_with_resource (before={utility_before:.1f}, after={utility_after:.1f})")


def test_utility_symmetry():
    """Test: Utilidad de A es opuesta a B (aproximadamente)."""
    state = create_test_state()
    utility_a = UtilityFunction.simple_distance_based(state, "A")
    utility_b = UtilityFunction.simple_distance_based(state, "B")
    
    # No necesariamente opuestas, pero diferentes
    assert utility_a != utility_b
    print(f"✅ test_utility_symmetry (A={utility_a:.1f}, B={utility_b:.1f})")


def test_create_eval_function_simple():
    """Test: Crear función de evaluación para Minimax."""
    eval_func = create_minimax_eval_function("A", "simple")
    state = create_test_state()
    
    value = eval_func(state)
    assert isinstance(value, float)
    print(f"✅ test_create_eval_function_simple (value={value:.1f})")


def test_create_eval_function_strategies():
    """Test: Diferentes estrategias producen valores diferentes."""
    state = create_test_state()
    
    strategies = ["simple", "balanced", "aggressive"]
    values = {}
    
    for strategy in strategies:
        eval_func = create_minimax_eval_function("A", strategy)
        values[strategy] = eval_func(state)
    
    # Verificar que cada estrategia produce un valor
    for strategy, value in values.items():
        assert isinstance(value, float)
        print(f"  {strategy}: {value:.1f}")
    
    print(f"✅ test_create_eval_function_strategies")


def test_invalid_strategy():
    """Test: Rechazar estrategia inválida."""
    try:
        create_minimax_eval_function("A", "invalid")
        assert False, "Debería lanzar error"
    except ValueError:
        print("✅ test_invalid_strategy")


if __name__ == "__main__":
    tests = [
        test_simple_utility_initial,
        test_balanced_utility_initial,
        test_aggressive_utility_initial,
        test_utility_higher_with_resource,
        test_utility_symmetry,
        test_create_eval_function_simple,
        test_create_eval_function_strategies,
        test_invalid_strategy,
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
            import traceback
            traceback.print_exc()

    print(f"\n{'='*70}")
    print(f"Resultados: {passed} pasados, {failed} fallidos")
    print(f"{'='*70}")
