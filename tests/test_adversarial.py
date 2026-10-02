"""Tests para algoritmos adversariales: Minimax y Alfa-Beta."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.algorithms.adversarial import (
    minimax, alfabeta, minimax_with_action, alfabeta_with_action,
    AdversarialResult
)


class SimpleTicTacToe:
    """Implementación simple de Tic-Tac-Toe para tests."""

    def __init__(self, board=None, is_x_turn=True):
        self.board = board if board else [' '] * 9
        self.is_x_turn = is_x_turn

    def get_state_dict(self):
        """Convertir a diccionario para algoritmos."""
        return {
            'board': tuple(self.board),
            'is_x_turn': self.is_x_turn,
            'is_terminal': self.is_game_over()[0]
        }

    def is_game_over(self):
        """Retorna (is_over, winner_code)."""
        # Líneas ganadoras
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Filas
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columnas
            [0, 4, 8], [2, 4, 6]               # Diagonales
        ]

        for line in lines:
            if self.board[line[0]] == self.board[line[1]] == self.board[line[2]] != ' ':
                winner = self.board[line[0]]
                return True, winner

        if ' ' not in self.board:
            return True, 'D'  # Draw

        return False, None

    def evaluate(self):
        """Evaluar estado: X gana (+10), O gana (-10), Empate (0)."""
        is_over, winner = self.is_game_over()
        if not is_over:
            return 0
        if winner == 'X':
            return 10
        elif winner == 'O':
            return -10
        else:
            return 0

    def get_successors(self, is_maximizing):
        """Generar sucesores: [(estado, acción), ...]."""
        successors = []
        player = 'X' if is_maximizing else 'O'
        board = list(self.board)

        for i in range(9):
            if board[i] == ' ':
                new_board = board.copy()
                new_board[i] = player
                new_state = SimpleTicTacToe(new_board, not self.is_x_turn)
                successors.append((new_state.get_state_dict(), f"move_{i}"))

        return successors


def eval_func(state):
    """Evaluar un estado."""
    board = list(state['board'])
    game = SimpleTicTacToe(board, state['is_x_turn'])
    return game.evaluate()


def get_successors_func(state, is_maximizing):
    """Generar sucesores."""
    board = list(state['board'])
    game = SimpleTicTacToe(board, state['is_x_turn'])
    return game.get_successors(is_maximizing)


class TestMinimax:
    """Tests para Minimax."""

    def test_minimax_terminal_state(self):
        """Minimax en estado terminal."""
        # X ganó
        board = ['X', 'X', 'X', 'O', 'O', ' ', ' ', ' ', ' ']
        state = {'board': tuple(board), 'is_x_turn': False, 'is_terminal': True}

        value, nodes = minimax(state, 0, True, eval_func, get_successors_func)

        assert value == 10  # X ganó
        assert nodes == 1

    def test_minimax_empty_board_depth_1(self):
        """Minimax en tablero vacío con profundidad 1."""
        board = [' '] * 9
        state = {'board': tuple(board), 'is_x_turn': True, 'is_terminal': False}

        value, nodes = minimax(state, 1, True, eval_func, get_successors_func)

        # Con profundidad 1, no puede terminar el juego, valor debe ser neutro
        assert isinstance(value, int)
        assert nodes > 1

    def test_minimax_with_action_simple(self):
        """Minimax con acción en tablero casi ganado."""
        # X puede ganar en la siguiente jugada
        board = ['X', 'X', ' ', 'O', 'O', ' ', ' ', ' ', ' ']
        state = {'board': tuple(board), 'is_x_turn': True, 'is_terminal': False}

        result = minimax_with_action(state, 2, True, eval_func, get_successors_func)

        assert isinstance(result, AdversarialResult)
        assert result.best_value > 0  # Movimiento ganador
        assert result.best_action is not None
        assert result.nodes_evaluated > 0

    def test_minimax_recognizes_draw(self):
        """Minimax reconoce tablero lleno (empate)."""
        board = ['X', 'O', 'X', 'O', 'X', 'O', 'O', 'X', 'O']
        state = {'board': tuple(board), 'is_x_turn': True, 'is_terminal': True}

        game = SimpleTicTacToe(board, True)
        is_over, winner = game.is_game_over()

        assert is_over
        assert winner == 'D'  # Draw
        assert game.evaluate() == 0


class TestAlfaBeta:
    """Tests para Alfa-Beta."""

    def test_alfabeta_same_as_minimax(self):
        """Alfa-Beta devuelve mismo valor que Minimax."""
        board = ['X', 'X', ' ', 'O', 'O', ' ', ' ', ' ', ' ']
        state = {'board': tuple(board), 'is_x_turn': True, 'is_terminal': False}

        minimax_val, minimax_nodes = minimax(state, 2, True, eval_func, get_successors_func)
        alfabeta_val, alfabeta_nodes = alfabeta(state, 2, True, float('-inf'), float('inf'),
                                                eval_func, get_successors_func)

        assert minimax_val == alfabeta_val
        assert alfabeta_nodes <= minimax_nodes  # Alfa-beta evalúa menos o igual

    def test_alfabeta_with_action_same_value(self):
        """Alfa-Beta con acción devuelve mismo valor que Minimax."""
        board = ['X', 'X', ' ', 'O', 'O', ' ', ' ', ' ', ' ']
        state = {'board': tuple(board), 'is_x_turn': True, 'is_terminal': False}

        result_minimax = minimax_with_action(state, 2, True, eval_func, get_successors_func)
        result_alfabeta = alfabeta_with_action(state, 2, True, eval_func, get_successors_func)

        assert result_minimax.best_value == result_alfabeta.best_value
        assert result_alfabeta.nodes_evaluated <= result_minimax.nodes_evaluated

    def test_alfabeta_pruning_effect(self):
        """Alfa-Beta poda significativamente en problemas grandes."""
        board = [' '] * 9  # Tablero vacío
        state = {'board': tuple(board), 'is_x_turn': True, 'is_terminal': False}

        minimax_val, minimax_nodes = minimax(state, 3, True, eval_func, get_successors_func)
        alfabeta_val, alfabeta_nodes = alfabeta(state, 3, True, float('-inf'), float('inf'),
                                                eval_func, get_successors_func)

        assert minimax_val == alfabeta_val
        # Alfa-beta debería podar bastante
        assert alfabeta_nodes < minimax_nodes

    def test_alfabeta_terminal_state(self):
        """Alfa-Beta en estado terminal."""
        board = ['X', 'X', 'X', 'O', 'O', ' ', ' ', ' ', ' ']
        state = {'board': tuple(board), 'is_x_turn': False, 'is_terminal': True}

        value, nodes = alfabeta(state, 0, False, float('-inf'), float('inf'),
                               eval_func, get_successors_func)

        assert value == 10  # X ganó
        assert nodes == 1


class TestAdversarialResult:
    """Tests para AdversarialResult."""

    def test_result_with_action(self):
        """AdversarialResult con acción."""
        result = AdversarialResult(5, "move_1", 100)

        assert result.best_value == 5
        assert result.best_action == "move_1"
        assert result.nodes_evaluated == 100

    def test_result_without_action(self):
        """AdversarialResult sin acción."""
        result = AdversarialResult(3, nodes_evaluated=50)

        assert result.best_value == 3
        assert result.best_action is None
        assert result.nodes_evaluated == 50


if __name__ == "__main__":
    print("Ejecutando tests de Minimax...")
    test_minimax = TestMinimax()
    test_minimax.test_minimax_terminal_state()
    test_minimax.test_minimax_empty_board_depth_1()
    test_minimax.test_minimax_with_action_simple()
    test_minimax.test_minimax_recognizes_draw()
    print("✅ Tests de Minimax pasaron\n")

    print("Ejecutando tests de Alfa-Beta...")
    test_alfabeta = TestAlfaBeta()
    test_alfabeta.test_alfabeta_same_as_minimax()
    test_alfabeta.test_alfabeta_with_action_same_value()
    test_alfabeta.test_alfabeta_pruning_effect()
    test_alfabeta.test_alfabeta_terminal_state()
    print("✅ Tests de Alfa-Beta pasaron\n")

    print("Ejecutando tests de AdversarialResult...")
    test_result = TestAdversarialResult()
    test_result.test_result_with_action()
    test_result.test_result_without_action()
    print("✅ Tests de AdversarialResult pasaron\n")

    print("✅ ¡Todos los tests pasaron!")
