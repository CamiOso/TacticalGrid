"""Esquema y estructura del formato JSON de escenarios."""

from typing import TypedDict, List, Dict, Any


class TerrainType(TypedDict):
    """Definición de un tipo de terreno."""
    costo: int
    transitable: bool


class Position(TypedDict):
    """Posición en el mapa (fila, columna)."""
    fila: int
    columna: int


class Unit(TypedDict):
    """Definición de una unidad."""
    id: str
    bando: str
    tipo: str
    fila: int
    columna: int


class BasePosition(TypedDict):
    """Posición de base de un bando."""
    fila: int
    columna: int


class GameConfig(TypedDict):
    """Configuración del juego."""
    portador_recurso: str | None
    profundidad_maxima_minimax: int


class TestMode(TypedDict):
    """Configuración de prueba."""
    modo: str
    unidad_inicio: str | None
    objetivo: Position


class MapConfig(TypedDict):
    """Configuración del mapa."""
    filas: int
    columnas: int


class ScenarioJSON(TypedDict):
    """Estructura completa del escenario JSON."""
    version: str
    mapa: MapConfig
    tipos_terreno: Dict[str, TerrainType]
    terreno: List[List[str]]
    bases: Dict[str, BasePosition]
    recurso: Position
    unidades: List[Unit]
    turno: str
    juego: GameConfig
    prueba: TestMode
