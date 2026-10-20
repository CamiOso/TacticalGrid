#!/usr/bin/env python3
"""
Búsqueda de caminos usando agentes integrados con escenarios JSON.

Demuestra cómo usar los agentes que cargan escenarios JSON dinámicamente
y ejecutan búsqueda en contexto real.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.scenario_agents import BFSAgent, DFSAgent, SmartAgent, EfficientAgent


def main():
    """Ejecuta búsquedas con agentes en escenarios disponibles."""
    scenarios_dir = Path(__file__).parent.parent / "scenarios"
    scenario_files = sorted(scenarios_dir.glob("*.json"))

    if not scenario_files:
        print("❌ No se encontraron escenarios")
        return

    print("\n" + "=" * 80)
    print("🤖 BÚSQUEDA CON AGENTES INTEGRADOS")
    print("=" * 80)

    for scenario_file in scenario_files:
        print(f"\n{'=' * 80}")
        print(f"📍 Escenario: {scenario_file.name}")
        print(f"{'=' * 80}")

        try:
            # Crear agentes para este escenario
            smart_agent = SmartAgent(scenario_file)

            # Mostrar información
            smart_agent.print_info()

            # Visualizar mapa
            print("🗺️  MAPA:")
            smart_agent.visualize_map()

            # Ejecutar búsqueda con A*
            goal = smart_agent.scenario.test_objective
            unit_id = smart_agent.scenario.units[0]['id']

            print(f"\n🔍 Búsqueda: {unit_id} → {goal}\n")
            smart_agent.move_to_goal(unit_id, tuple(goal.values()) if isinstance(goal, dict) else goal)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ Búsqueda con agentes completada")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
