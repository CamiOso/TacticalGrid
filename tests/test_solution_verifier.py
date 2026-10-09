"""Tests para verificador de soluciones."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scenario.loader import ScenarioLoader
from src.application.solution_verifier import SolutionVerifier


def create_verifier():
    """Crea verificador desde escenario."""
    scenario_data = ScenarioLoader.load(
        Path(__file__).parent.parent / "scenarios" / "ejemplo_basico.json"
    )
    return SolutionVerifier(scenario_data)


def test_valid_path():
    """Test: Validar camino válido."""
    verifier = create_verifier()
    # Camino válido en ejemplo_basico.json
    path = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), (3, 3)]
    
    is_valid, errors = verifier.verify_path(path)
    assert is_valid, f"Camino válido rechazado: {errors}"
    print("✅ test_valid_path")


def test_invalid_path_out_of_bounds():
    """Test: Rechazar camino fuera del mapa."""
    verifier = create_verifier()
    path = [(0, 0), (10, 10)]
    
    is_valid, errors = verifier.verify_path(path)
    assert not is_valid
    assert any("fuera del mapa" in e for e in errors)
    print("✅ test_invalid_path_out_of_bounds")


def test_invalid_path_disconnected():
    """Test: Rechazar camino desconectado."""
    verifier = create_verifier()
    path = [(0, 0), (2, 2)]
    
    is_valid, errors = verifier.verify_path(path)
    assert not is_valid
    assert any("Salto inválido" in e for e in errors)
    print("✅ test_invalid_path_disconnected")


def test_cost_correct():
    """Test: Validar costo correcto."""
    verifier = create_verifier()
    path = [(0, 0), (1, 0)]
    
    is_valid, errors = verifier.verify_cost(path, 1.0)
    assert is_valid, f"Costo válido rechazado: {errors}"
    print("✅ test_cost_correct")


def test_cost_incorrect():
    """Test: Rechazar costo incorrecto."""
    verifier = create_verifier()
    path = [(0, 0), (1, 0)]
    
    is_valid, errors = verifier.verify_cost(path, 999.0)
    assert not is_valid
    assert any("mismatch" in e for e in errors)
    print("✅ test_cost_incorrect")


def test_objective_satisfied():
    """Test: Objetivo satisfecho."""
    verifier = create_verifier()
    initial = (0, 0)
    final = (3, 3)
    objective = (3, 3)
    
    is_valid, errors = verifier.verify_objective_satisfaction(initial, final, objective)
    assert is_valid, f"Objetivo válido rechazado: {errors}"
    print("✅ test_objective_satisfied")


def test_objective_not_satisfied():
    """Test: Objetivo no satisfecho."""
    verifier = create_verifier()
    initial = (0, 0)
    final = (1, 1)
    objective = (3, 3)
    
    is_valid, errors = verifier.verify_objective_satisfaction(initial, final, objective)
    assert not is_valid
    assert any("Objetivo no alcanzado" in e for e in errors)
    print("✅ test_objective_not_satisfied")


def test_no_invalid_states():
    """Test: Sin estados inválidos."""
    verifier = create_verifier()
    # Camino que evita muros
    path = [(0, 0), (1, 0), (2, 0), (2, 1)]
    
    is_valid, errors = verifier.verify_no_invalid_states(path)
    assert is_valid, f"Estados válidos rechazados: {errors}"
    print("✅ test_no_invalid_states")


def test_complete_valid_solution():
    """Test: Solución completamente válida."""
    verifier = create_verifier()
    # Camino válido en ejemplo_basico.json
    path = [(0, 0), (1, 0)]
    cost = 1.0  # 1 paso en camino (costo 1)
    objective = (1, 0)
    
    is_valid, reporte = verifier.verify_complete_solution(path, cost, objective)
    assert is_valid, f"Solución válida rechazada: {reporte}"
    assert reporte['valid_path']
    assert reporte['valid_cost']
    assert reporte['objective_satisfied']
    print("✅ test_complete_valid_solution")


def test_complete_invalid_solution():
    """Test: Solución inválida."""
    verifier = create_verifier()
    path = [(0, 0), (10, 10)]
    cost = 1.0
    objective = (3, 3)
    
    is_valid, reporte = verifier.verify_complete_solution(path, cost, objective)
    assert not is_valid
    assert len(reporte['errors']) > 0
    print("✅ test_complete_invalid_solution")


def test_format_report():
    """Test: Formatear reporte."""
    verifier = create_verifier()
    path = [(0, 0), (1, 0)]
    cost = 1.0
    objective = (1, 0)
    
    is_valid, reporte = verifier.verify_complete_solution(path, cost, objective)
    formatted = verifier.format_report(reporte)
    
    assert "VERIFICACIÓN" in formatted
    print("✅ test_format_report")


if __name__ == "__main__":
    tests = [
        test_valid_path,
        test_invalid_path_out_of_bounds,
        test_invalid_path_disconnected,
        test_cost_correct,
        test_cost_incorrect,
        test_objective_satisfied,
        test_objective_not_satisfied,
        test_no_invalid_states,
        test_complete_valid_solution,
        test_complete_invalid_solution,
        test_format_report,
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
