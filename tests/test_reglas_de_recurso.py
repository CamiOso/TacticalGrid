"""Tests de las reglas del recurso: recoger, transportar, soltar y ganar.

Estas reglas (`PICKUP_RESOURCE`, `DROP_RESOURCE` y el transporte implícito) no
estaban cubiertas por la suite. Los tests usan un escenario mínimo 3x3 sin muros
para poder colocar las unidades con total control y verificar cada regla.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game.state import GameState, Unit, Action


def _escenario_minimo():
    """Escenario 3x3 sin muros: base A en (0,0), base B en (2,2), recurso en (1,1)."""
    data = {
        "version": "1.0",
        "mapa": {"filas": 3, "columnas": 3},
        "tipos_terreno": {
            "camino": {"costo": 1, "transitable": True},
        },
        "terreno": [
            ["camino", "camino", "camino"],
            ["camino", "camino", "camino"],
            ["camino", "camino", "camino"],
        ],
        "bases": {"A": {"fila": 0, "columna": 0}, "B": {"fila": 2, "columna": 2}},
        "recurso": {"fila": 1, "columna": 1},
        "unidades": [
            {"id": "A1", "bando": "A", "tipo": "estandar", "fila": 0, "columna": 0},
            {"id": "B1", "bando": "B", "tipo": "estandar", "fila": 2, "columna": 2},
        ],
        "turno": "A",
        "juego": {"portador_recurso": None, "profundidad_maxima_minimax": 3},
        "prueba": {"modo": "partida"},
    }
    return data


def _estado(units=None, resource_pos=(1, 1), carrier=None, turn="A"):
    """Construye un GameState con unidades y posiciones configurables."""
    data = _escenario_minimo()
    if units is None:
        units = [
            Unit("A1", "A", 0, 0),
            Unit("B1", "B", 2, 2),
        ]
    return GameState(
        scenario_data=data,
        units=units,
        resource_pos=resource_pos,
        resource_carrier=carrier,
        current_turn=turn,
    )


class TestRecogerRecurso:
    """Regla 'recoger': pisar el recurso libre pasa a ser suyo."""

    def test_recoger_cuando_recurso_libre(self):
        """Si la unidad está en la celda del recurso libre, puede recogerlo."""
        # A1 en (1,1) que es donde está el recurso libre.
        a1 = Unit("A1", "A", 1, 1)
        b1 = Unit("B1", "B", 2, 2)
        st = _estado(units=[a1, b1], resource_pos=(1, 1), carrier=None, turn="A")

        assert Action.PICKUP_RESOURCE in st.get_valid_actions("A1")

        ok = st.apply_action("A1", Action.PICKUP_RESOURCE)
        assert ok
        assert st.resource_carrier == "A1"
        assert st.get_unit("A1").carries_resource is True

    def test_no_recoger_si_otro_lleva_el_recurso(self):
        """No se puede recoger si el recurso ya tiene portador."""
        a1 = Unit("A1", "A", 1, 1)
        b1 = Unit("B1", "B", 2, 2)
        st = _estado(units=[a1, b1], resource_pos=(1, 1), carrier="B1", turn="A")

        assert Action.PICKUP_RESOURCE not in st.get_valid_actions("A1")

    def test_no_recoger_si_no_esta_en_la_celda(self):
        """No se puede recoger desde una celda distinta a la del recurso."""
        a1 = Unit("A1", "A", 0, 0)
        b1 = Unit("B1", "B", 2, 2)
        st = _estado(units=[a1, b1], resource_pos=(1, 1), carrier=None, turn="A")

        assert Action.PICKUP_RESOURCE not in st.get_valid_actions("A1")


class TestTransporteDelRecurso:
    """Regla 'transporte': la posición del recurso sigue al portador."""

    def test_recurso_sigue_al_portador(self):
        """get_resource_position devuelve la celda del portador."""
        a1 = Unit("A1", "A", 1, 1, carries_resource=True)
        b1 = Unit("B1", "B", 2, 2)
        st = _estado(units=[a1, b1], resource_pos=(1, 1), carrier="A1", turn="A")

        assert st.get_resource_position() == (1, 1)

        # A1 se mueve a (0,1): el recurso viaja con él.
        ok = st.apply_action("A1", Action.MOVE_UP)
        assert ok
        assert st.get_resource_position() == (0, 1)


class TestSoltarRecurso:
    """Regla 'soltar': dejar el recurso en una celda."""

    def test_soltar_recurso(self):
        """El portador puede soltar el recurso y queda libre en esa celda."""
        a1 = Unit("A1", "A", 1, 1, carries_resource=True)
        b1 = Unit("B1", "B", 2, 2)
        st = _estado(units=[a1, b1], resource_pos=(1, 1), carrier="A1", turn="A")

        assert Action.DROP_RESOURCE in st.get_valid_actions("A1")

        ok = st.apply_action("A1", Action.DROP_RESOURCE)
        assert ok
        assert st.resource_carrier is None
        assert st.get_unit("A1").carries_resource is False
        assert st.resource_pos == (1, 1)


class TestVictoria:
    """Regla 'victoria': dejar el recurso en la base propia gana."""

    def test_ganar_al_llegar_a_base_propia(self):
        """Si el portador llega a su base y suelta, gana su bando."""
        # A1 lleva el recurso y está en su base (0,0).
        a1 = Unit("A1", "A", 0, 0, carries_resource=True)
        b1 = Unit("B1", "B", 2, 2)
        st = _estado(units=[a1, b1], resource_pos=(0, 0), carrier="A1", turn="A")

        assert st.get_winner() == "A"
        assert st.is_terminal() is True

    def test_no_gana_el_rival_por_estar_en_su_base(self):
        """El recurso en la base ajena no da la victoria al otro bando si el
        portador no es suyo."""
        # B1 (sin recurso) en su base (2,2); A1 lleva el recurso en (0,0).
        a1 = Unit("A1", "A", 0, 0, carries_resource=True)
        b1 = Unit("B1", "B", 2, 2)
        st = _estado(units=[a1, b1], resource_pos=(0, 0), carrier="A1", turn="A")

        assert st.get_winner() == "A"
        # B no gana solo por estar en su base sin portar el recurso.
        assert st.get_winner() != "B"


class TestSoloUnidadDelTurnoActua:
    """Regla de turno: solo el bando en turno puede actuar."""

    def test_unidad_fuera_de_turno_no_tiene_acciones(self):
        """La unidad del bando que no está en turno no tiene acciones."""
        a1 = Unit("A1", "A", 1, 1)
        b1 = Unit("B1", "B", 2, 2)
        st = _estado(units=[a1, b1], resource_pos=(1, 1), carrier=None, turn="A")

        # Es turno de A; B1 no puede actuar.
        assert st.get_valid_actions("B1") == []
