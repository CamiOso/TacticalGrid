"""Cargador de escenarios desde archivos JSON."""

import json
from pathlib import Path
from typing import Dict
from src.scenario.validator import ScenarioValidator


class ScenarioLoader:
    """Carga y valida escenarios desde archivos JSON."""

    @staticmethod
    def load(filepath: str | Path) -> Dict:
        """
        Carga un escenario desde archivo JSON y lo valida.

        Parámetros:
            filepath: Ruta del archivo JSON

        Retorna:
            Dict: Escenario validado

        Lanza:
            FileNotFoundError: Si el archivo no existe
            json.JSONDecodeError: Si el JSON es inválido
            ValueError: Si el escenario no pasa validación
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Archivo de escenario no encontrado: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                scenario = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"JSON inválido en {filepath}: {e.msg}",
                e.doc,
                e.pos
            )

        # Validar
        is_valid, errors = ScenarioValidator.validate_scenario(scenario)
        if not is_valid:
            error_msg = "Escenario inválido:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ValueError(error_msg)

        return scenario

    @staticmethod
    def load_all(directory: str | Path) -> Dict[str, Dict]:
        """
        Carga todos los escenarios JSON de un directorio.

        Parámetros:
            directory: Ruta del directorio con archivos .json

        Retorna:
            Dict[nombre -> escenario]: Diccionario de escenarios cargados
        """
        directory = Path(directory)
        scenarios = {}

        for json_file in directory.glob("*.json"):
            try:
                scenario = ScenarioLoader.load(json_file)
                scenarios[json_file.stem] = scenario
            except Exception as e:
                print(f"⚠ Error cargando {json_file.name}: {e}")

        return scenarios
