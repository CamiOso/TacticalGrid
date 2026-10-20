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

### **OPCIÓN 1: Ejecutar y ver TODO en consola (CON VISUALIZACIÓN ASCII)**

```bash
python start.py                                            # ejecuta todos los escenarios de scenarios/
python start.py scenarios/ejemplo_basico.json               # un escenario concreto
python start.py scenarios/terrenos_costosos.json --algoritmo A_ESTRELLA --heuristica distancia_bfs
python start.py scenarios/divergencia_bfs_ucs.json --algoritmo BEAM --k 4
python start.py scenarios/partida_simple.json --algoritmo ALFA_BETA --profundidad 2
python start.py scenarios/adversarial_simple.json --algoritmo MINIMAX --profundidad 3
```

**Qué hace:**
- ✅ Carga los escenarios JSON (todos o uno específico)
- ✅ **Visualiza cada mapa en ASCII** con terrenos, unidades, bases, recurso
- ✅ Ejecuta búsqueda (BFS, DFS, UCS, A*, Beam) o adversario (Minimax/alfa-beta) según el modo
- ✅ Muestra métricas: movimientos, costo, nodos generados/expandidos
- ✅ Verifica la solución de forma independiente
- ✅ Sin banderas, muestra un menú para elegir algoritmo/heurística/k (JSON como sugerencia)

**Modos:** el campo `prueba.modo` del escenario decide qué hace:

| Modo | Qué hace |
|------|----------|
| `busqueda` | Ejecuta BFS/DFS/UCS/A*/Beam sobre la unidad y objetivo de `prueba` y verifica la solución. |
| `partida` | Simula la partida por turnos entre dos bandos. |
| `adversarial` | Evalúa el estado actual y decide una acción con Minimax/alfa-beta. |

**Banderas de `start.py`:**

| Bandera | Valores | Aplica a |
|---------|---------|----------|
| `--algoritmo` | `BFS`, `DFS`, `UCS`, `A*`/`ASTAR`, `BEAM` | búsqueda |
| `--algoritmo` | `MINIMAX` (puro) o `ALFA_BETA` (con poda) | partida/adversarial |
| `--heuristica` | `manhattan`, `manhattan_pasos`, `distancia_bfs`, `zero` | A* y Beam |
| `--k` | entero ≥ 1 | Beam Search |
| `--profundidad` | entero ≥ 1 | partida/adversarial |
| `--no-preguntar` | — | usa la sugerencia del JSON sin menú |

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

### **OPCIÓN 1B: Usar agentes inteligentes integrados con JSON**

```bash
python scripts/search_with_agents.py
```

**Qué hace:**
- ✅ Carga escenarios JSON dinámicamente
- ✅ Crea **agentes inteligentes** (BFS, DFS, A*, Beam Search)
- ✅ Cada agente busca camino desde unidad inicial a objetivo
- ✅ **Visualización ASCII** automática de mapa y resultado
- ✅ Detalles de búsqueda: pasos, costo, nodos explorados

**Agentes disponibles:**
- `BFSAgent` - Búsqueda por amplitud
- `DFSAgent` - Búsqueda por profundidad  
- `SmartAgent` - Búsqueda A* (recomendado)
- `EfficientAgent` - Beam Search con k variable

---

### **OPCIÓN 2: Generar visualizaciones HTML (interactivo)**

```bash
python scripts/visualize_search.py
```

**Qué genera:**
- ✅ Archivos HTML con visualizaciones del mapa
- ✅ Ver terrenos en colores
- ✅ Ver unidades, bases, recurso
- ✅ Ver camino encontrado (línea roja)

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
- ✅ Pruebas de escenarios JSON (validación)
- ✅ Pruebas de búsqueda (BFS, DFS, UCS, A*, Beam Search)
- ✅ Pruebas de heurísticas (incluida `distancia_bfs`)
- ✅ Pruebas de estado del juego
- ✅ Pruebas de funciones de utilidad
- ✅ Pruebas de adversarios (Minimax, Alfa-Beta)
- ✅ Pruebas de verificación de soluciones
- ✅ Pruebas de los 10 casos mínimos del enunciado
- ✅ Pruebas de adaptación a cambios de escenario

---

### **OPCIÓN 4: Ejecutar ejemplos específicos**

```bash
python scripts/casos_minimos.py           # Demuestra los 10 casos mínimos del enunciado
python scripts/examples_search.py          # Ver cómo trabajan BFS/DFS/UCS/A*
python scripts/examples_adversarial.py     # Ver Minimax y Alfa-Beta
python scripts/examples_agents.py          # Ver agentes inteligentes
```

---

## 📁 Estructura del Proyecto

```
Proyecto/
├── start.py                        # ⭐ Punto de entrada único (modos busqueda/partida/adversarial)
├── src/
│   ├── algorithms/
│   │   ├── search.py               # BFS, DFS, UCS, A*, Beam Search
│   │   ├── adversarial.py          # Minimax, Alfa-Beta
│   │   └── heuristics.py           # Manhattan, ponderada, distancia_bfs, zero
│   ├── scenario/
│   │   ├── schema.py               # Definiciones TypedDict
│   │   ├── validator.py            # Valida escenarios JSON
│   │   ├── loader.py               # Carga archivos JSON
│   │   └── scenario.py             # Acceso a datos del escenario
│   ├── game/
│   │   ├── state.py                # GameState (unidades, acciones, estado)
│   │   └── utility.py              # Funciones de evaluación Minimax
│   ├── application/
│   │   ├── test_executor.py        # Ejecuta búsqueda/adversarial desde JSON
│   │   ├── solution_verifier.py    # Verifica soluciones válidas
│   │   ├── visualizer.py           # Genera HTML+Canvas
│   │   └── ascii_visualizer.py     # ⭐ Visualización ASCII robusta
│   └── agents/
│       ├── unit.py                 # UnitBFS, UnitDFS
│       ├── smart_unit.py           # SmartUnit (A*)
│       ├── tactical_unit.py        # TacticalUnit (Minimax)
│       └── scenario_agents.py      # ⭐ Agentes integrados con JSON
├── scenarios/
│   ├── ejemplo_basico.json         # Mapa 4×4
│   ├── terrenos_costosos.json      # Mapa 5×5 con costos variables
│   ├── divergencia_bfs_ucs.json    # Caso de estudio: BFS vs UCS
│   ├── partida_simple.json         # Partida 1 vs 1
│   └── adversarial_simple.json     # Decisión adversarial
├── scripts/                        # Scripts auxiliares y demos
│   ├── casos_minimos.py            # 10 casos mínimos del enunciado
│   ├── examples_search.py          # Ejemplos de búsqueda
│   ├── examples_adversarial.py     # Ejemplos de Minimax/Alfa-Beta
│   ├── examples_agents.py          # Ejemplos de agentes
│   ├── examples_with_scenarios.py  # Ejemplos con escenarios JSON
│   ├── visualize_search.py         # Visualizaciones HTML
│   ├── interactive.py              # Modo interactivo guiado
│   └── experimentos_beam_search.py # Experimento Beam Search (k=1,2,4,8)
├── tests/
│   ├── test_scenario.py            # Validación de escenarios
│   ├── test_search.py              # BFS, DFS, UCS, A*
│   ├── test_beam_search.py         # Beam Search
│   ├── test_adversarial.py         # Minimax y Alfa-Beta
│   ├── test_casos_minimos.py       # ⭐ Los 10 casos mínimos como asserts
│   ├── test_heuristica_bfs.py      # ⭐ Heurística distancia_bfs
│   └── ...                         # game_state, utility, verifier, adaptación
├── DOCUMENTO_TECNICO_COMPLETO.md   # Documentación técnica (61KB)
├── DOCUMENTO_TECNICO_COMPLETO.html # Versión HTML para PDF
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
| **Alfa-Beta** | Adversarial | ✅ | Media | Poda (misma decisión, menos nodos) |

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

## 📚 Documentos

- `DOCUMENTO_TECNICO_COMPLETO.md` — documentación técnica (modelado, algoritmos, experimentos, uso de IA).
- `MANUAL_USUARIO.md` — manual de usuario con instrucciones de instalación y ejecución.
- `README.md` — este archivo.

## 👨‍💻 Autor

**Cristian Camilo Osorio Granada**  
Estudiante de Ingeniería en Sistemas Computacionales  
Universidad de Caldas  
Sistemas Inteligentes I - 2024

**Correo:** cristian.1701421857@ucaldas.edu.co
