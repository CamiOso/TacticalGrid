"""Ejemplos de algoritmos adversariales: Minimax y Alfa-Beta."""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from src.algorithms.adversarial import (
    minimax_with_action, alfabeta_with_action
)


class SimpleTicTacToe:
    """Tic-Tac-Toe simple para ejemplos."""

    def __init__(self, board=None, is_x_turn=True):
        self.board = board if board else [' '] * 9
        self.is_x_turn = is_x_turn

    def get_state_dict(self):
        return {
            'board': tuple(self.board),
            'is_x_turn': self.is_x_turn,
            'is_terminal': self.is_game_over()[0]
        }

    def is_game_over(self):
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for line in lines:
            if self.board[line[0]] == self.board[line[1]] == self.board[line[2]] != ' ':
                return True, self.board[line[0]]
        if ' ' not in self.board:
            return True, 'D'
        return False, None

    def evaluate(self):
        is_over, winner = self.is_game_over()
        if not is_over:
            return 0
        return 10 if winner == 'X' else (-10 if winner == 'O' else 0)

    def get_successors(self, is_maximizing):
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

    def display_board(self):
        print("   0   1   2")
        for row in range(3):
            line = f"{row}  "
            for col in range(3):
                idx = row * 3 + col
                line += self.board[idx] + " | "
            print(line)
            if row < 2:
                print("  -----------")

    def display_move(self, move_str):
        move_idx = int(move_str.split('_')[1])
        print(f"   (fila {move_idx // 3}, columna {move_idx % 3})")


def eval_func(state):
    board = list(state['board'])
    game = SimpleTicTacToe(board, state['is_x_turn'])
    return game.evaluate()


def get_successors_func(state, is_maximizing):
    board = list(state['board'])
    game = SimpleTicTacToe(board, state['is_x_turn'])
    return game.get_successors(is_maximizing)


def ejemplo_minimax_simple():
    """Ejemplo 1: Minimax en una situación simple."""
    print("=" * 70)
    print("EJEMPLO 1: Minimax - X puede ganar en siguiente movimiento")
    print("=" * 70)

    board = ['X', 'X', ' ', 'O', 'O', ' ', ' ', ' ', ' ']
    game = SimpleTicTacToe(board)

    print("\nTablero actual:")
    game.display_board()

    print("\nAnalizando con Minimax (profundidad 2)...")
    state = game.get_state_dict()
    result = minimax_with_action(state, 2, True, eval_func, get_successors_func)

    print(f"\nResultado:")
    print(f"  Mejor movimiento: {result.best_action}")
    game.display_move(result.best_action)
    print(f"  Valor esperado: {result.best_value} (victoria)")
    print(f"  Nodos evaluados: {result.nodes_evaluated}")


def ejemplo_alfabeta_vs_minimax():
    """Ejemplo 2: Comparación Minimax vs Alfa-Beta."""
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Minimax vs Alfa-Beta - Eficiencia")
    print("=" * 70)

    # Tablero con múltiples opciones
    board = ['X', 'O', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
    game = SimpleTicTacToe(board)

    print("\nTablero actual:")
    game.display_board()

    state = game.get_state_dict()

    print("\nAnalizando con Minimax (profundidad 3)...")
    t0 = time.time()
    result_minimax = minimax_with_action(state, 3, True, eval_func, get_successors_func)
    time_minimax = time.time() - t0

    print(f"  Mejor movimiento: {result_minimax.best_action}")
    print(f"  Valor: {result_minimax.best_value}")
    print(f"  Nodos evaluados: {result_minimax.nodes_evaluated}")
    print(f"  Tiempo: {time_minimax:.4f}s")

    print("\nAnalizando con Alfa-Beta (profundidad 3)...")
    t0 = time.time()
    result_alfabeta = alfabeta_with_action(state, 3, True, eval_func, get_successors_func)
    time_alfabeta = time.time() - t0

    print(f"  Mejor movimiento: {result_alfabeta.best_action}")
    print(f"  Valor: {result_alfabeta.best_value}")
    print(f"  Nodos evaluados: {result_alfabeta.nodes_evaluated}")
    print(f"  Tiempo: {time_alfabeta:.4f}s")

    print(f"\n✨ MEJORA CON ALFA-BETA:")
    print(f"  Nodos ahorrados: {result_minimax.nodes_evaluated - result_alfabeta.nodes_evaluated}")
    reduction = (1 - result_alfabeta.nodes_evaluated / result_minimax.nodes_evaluated) * 100
    print(f"  Reducción: {reduction:.1f}%")


def ejemplo_alfabeta_profundidad():
    """Ejemplo 3: Alfa-Beta permite profundidad mayor."""
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Profundidad vs Eficiencia con Alfa-Beta")
    print("=" * 70)

    board = [' '] * 9
    game = SimpleTicTacToe(board)

    print("\nTablero vacío")

    state = game.get_state_dict()

    for depth in [2, 3, 4]:
        print(f"\nProfundidad {depth}:")

        print(f"  Minimax...", end=" ", flush=True)
        t0 = time.time()
        result_minimax = minimax_with_action(state, depth, True, eval_func, get_successors_func)
        time_m = time.time() - t0
        print(f"{result_minimax.nodes_evaluated} nodos, {time_m:.4f}s")

        print(f"  Alfa-Beta...", end=" ", flush=True)
        t0 = time.time()
        result_alfabeta = alfabeta_with_action(state, depth, True, eval_func, get_successors_func)
        time_a = time.time() - t0
        print(f"{result_alfabeta.nodes_evaluated} nodos, {time_a:.4f}s")

        ratio = result_minimax.nodes_evaluated / result_alfabeta.nodes_evaluated
        print(f"  Ratio: {ratio:.1f}×")


def ejemplo_defensa():
    """Ejemplo 4: Minimax elige defensa óptima."""
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Defensa Óptima - Evitar derrota")
    print("=" * 70)

    # O (adversario) puede ganar en siguiente turno
    # X debe bloquearlo
    board = ['O', 'O', ' ', 'X', 'X', ' ', ' ', ' ', ' ']
    game = SimpleTicTacToe(board)

    print("\nTablero actual (es turno de O):")
    game.display_board()

    print("\nO amenaza ganar en posición 2")
    print("Analizando con Minimax (profundidad 2)...")

    state = game.get_state_dict()
    result = minimax_with_action(state, 2, False, eval_func, get_successors_func)

    print(f"\nMejor movimiento de O: {result.best_action}")
    game.display_move(result.best_action)
    print(f"Valor: {result.best_value} (victoria para O)")
    print(f"Nodos evaluados: {result.nodes_evaluated}")

    # Ahora es turno de X defenderse
    board[2] = 'X'  # X bloquea
    game = SimpleTicTacToe(board)

    print("\n" + "-" * 70)
    print("X bloquea la amenaza")
    game.display_board()

    print("\nAhora turno de X nuevamente:")
    state = game.get_state_dict()
    result = minimax_with_action(state, 2, True, eval_func, get_successors_func)

    print(f"\nMejor movimiento de X: {result.best_action}")
    game.display_move(result.best_action)
    print(f"Valor: {result.best_value}")


def ejemplo_game_tree():
    """Ejemplo 5: Visualizar árbol de juego pequeño."""
    print("\n" + "=" * 70)
    print("EJEMPLO 5: Árbol de Juego Completo (posición simple)")
    print("=" * 70)

    board = ['X', ' ', ' ', 'O', ' ', ' ', ' ', ' ', ' ']
    game = SimpleTicTacToe(board)

    print("\nTablero inicial:")
    game.display_board()

    print("\nÁrbol de decisión (primeros 2 movimientos):")
    print("MAX (X) - profundidad 0")

    state = game.get_state_dict()
    successors = game.get_successors(is_maximizing=True)

    print(f"  {len(successors)} opciones posibles para X:")
    for i, (succ_state, action) in enumerate(successors[:3], 1):
        print(f"    {i}. {action}")
        succ_game = SimpleTicTacToe(list(succ_state['board']), False)
        min_successors = succ_game.get_successors(is_maximizing=False)
        print(f"       → MIN (O) tendría {len(min_successors)} opciones de respuesta")

    print(f"\n  Total: 3 + (3×{len(successors[0][0]['board'])//2}) = ~{3 + 3*4} nodos hasta profundidad 2")


if __name__ == "__main__":
    ejemplo_minimax_simple()
    ejemplo_alfabeta_vs_minimax()
    ejemplo_alfabeta_profundidad()
    ejemplo_defensa()
    ejemplo_game_tree()

    print("\n" + "=" * 70)
    print("✅ Todos los ejemplos completados")
    print("=" * 70)
