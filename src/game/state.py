"""Game state representation for TacticalGrid."""


class GameState:
    """Represents the current state of the TacticalGrid game."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.units = {}
        self.terrain = {}
        self.resource_position = None
        self.team_a_base = None
        self.team_b_base = None

    def __repr__(self):
        return f"GameState({self.width}x{self.height})"
