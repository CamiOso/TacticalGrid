"""Tests para Beam Search."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.algorithms.search import beam_search
from src.algorithms.heuristics import manhattan_distance


def crear_grafo_simple() -> dict:
    """Crea un grafo simple para pruebas."""
    return {
        (0, 0): [(0, 1), (1, 0)],
        (0, 1): [(0, 0), (0, 2), (1, 1)],
        (0, 2): [(0, 1), (0, 3)],
        (0, 3): [(0, 2), (1, 3)],
        (1, 0): [(0, 0), (1, 1), (2, 0)],
        (1, 1): [(0, 1), (1, 0), (1, 2), (2, 1)],
        (1, 2): [(1, 1), (1, 3)],
        (1, 3): [(0, 3), (1, 2), (2, 3)],
        (2, 0): [(1, 0), (2, 1)],
        (2, 1): [(2, 0), (2, 2)],
        (2, 2): [(2, 1), (2, 3)],
        (2, 3): [(1, 3), (2, 2)],
    }


def test_beam_search_k1():
    """Test: Beam Search con k=1 (greedy puro)."""
    graph = crear_grafo_simple()
    start = (0, 0)
    goal = (2, 3)
    
    result = beam_search(graph, start, goal, manhattan_distance, k=1)
    assert result.path is not None
    assert result.path[0] == start
    assert result.path[-1] == goal
    print(f"✅ test_beam_search_k1 (path_length={len(result.path)-1}, explored={result.explored})")


def test_beam_search_k2():
    """Test: Beam Search con k=2."""
    graph = crear_grafo_simple()
    start = (0, 0)
    goal = (2, 3)
    
    result = beam_search(graph, start, goal, manhattan_distance, k=2)
    assert result.path is not None
    assert result.path[0] == start
    assert result.path[-1] == goal
    print(f"✅ test_beam_search_k2 (path_length={len(result.path)-1}, explored={result.explored})")


def test_beam_search_k4():
    """Test: Beam Search con k=4."""
    graph = crear_grafo_simple()
    start = (0, 0)
    goal = (2, 3)
    
    result = beam_search(graph, start, goal, manhattan_distance, k=4)
    assert result.path is not None
    assert result.path[0] == start
    assert result.path[-1] == goal
    print(f"✅ test_beam_search_k4 (path_length={len(result.path)-1}, explored={result.explored})")


def test_beam_search_k8():
    """Test: Beam Search con k=8."""
    graph = crear_grafo_simple()
    start = (0, 0)
    goal = (2, 3)
    
    result = beam_search(graph, start, goal, manhattan_distance, k=8)
    assert result.path is not None
    assert result.path[0] == start
    assert result.path[-1] == goal
    print(f"✅ test_beam_search_k8 (path_length={len(result.path)-1}, explored={result.explored})")


def test_beam_search_increasing_k():
    """Test: Beam Search con k creciente.
    
    Demostración: A mayor k, más nodos explorados pero mejor camino.
    """
    graph = crear_grafo_simple()
    start = (0, 0)
    goal = (2, 3)
    
    results = {}
    for k in [1, 2, 4, 8]:
        result = beam_search(graph, start, goal, manhattan_distance, k=k)
        results[k] = result
    
    # Verificar que todos encontraron solución
    for k, result in results.items():
        assert result.path is not None, f"k={k} no encontró solución"
    
    # Mostrar resultados
    print(f"\n📊 Análisis Beam Search (k=1,2,4,8):")
    print(f"{'k':<5} {'Pasos':<10} {'Explorados':<12} {'Ratio':<10}")
    print("-" * 37)
    for k in [1, 2, 4, 8]:
        result = results[k]
        pasos = len(result.path) - 1
        ratio = result.explored / results[1].explored if results[1].explored > 0 else 0
        print(f"{k:<5} {pasos:<10} {result.explored:<12} {ratio:.2f}x")
    
    print("✅ test_beam_search_increasing_k")


def test_beam_search_invalid_k():
    """Test: Rechazar k inválido."""
    graph = crear_grafo_simple()
    try:
        beam_search(graph, (0, 0), (2, 3), manhattan_distance, k=0)
        assert False, "Debería rechazar k=0"
    except ValueError:
        print("✅ test_beam_search_invalid_k")


def test_beam_search_same_start_goal():
    """Test: Start == Goal."""
    graph = crear_grafo_simple()
    result = beam_search(graph, (0, 0), (0, 0), manhattan_distance, k=2)
    assert result.path == [(0, 0)]
    assert result.explored == 1
    print("✅ test_beam_search_same_start_goal")


if __name__ == "__main__":
    tests = [
        test_beam_search_k1,
        test_beam_search_k2,
        test_beam_search_k4,
        test_beam_search_k8,
        test_beam_search_increasing_k,
        test_beam_search_invalid_k,
        test_beam_search_same_start_goal,
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
