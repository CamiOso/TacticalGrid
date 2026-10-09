# TacticalGrid

Sistema inteligente de búsqueda y decisión adversarial para un juego táctico 2D basado en escenarios JSON.

## 🎮 ¿Qué hace el proyecto?

El proyecto ejecuta **algoritmos de inteligencia artificial** en mapas tácticos 2D:

1. **Carga escenarios JSON** con mapas, unidades, bases, terrenos y recursos
2. **Ejecuta algoritmos de búsqueda** para encontrar el camino óptimo:
   - BFS, DFS, UCS, A*, Beam Search
3. **Verifica que las soluciones sean válidas** (camino conectado, costo correcto)
4. **Genera visualizaciones HTML** del mapa y soluciones encontradas
5. **Analiza resultados** mostrando diferencias entre algoritmos

---

## 🚀 Cómo ejecutar TODO el proyecto (línea por línea)

### **OPCIÓN 1: Ejecutar y ver TODO en consola**

```bash
python run_tests.py
```

**Qué hace:**
- ✅ Carga los 3 escenarios JSON automáticamente
- ✅ Ejecuta BFS, DFS, UCS, A* en cada uno
- ✅ Muestra resultados en tabla: movimientos, costo, nodos explorados
- ✅ Compara algoritmos (ej: "UCS 50% más barato que BFS")
- ✅ TODO en la pantalla, sin archivos adicionales

**Output típico:**
```
=================================================================================
EXECUTOR DE PRUEBAS - TacticalGrid
=================================================================================

📁 Encontrados 3 escenario(s)

=============================== 
Ejecutando: divergencia_bfs_ucs.json
===============================

✅ Escenario cargado:
   Mapa: 3×5
   Unidades: 2
   Modo de prueba: busqueda

Algoritmo        Éxito    Movimientos  Costo         Explorados
---------------------------------------------------------------------------
BFS              ✅       4            16/16         12
DFS              ✅       4            16/16         6
UCS              ✅       8            8             8
A*               ✅       8            8             7

📊 Análisis Comparativo:
  💰 UCS encontró ruta más barata:
     BFS: 16 vs UCS: 8 (50.0% más barata)

  🎯 A* es más eficiente que UCS:
     UCS exploró: 8 nodos
     A* exploró: 7 nodos (87.5%)
```

---

### **OPCIÓN 2: Generar visualizaciones HTML (interactivo)**

```bash
python visualize_search.py
```

**Qué genera:**
- ✅ Archivos HTML con visualizaciones del mapa
- ✅ Ver terrenos en colores
- ✅ Ver unidades, bases, recurso
- ✅ Ver camino encontrado (línea roja)

**Archivos generados:**
```
visualizacion_divergencia_bfs_ucs_bfs.html
visualizacion_divergencia_bfs_ucs_ucs.html
visualizacion_divergencia_bfs_ucs_a_star.html
```

**Cómo verlos:**
1. Los archivos se guardan en el directorio raíz
2. Abre uno en Chrome/Firefox/Edge: `Ctrl+O` y selecciona el archivo
3. Ves el mapa interactivo con la solución

---

### **OPCIÓN 3: Ejecutar todos los tests**

```bash
python -m pytest tests/ -v
```

**Qué verifica:**
- ✅ 13 tests de escenarios JSON (validación)
- ✅ 15 tests de búsqueda (BFS, DFS, UCS, A*, Beam Search)
- ✅ 9 tests de estado del juego
- ✅ 8 tests de funciones de utilidad
- ✅ 11 tests de verificación de soluciones

**Output:**
```
tests/test_scenario.py::test_validator_complete_scenario PASSED
tests/test_search.py::test_bfs_simple_path PASSED
tests/test_search.py::test_beam_search_k_variations PASSED
... (57 tests total)
```

---

### **OPCIÓN 4: Ejecutar ejemplos específicos**

```bash
python examples_search.py          # Ver cómo trabajan BFS/DFS/UCS/A*
python examples_adversarial.py     # Ver Minimax y Alfa-Beta
python examples_agents.py          # Ver agentes inteligentes
```

---

## 📁 Estructura del Proyecto

```
Proyecto/
├── src/
│   ├── algorithms/
│   │   ├── search.py              # BFS, DFS, UCS, A*, Beam Search
│   │   ├── adversarial.py         # Minimax, Alfa-Beta
│   │   └── heuristics.py          # Manhattan, Euclidean, Chebyshev
│   ├── scenario/
│   │   ├── schema.py              # Definiciones TypedDict
│   │   ├── validator.py           # Valida escenarios JSON (13 tests)
│   │   ├── loader.py              # Carga archivos JSON
│   │   └── scenario.py            # Acceso a datos del escenario
│   ├── game/
│   │   ├── state.py               # GameState (unidades, acciones, estado)
│   │   └── utility.py             # Funciones de evaluación Minimax
│   ├── application/
│   │   ├── test_executor.py       # Ejecuta búsqueda desde JSON
│   │   ├── solution_verifier.py   # Verifica soluciones válidas
│   │   └── visualizer.py          # Genera HTML+Canvas
│   └── agents/
│       ├── unit.py                # UnitBFS, UnitDFS
│       ├── smart_unit.py          # SmartUnit (A*)
│       └── tactical_unit.py       # TacticalUnit (Minimax)
├── tests/
│   ├── test_scenario.py           # 13 tests
│   ├── test_search.py             # 15 tests
│   ├── test_game_state.py         # 9 tests
│   ├── test_utility.py            # 8 tests
│   ├── test_beam_search.py        # 7 tests
│   └── test_solution_verifier.py  # 11 tests
├── scenarios/
│   ├── ejemplo_basico.json        # Mapa 4×4
│   ├── terrenos_costosos.json     # Mapa 5×5 con costos variables
│   └── divergencia_bfs_ucs.json   # Caso de estudio: BFS vs UCS
├── run_tests.py                   # Ejecuta TODO de forma simple
├── visualize_search.py            # Genera visualizaciones HTML
├── examples_search.py             # Ejemplos de búsqueda
├── examples_adversarial.py        # Ejemplos de Minimax/Alfa-Beta
├── examples_agents.py             # Ejemplos de agentes
└── README.md
```

---

## 📊 Algoritmos Implementados

| Algoritmo | Tipo | Óptimo | Memoria | Uso |
|-----------|------|--------|---------|-----|
| **BFS** | No informada | ✅ | ❌ Alto | Camino más corto |
| **DFS** | No informada | ❌ | ✅ Bajo | Exploración profunda |
| **UCS** | Informada | ✅ | Media | Costo mínimo |
| **A\*** | Informada | ✅* | Media | Heurística guiada |
| **Beam Search** | Informada | ❌ | ✅ Bajo | Memoria limitada |
| **Minimax** | Adversarial | ✅ | ❌ Alto | Decisión óptima |
| **Alfa-Beta** | Adversarial | ✅ | Media | Poda (17.5× más rápido) |

---

## 📈 Ejemplo: Caso de estudio BFS vs UCS

**Escenario:** `divergencia_bfs_ucs.json` (mapa 3×5)

```
BFS (minimiza pasos):
  - Movimientos: 4
  - Costo real: 16 ❌ (MÁS CARO)
  
UCS (minimiza costo):
  - Movimientos: 8  
  - Costo: 8 ✅ (MÁS BARATO - 50% menos)
```

**Conclusión:** BFS eligió ruta corta pero cara. UCS eligió ruta larga pero barata.

---

## ✅ Lo que el proyecto VERIFICA

1. **Validación de escenarios JSON**
   - Mapa tiene dimensiones válidas
   - Todos los terrenos están definidos
   - Unidades, bases, recurso están dentro del mapa
   - Recurso inicial tiene portador válido

2. **Verificación de soluciones**
   - Camino es conexo (cada paso es vecino del anterior)
   - No cruza muros u obstáculos
   - Costo reportado = suma real de transiciones
   - Objetivo se alcanza

3. **Análisis de algoritmos**
   - Compara costos entre BFS/UCS/A*
   - Cuenta nodos explorados
   - Mide eficiencia de cada uno

---

## 🔧 Requisitos

- Python 3.8+
- Sin dependencias externas (solo librería estándar)

---

## 👨‍💻 Autores

Cristian Camilo Osorio Granada  
Sistemas Inteligentes I - UCALDAS
