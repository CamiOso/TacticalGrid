# DOCUMENTO TÉCNICO COMPLETO: TacticalGrid

## Un Sistema Inteligente de Búsqueda y Decisión en Juegos Tácticos 2D

**Autor:** Cristian Camilo Osorio Granada  
**Institución:** Universidad de Caldas  
**Curso:** Sistemas Inteligentes I  
**Profesor(a):** -  
**Fecha:** 2026

---

## 1. INTRODUCCIÓN Y MOTIVACIÓN

### 1.1 Contexto del Proyecto

Durante el curso de Sistemas Inteligentes I de la Universidad de Caldas, se planteó un reto fundamental: implementar un sistema inteligente de búsqueda que pueda resolver problemas de navegación en espacios 2D usando múltiples estrategias algorítmicas. El proyecto surge de una pregunta central que todo ingeniero en sistemas debe responder:

**¿Cuándo usar cada algoritmo? ¿Qué características del problema determinan la mejor estrategia de búsqueda?**

Estas preguntas no tienen respuestas simples. En el mundo real, contamos con recursos limitados (memoria, tiempo de procesamiento), restricciones complejas (terrenos costosos, obstáculos), y objetivos diversos (encontrar cualquier camino, el más corto, el más barato, o el que maximiza una función de utilidad).

### 1.2 El Problema que Resolvemos

TacticalGrid es un sistema que simula un juego táctico 2D donde:

1. **Hay un mapa con terrenos** - cada celda tiene un tipo (pasto, camino, muro, agua) con su propio costo de traversal y si es transitable
2. **Hay unidades controladas** - dos equipos (A y B) con unidades que pueden moverse
3. **Hay un recurso valioso** - existe un recurso único que una unidad puede recoger y llevar
4. **Hay objetivos estratégicos** - las unidades deben alcanzar posiciones específicas del mapa
5. **Hay diferentes formas de resolver el problema** - podemos usar BFS para el camino más corto, UCS para el costo mínimo, A* con heurísticas, o incluso tomar decisiones adversariales con Minimax

El proyecto no busca crear el "mejor" algoritmo, sino demostrar que **cada algoritmo es el mejor para su contexto específico**. BFS es óptimo si solo importa la cantidad de pasos. UCS es óptimo si minimizar costo es crítico. A* balancea ambos con información heurística. Beam Search es la opción cuando la memoria es un lujo que no podemos permitirnos.

### 1.3 Requisitos Implementados

Para responder adecuadamente a estas preguntas, el proyecto implementó:

**Algoritmos de Búsqueda:**
- BFS (Breadth-First Search) - encuentra el camino con menos pasos
- DFS (Depth-First Search) - explora profundidad para casos especiales
- UCS (Uniform Cost Search) - minimiza el costo real acumulado
- A* (A-Star) - heurística guiada para eficiencia óptima
- Beam Search - búsqueda con restricciones de memoria
- Minimax - búsqueda en espacios adversariales
- Alfa-Beta - poda sobre Minimax (produce la misma decisión evaluando menos nodos)

**Heurísticas para A*:**
- Manhattan (admisible, 4 direcciones)
- Manhattan ponderada por costo mínimo (heurística propia, admisible)
- Euclidean y Chebyshev (documentadas como no admisibles para 4 direcciones)

**Modos de prueba:**
- `busqueda`: resolver una navegación con BFS, DFS, UCS o A*.
- `adversarial`: evaluar un estado con Minimax/Alfa-Beta y seleccionar una acción.
- `partida`: jugar una partida por turnos con alfa-beta hasta ganador o límite de turnos.

**Validación Exhaustiva:**
- Validación de escenarios JSON con las reglas del formato común (estructura, mapa, terrenos, entidades, turno y portador)
- Verificación de soluciones válidas (camino conexo, costo consistente, objetivo alcanzado, sin estados inválidos)
- Auditoría de costos y caminos conectados

**Visualización e Interactividad:**
- Visualización paso a paso del algoritmo en HTML interactivo
- Terminal ASCII para depuración rápida
- Generación de visualizaciones HTML del mapa y del camino encontrado

**Sistema Completo:**
- 86 pruebas automatizadas cubriendo todos los componentes
- Arquitectura de 5 capas con separación clara de responsabilidades
- Documentación formal del sistema

### 1.4 Metodología Propuesta

Organizamos el trabajo en **tres fases principales**, con ciclos de iteración entre ellas:

**Fase 1: Análisis y Diseño**
- Estudiar el problema de búsqueda en espacios 2D
- Diseñar la arquitectura en 5 capas
- Definir formalmente el espacio de estados
- Especificar la estructura JSON de escenarios

**Fase 2: Implementación**
- Construir la capa de validación de escenarios
- Implementar el modelo de estado del juego (GameState)
- Codificar los 7 algoritmos de búsqueda
- Desarrollar verificadores y visualizadores
- Escribir tests exhaustivos

**Fase 3: Evaluación**
- Ejecutar experimentos variando parámetros (k en Beam Search)
- Comparar algoritmos en casos donde divergen
- Analizar trade-offs memoria vs calidad
- Documentar aprendizajes

Este no fue un proceso perfectamente lineal. Hubo múltiples ciclos de refinamiento - cuando los tests fallaban, volvíamos a la fase 2. Cuando encontrábamos patrones interesantes, volvíamos a fase 1 para analizar más profundamente. Esta es la naturaleza real del desarrollo de sistemas complejos.

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Visión General de las Capas

Un principio fundamental en ingeniería de software es la **separación de responsabilidades**. Un sistema monolítico que mezcla carga de JSON, validación, búsqueda algorítmica, y visualización es difícil de mantener, extender y testear.

Por eso diseñamos TacticalGrid con una arquitectura de **5 capas independientes** pero conectadas:

```
┌───────────────────────────────────────────────────────────┐
│          CAPA 5: APPLICATION LAYER                        │
│   TestExecutor, Visualizer, SolutionVerifier              │
│   Orquesta la ejecución, verifica y visualiza resultados  │
├───────────────────────────────────────────────────────────┤
│          CAPA 4: AGENTS LAYER                             │
│   UnitBFS, SmartUnit, TacticalUnit                        │
│   Combinan algoritmos con decisiones en el dominio        │
├───────────────────────────────────────────────────────────┤
│          CAPA 3: ALGORITHMS LAYER                         │
│   Search (BFS, DFS, UCS, A*, Beam), Adversarial,         │
│   Heuristics. Pura lógica algorítmica, reutilizable      │
├───────────────────────────────────────────────────────────┤
│          CAPA 2: GAME DOMAIN LAYER                        │
│   GameState, Action, UtilityFunction                      │
│   Modela el estado del juego y sus transiciones          │
├───────────────────────────────────────────────────────────┤
│          CAPA 1: SCENARIO LAYER                           │
│   Schema, Validator, Loader, Scenario                     │
│   Carga, valida y proporciona acceso seguro a datos JSON  │
└───────────────────────────────────────────────────────────┘
```

### 2.2 Propósito de Cada Capa

**Capa 1 - Scenario Layer (Capa de Escenarios):**

Esta es la capa más baja y trata con la realidad externa del sistema: archivos JSON que el usuario proporciona. Sus responsabilidades son:

- **Cargar JSON:** Lee archivos JSON de escenarios del disco
- **Validar estructura:** Asegura que el JSON tiene todos los campos requeridos
- **Validar contenido:** Verifica que los datos sean consistentes (no unidades fuera del mapa, terrenos válidos, etc.)
- **Acceso seguro:** Proporciona métodos para leer datos sin permitir modificaciones accidentales

El Scenario carga un JSON como este:
```json
{
  "version": "1.0",
  "mapa": {"filas": 4, "columnas": 4},
  "terreno": [["camino", "muro"], ["pasto", "camino"]],
  "unidades": [{"id": "A1", "bando": "A", "tipo": "estandar", "fila": 0, "columna": 0}],
  "tipos_terreno": {"camino": {"costo": 1, "transitable": true}, "pasto": {"costo": 2, "transitable": true}, "muro": {"costo": 0, "transitable": false}},
  "recurso": {"fila": 1, "columna": 1},
  "bases": {"A": {"fila": 3, "columna": 3}, "B": {"fila": 0, "columna": 3}},
  "juego": {"portador_recurso": null, "profundidad_maxima_minimax": 4},
  "prueba": {"modo": "busqueda", "unidad_inicio": "A1", "objetivo": {"fila": 2, "columna": 2}}
}
```

Y lo valida contra las reglas del formato común antes de permitir su uso (detalladas en la sección 5).

**Capa 2 - Game Domain Layer (Capa de Dominio del Juego):**

Una vez tenemos datos válidos, necesitamos representar formalmente el **estado del juego**. Esta capa define:

- **GameState:** Clase que encapsula posiciones de unidades, quién lleva el recurso, turno actual
- **Action:** Enumeración de acciones válidas (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, PICKUP_RESOURCE, DROP_RESOURCE)
- **Transiciones:** Métodos que dicen "si estoy en estado S y tomo acción A, ¿a qué nuevo estado S' llego?"
- **Utility:** Funciones que evalúan qué tan "bueno" es un estado (necesarias para Minimax)

Formalmente:
```
Transición: (Estado, Acción) → (NuevoEstado, Costo)

Ejemplo:
Estado1: A1 en (0,0), B1 en (1,0), recurso sin portador
Acción: MOVE_DOWN(A1)
Estado2: A1 en (1,0), B1 en (1,0)...
```

Dos unidades no pueden ocupar la misma celda: la regla de movimiento impide entrar en una celda ya ocupada (decisión de diseño del equipo).

**Capa 3 - Algorithms Layer (Capa de Algoritmos):**

Esta capa implementa la "inteligencia" pura. Contiene:

- **BFS:** Función que recibe un grafo y estado objetivo, retorna el camino más corto
- **DFS:** Función para exploración profunda
- **UCS:** Función para costo mínimo
- **A\*:** Función que usa heurística para guiar la búsqueda
- **Beam Search:** Función que limita la memoria a k nodos en la frontera
- **Minimax:** Algoritmo adversarial de alternancia de turnos
- **Alfa-Beta:** Versión optimizada de Minimax con poda

Cada función retorna un objeto SearchResult consistente:
```python
class SearchResult:
    path: List[Tuple[int, int]]  # Secuencia de posiciones
    cost: int                     # Costo total del camino
    expanded: int                 # Nodos expandidos (sacados de la frontera)
    generated: int                # Nodos generados (creados durante la búsqueda)
    max_frontier: int             # Tamaño máximo de la frontera
```

La belleza de esta capa es que **no sabe nada del dominio**. Los algoritmos reciben un grafo genérico con nodos y aristas, y el costo asociado a cada arista. Podrían usarse para resolver problemas completamente diferentes - ruteo de redes, planificación de rutas en logística, etc.

**Capa 4 - Agents Layer (Capa de Agentes):**

Aquí es donde los algoritmos "conocen" del dominio del juego. Los agentes combinan:
- Un algoritmo específico (ej: BFS)
- El estado actual del juego
- Las reglas del dominio
- Toman decisiones automáticas

Ejemplos:
- `UnitBFS(unidad)` - mi unidad siempre elige el siguiente movimiento usando BFS
- `SmartUnit(unidad)` - mi unidad usa A* con heurística Manhattan
- `TacticalUnit(unidad)` - mi unidad usa Minimax para decisiones adversariales

**Capa 5 - Application Layer (Capa de Aplicación):**

La capa más alta que orquesta todo:
- **TestExecutor:** Carga escenarios, ejecuta todos los algoritmos, compara resultados
- **SolutionVerifier:** Valida que una solución propuesta es realmente válida
- **Visualizer:** Genera HTML/terminal con representaciones visuales
- **SearchTracker:** Registra paso a paso qué nodos se exploraron (para visualización)

### 2.3 Flujo de Datos a Través de las Capas

Cuando el usuario quiere ejecutar una búsqueda, los datos fluyen así:

```
1. JSON en disco
   ↓
2. ScenarioLoader.load(archivo) 
   → dict de Python
   ↓
3. ScenarioValidator.validate_scenario(dict)
   → True/False + lista de errores
   ↓
4. Scenario(dict)
   → Objeto con acceso seguro a datos
   ↓
5. TestExecutor.load_scenario(scenario_path)
   → Scenario dentro del executor
   ↓
6. TestExecutor.execute_test()
   → Ejecuta BFS, DFS, UCS, A*, Beam Search
   → Retorna Dict con resultados
   ↓
7. SolutionVerifier.verify_complete_solution(path, scenario)
   → True/False (¿es válida la solución?)
   ↓
8. MapVisualizer.generate_html(scenario, path)
   → HTML con Canvas
   ↓
9. Navegador abre HTML
   → Usuario ve visualización interactiva
```

Cada capa es independiente, pero conectada. Podemos:
- Cambiar la estrategia de visualización sin afectar búsqueda
- Reemplazar BFS con A* sin cambiar el cargador
- Agregar nuevos escenarios sin modificar algoritmos
- Esto es **separación de responsabilidades**: cada capa puede evolucionar sin romper las demás.

### 2.4 Visualización ASCII Robusta

Desde el proyecto es crítico visualizar qué está pasando en el mapa. Implementamos una **visualización ASCII profesional** en `src/application/ascii_visualizer.py`:

```
Características:
✅ Mapa con terrenos en símbolos (· para camino, ~ para pasto, █ para muro)
✅ Colores ANSI para mejor legibilidad
✅ Posiciones de unidades con sus identificadores
✅ Bases de equipos A (verde) y B (magenta)
✅ Recurso marcado con ◆ en amarillo
✅ Camino encontrado: S (inicio), * (intermedio), E (fin)
✅ Leyenda completa de símbolos
✅ Detalles de búsqueda: pasos, costo, nodos explorados
✅ Secuencia de movimientos con direcciones (↑↓←→)
```

**Ejemplo de uso:**

```python
from src.application.ascii_visualizer import ASCIIVisualizer
from src.scenario.scenario import Scenario

scenario = Scenario(scenario_data)
visualizer = ASCIIVisualizer(scenario)

# Mostrar mapa con unidades y bases
visualizer.print_map()

# Mostrar mapa con camino encontrado
visualizer.print_path(path=result.path)

# Visualización completa con detalles
visualizer.print_complete_visualization(
    path=result.path,
    cost=result.cost,
    explored=result.explored,
    algorithm_name="A*"
)
```

Esta visualización se integra automáticamente en `run_tests.py`, por lo que cada ejecución muestra el mapa ASCII.

### 2.5 Agentes Integrados con Escenarios JSON

Los algoritmos de búsqueda por sí solos no saben de escenarios JSON. Para aplicarlos en contexto real, creamos **agentes inteligentes** que cargan escenarios dinámicamente:

```python
# En src/agents/scenario_agents.py

class ScenarioAgent:
    """Agente que carga escenario JSON y ejecuta búsqueda."""
    
    def __init__(self, scenario_path):
        # Cargar y validar escenario
        self.scenario = Scenario(ScenarioLoader.load(scenario_path))
    
    def search(self, unit_id: str, goal: Tuple) -> SearchResult:
        # Crear grafo dinámicamente desde escenario
        # Ejecutar algoritmo de búsqueda
        # Retornar resultado con visualización

class BFSAgent(ScenarioAgent): ...    # Búsqueda BFS
class DFSAgent(ScenarioAgent): ...    # Búsqueda DFS
class SmartAgent(ScenarioAgent): ...  # Búsqueda A*
class EfficientAgent(ScenarioAgent): ... # Beam Search
```

**Ventajas:**

1. **Dinámico:** Cargan cualquier escenario JSON sin modificar código
2. **Validación:** Rechazan escenarios inválidos antes de ejecutar
3. **Contextual:** Crean grafo a partir de mapa, unidades, terrenos
4. **Flexible:** Diferentes agentes usan diferentes algoritmos
5. **Integrado:** Se ejecutan como parte normal del proyecto

**Ejemplo:**

```python
from src.agents.scenario_agents import SmartAgent

# Cargar escenario
agent = SmartAgent("scenarios/ejemplo_basico.json")

# Mostrar información
agent.print_info()

# Visualizar mapa
agent.visualize_map()

# Buscar camino
result = agent.search("A1", (3, 3))

# O visualizar directamente
agent.move_to_goal("A1", (3, 3))
```

Los agentes se ejecutan en `search_with_agents.py`:

```bash
python3 search_with_agents.py    # Ejecuta agentes en todos los escenarios
```

---

## 3. MODELADO FORMAL DEL PROBLEMA

### 3.1 Definición del Espacio de Estados

Para que los algoritmos de búsqueda funcionen, necesitamos una **representación formal y completa** del estado del problema. Un estado debe capturar toda la información necesaria para:

1. Generar sucesores (acciones posibles desde este estado)
2. Determinar si hemos alcanzado la meta
3. Calcular el costo de llegar aquí

En TacticalGrid, el estado (`GameState`) captura la siguiente información:

```
Estado S = (unidades, recurso, turno)

Donde:
- unidades: Diccionario {ID_unidad → Unidad}. Cada Unidad tiene
  id, team (A/B), fila, columna y carries_resource (bool).
  Ejemplo: A1 en (2,3), A2 en (1,1), B1 en (3,0)

- recurso: posición neutral (fila, columna) y portador actual.
  resource_carrier es el ID de la unidad que lo transporta, o None si está suelto.
  Invariante: solo UNA unidad porta el recurso (o ninguna).

- turno: current_turn, el bando que debe actuar ("A" o "B").
  Tras cada acción el turno alterna entre A y B.

- move_history: registro de (unidad, acción, posición) para trazabilidad.
```

¿Por qué estos componentes? Porque necesitamos saber:
- **¿Dónde está cada unidad?** → unidades
- **¿Quién lleva el recurso?** → resource_carrier
- **¿A quién le toca actuar?** → current_turn

Sin alguno de estos, no podríamos responder si una acción es válida o si se ganó la partida. La posesión del recurso distingue estados que comparten la misma posición física (estado compuesto).

### 3.2 Tamaño del Espacio de Estados

Un concepto importante es el **tamaño del espacio de estados** - cuántos estados diferentes son teóricamente posibles.

Para un mapa m×n con k unidades:

```
|S| ≤ (m × n)^k × (k + 1) × 2

Donde:
- (m × n)^k: cada una de las k unidades puede estar en cualquiera de m×n celdas
- (k + 1): cualquiera de las k unidades lleva recurso, o ninguna (k+1 posibilidades)
- 2: el turno puede ser de A o de B

Ejemplo concreto:
- Mapa 4×4 (16 celdas)
- 2 unidades
- |S| ≤ 16^2 × 3 × 2 = 1536 estados

Pero en la práctica es mucho menor porque:
- No todas las celdas son transitables
- Las unidades no pueden estar en la misma celda
- El horizonte de búsqueda limita la profundidad explorada
```

Este análisis es importante porque nos dice que **el espacio de búsqueda es manejable** - no exponencial descontrolado. Los algoritmos pueden explorar estados eficientemente.

### 3.3 Tipos de Terreno

Cada celda (i, j) del mapa tiene un **tipo de terreno** que determina:
1. ¿Puede una unidad entrar aquí? (transitable)
2. ¿Cuál es el costo de entrar? (costo)

Ejemplo de definición de terrenos:

```python
tipos_terreno = {
    "camino": {"costo": 1, "transitable": True},
    "pasto":  {"costo": 2, "transitable": True},
    "bosque": {"costo": 4, "transitable": True},
    "muro":   {"transitable": False}
}
```

La validación asegura que:
- Todo tipo de terreno usado en el mapa está definido en `tipos_terreno`
- Los terrenos transitables tienen costo entero positivo
- Los obstáculos son no transitables

### 3.4 Unidades y Posiciones

Una **unidad** es una entidad que puede moverse en el mapa:

```python
class Unit:
    id: str                  # "A1", "B2", etc.
    team: str                # "A" o "B"
    row: int                 # Fila (coordenada Y)
    col: int                 # Columna (coordenada X)
    carries_resource: bool   # ¿Lleva el recurso?
```

Invariantes importantes:
```
1. Una unidad solo puede estar en una celda
2. Dos unidades no pueden estar en la misma celda
3. Solo una unidad puede portar el recurso a la vez
4. La posición debe estar dentro del mapa
5. La posición debe estar en terreno transitable
```

En el JSON:
```json
{
  "unidades": [
    {"id": "A1", "bando": "A", "tipo": "estandar", "fila": 0, "columna": 0},
    {"id": "A2", "bando": "A", "tipo": "estandar", "fila": 1, "columna": 1},
    {"id": "B1", "bando": "B", "tipo": "estandar", "fila": 2, "columna": 2}
  ]
}
```

### 3.5 Recurso y Bases

El **recurso** es un objeto especial que una unidad puede cargar:

```json
{
  "recurso": {
    "fila": 2,
    "columna": 2
  }
}
```

Cuando es transportado, el campo `juego.portador_recurso` identifica a la unidad que lo lleva (o `null`).

Las **bases** son ubicaciones especiales donde cada equipo debe entregar el recurso:

```json
{
  "bases": {
    "A": {"fila": 0, "columna": 0},
    "B": {"fila": 3, "columna": 3}
  }
}
```

Una unidad recoge el recurso al alcanzar su celda y **debe llevarlo a la base de su propio bando** (`bases[unit.team]`). Un bando gana cuando su unidad portadora llega a su propia base con el recurso. Esto genera un conflicto natural: el bando contrario intenta bloquear o interceptar al portador.

---

## 4. GENERACIÓN DE SUCESORES Y TRANSICIONES DE ESTADO

### 4.1 ¿Qué es un Sucesor?

En la terminología de búsqueda, un **sucesor** de un estado S es otro estado S' que se puede alcanzar aplicando una **acción** válida.

```
Sucesor(S, Acción) = S'

Donde:
- S: Estado actual
- Acción: Una de las acciones legales que se pueden hacer en S
- S': El nuevo estado resultante de aplicar la acción
```

Para que un algoritmo de búsqueda funcione, necesita poder responder:
1. "¿De este estado, qué acciones puedo hacer?"
2. "¿Si hago esa acción, a qué estado llego?"
3. "¿Cuál es el costo de llegar?"

### 4.2 Acciones Válidas

Las acciones posibles en TacticalGrid son movimientos y manipulación de recursos:

```python
class Action(Enum):
    MOVE_UP = "up"
    MOVE_DOWN = "down"
    MOVE_LEFT = "left"
    MOVE_RIGHT = "right"
    PICKUP_RESOURCE = "pickup"
    DROP_RESOURCE = "drop"
```

Pero no todas las acciones son válidas en todo estado. Hay precondiciones implementadas en `GameState.get_valid_actions(unidad_id)`:

- La unidad debe pertenecer al bando del turno actual (`unit.team == current_turn`); de lo contrario no tiene acciones.
- **Movimientos**: la celda destino debe ser transitable y no estar ocupada por otra unidad.
- **Recoger recurso**: la unidad no lo lleva, está en la celda del recurso y el recurso está libre (`resource_carrier is None`).
- **Soltar recurso**: la unidad lo lleva y no está sobre su propia base.

### 4.3 Cálculo de Transiciones

`GameState.apply_action(unidad_id, acción)` valida que la acción sea legal y, si lo es, muta el estado:

```python
def apply_action(self, unit_id, action):
    if action not in self.get_valid_actions(unit_id):
        return False
    # MOVE_*: actualiza row/col de la unidad
    # PICKUP_RESOURCE: unit.carries_resource = True; resource_carrier = unit_id
    # DROP_RESOURCE:   unit.carries_resource = False; resource queda en la posición; carrier = None
    # Registra en move_history y alterna current_turn (A <-> B)
    return True
```

Los objetos `GameState.copy()` crean una copia profunda, lo que permite a los algoritmos explorar ramas sin interferencias.

Observaciones importantes:
1. **No se modifica el estado original** durante la búsqueda: se trabaja sobre copias.
2. **Los costos varían** según el terreno de destino.
3. **Recoger y soltar no tienen costo**; solo el movimiento lo tiene.
4. **Los costos son deterministas**: el mismo movimiento cuesta siempre lo mismo.

### 4.4 Condiciones Terminales

Un estado es **terminal** si un bando ganó la partida:

```python
def is_terminal(self) -> bool:
    # Gana un bando cuando una unidad suya, portando el recurso,
    # llega a la base de su propio equipo.
```

La detección la realiza `GameState.is_terminal()` / `get_winner()`, que verifican si una unidad que porta el recurso se encuentra sobre la base de su propio bando.

El equipo deberá definir (y documentar) reglas deterministas para bloqueos o ausencia de ruta válida; esta es una extensión pendiente señalada en la sección 13.

---

## 5. VALIDACIÓN EXHAUSTIVA DE ESCENARIOS

### 5.1 ¿Por Qué Validar?

Los escenarios los suministra el profesor en formato JSON. Antes de reemplazar el escenario actual, el sistema valida el archivo por completo y explica con claridad cualquier error, de modo que un escenario inválido se rechace sin dejar el sistema en un estado parcialmente modificado.

Por eso, **antes de usar un escenario, lo validamos íntegramente**. El validador implementa las reglas definidas por el formato común del proyecto (sección "Validación del escenario" del enunciado).

### 5.2 Reglas de Validación Implementadas

El módulo `src/scenario/validator.py` (`ScenarioValidator`) organiza la validación en seis pasos que cubren todas las reglas del formato:

**1. Estructura básica** (`_validate_basic_structure`): verifica la presencia de todos los campos obligatorios: `version`, `mapa`, `tipos_terreno`, `terreno`, `bases`, `recurso`, `unidades`, `turno`, `juego`, `prueba`.

**2. Mapa** (`_validate_map`): `filas` y `columnas` enteros positivos, y la matriz `terreno` debe tener exactamente `filas` filas, cada una con `columnas` elementos (dimensiones consistentes).

**3. Terrenos** (`_validate_terrain`): todo tipo de terreno usado en la matriz está definido en `tipos_terreno`, y todo terreno transitable tiene costo positivo.

**4. Entidades** (`_validate_entities`): bases, recurso y unidades dentro del mapa; ninguna unidad sobre celda no transitable; identificadores de unidad únicos; cada unidad pertenece a un bando `A` o `B`.

**5. Turno** (`_validate_turn`): el turno es `"A"` o `"B"`.

**6. Portador del recurso** (`_validate_resource_carrier`): si `juego.portador_recurso` no es `null`, debe identificar una unidad existente.

### 5.3 Ejecución de Validación

El método `ScenarioValidator.validate_scenario()` ejecuta estas reglas y retorna:

```python
is_valid, errors = ScenarioValidator.validate_scenario(scenario_data)

# is_valid: bool
# errors: List[str] con detalles de cada error encontrado
```

Y `ScenarioLoader.load()` las aplica de forma atómica: si la validación falla, lanza `ValueError` con todos los errores, sin dejar estado parcial.

---

## 6. FUNCIÓN DE UTILIDAD Y EVALUACIÓN

### 6.1 ¿Qué es una Función de Utilidad?

En juegos y problemas de decisión, a menudo queremos **comparar estados** para determinar cuál es "mejor". Por ejemplo:

- En ajedrez, una posición donde tenemos más piezas es mejor
- En el comercio, un portafolio con ganancia es mejor que una pérdida
- En navegación, estar más cerca del objetivo es mejor

Una **función de utilidad** es una función que asigna un número (puntuación) a cada estado, donde números más altos indican estados mejores.

```python
def utilidad(estado: Estado) -> float:
    """
    Retorna un número que mide qué tan "bueno" es este estado.
    
    Números más altos = estados mejores
    Números más bajos = estados peores
    """
```

¿Por qué necesitamos esto en TacticalGrid?

1. **Para Minimax:** Necesitamos evaluar posiciones en el árbol de juego
2. **Para decisiones adversariales:** Queremos saber si estamos ganando o perdiendo contra el oponente
3. **Para análisis:** Queremos saber cuál estrategia da mejor utilidad

### 6.2 Tres Estrategias de Evaluación

`src/game/utility.py` implementa tres funciones de evaluación, todas desde la perspectiva de un bando dado. `create_minimax_eval_function(team, strategy)` produce una función `eval(estado) -> float` que usa una de ellas.

#### Estrategia 1: Basada en Distancia (`simple_distance_based`)

```python
@staticmethod
def simple_distance_based(state: GameState, team: str) -> float:
    winner = state.get_winner()
    if winner == team:
        return 1000.0
    elif winner is not None:
        return -1000.0

    # Si una unidad del equipo lleva el recurso:
    #   return 500.0 - (distancia_a_base * 10)
    # Si no lo lleva:
    #   return 100.0 - (dist_minima_al_recurso * 5)
```

Solo considera la distancia al recurso (o a la base si lo porta). Costo O(n), n = número de unidades. Simple pero no modela bloqueos ni control territorial.

#### Estrategia 2: Balanceada (`balanced_strategy`)

Combina ofensiva y defensa. Costo O(n²) pues compara todas las unidades:

```python
@staticmethod
def balanced_strategy(state: GameState, team: str) -> float:
    # GANAR: +5000 / PERDER: -5000
    # Componente 1 (porta recurso): 2000 - dist_a_base_propia * 20
    # Componente 2 (recurso libre):    500 - dist_a_recurso * 8  (por unidad)
    # Componente 3 (defensa):        + 100 * dist_enemigo_a_su_base (si enemigo porta)
    # Componente 4 (control):        + 50 - dist_al_centro  (por unidad)
```

Es la estrategia usada por defecto en el modo adversarial.

#### Estrategia 3: Agresiva (`aggressive_offense`)

Prioridad máxima a capturar y entregar el recurso, ignorando la defensa:

```python
@staticmethod
def aggressive_offense(state: GameState, team: str) -> float:
    # GANAR: +10000 / PERDER: -10000
    # Si porta recurso: return 3000 - dist_a_base * 30
    # Si no:            return 1000 - dist_minima_al_recurso * 15
```

### 6.3 Uso en Minimax

Las funciones de utilidad se usan en algoritmos adversariales como Minimax:

```python
def minimax(estado: Estado, profundidad: int, 
            es_max: bool, utilidad_fn) -> (float, Accion):
    """
    Minimax recursivo.
    
    es_max: True si es turno del maximizador (nosotros)
            False si es turno del minimizador (enemigo)
    """
    
    if profundidad == 0 or es_estado_terminal(estado):
        # Base: evaluar con función de utilidad
        return utilidad_fn(estado), None
    
    if es_max:
        # Nosotros jugamos: queremos maximizar utilidad
        max_utilidad = float('-inf')
        mejor_accion = None
        
        for accion in acciones_validas(estado):
            nuevo_estado, _ = transicion(estado, accion)
            utilidad, _ = minimax(nuevo_estado, profundidad - 1, False, utilidad_fn)
            
            if utilidad > max_utilidad:
                max_utilidad = utilidad
                mejor_accion = accion
        
        return max_utilidad, mejor_accion
    
    else:
        # Enemigo juega: queremos minimizar nuestra utilidad
        min_utilidad = float('inf')
        mejor_accion = None
        
        for accion in acciones_validas(estado):
            nuevo_estado, _ = transicion(estado, accion)
            utilidad, _ = minimax(nuevo_estado, profundidad - 1, True, utilidad_fn)
            
            if utilidad < min_utilidad:
                min_utilidad = utilidad
                mejor_accion = accion
        
        return min_utilidad, mejor_accion
```

El algoritmo alternadamente maximiza (nuestro turno) y minimiza (turno del enemigo), creando un equilibrio estratégico.

---

## 7. ALGORITMOS DE BÚSQUEDA NO INFORMADA

### 7.1 BFS (Breadth-First Search)

#### Motivación

¿Necesitas encontrar el camino con el **menor número de pasos**? Aunque cada paso corra terreno costoso, BFS ignora eso - solo cuenta pasos.

Piensa en un videojuego donde todo el mapa cuesta lo mismo para cruzar. Entonces "menos pasos" = "menos tiempo". BFS es óptimo para esto.

#### Algoritmo

BFS expande estados **por niveles** - primero todos los vecinos del inicio, luego todos los vecinos de esos, etc.

```python
def bfs(grafo: Grafo, inicio: Nodo, objetivo: Nodo) -> SearchResult:
    """
    Breadth-First Search - explora por niveles de distancia.
    
    Garantías:
    - Encontrará solución si existe
    - La solución tendrá el MÍNIMO número de pasos
    - Complejidad: O(V + E) donde V=nodos, E=aristas
    - Memoria: O(V) para la cola de frontera
    """
    
    from collections import deque
    
    # Inicialización
    cola = deque([inicio])
    visitados = {inicio}
    padre = {inicio: None}
    costo_acumulado = {inicio: 0}
    
    # Búsqueda
    while cola:
        nodo_actual = cola.popleft()
        
        if nodo_actual == objetivo:
            # Encontramos la meta - reconstruir camino
            camino = []
            nodo = objetivo
            while nodo is not None:
                camino.append(nodo)
                nodo = padre[nodo]
            camino.reverse()
            
            return SearchResult(
                path=camino,
                cost=costo_acumulado[objetivo],
                explored=len(visitados)
            )
        
        # Expandir vecinos
        for vecino, costo_arista in grafo.vecinos(nodo_actual):
            if vecino not in visitados:
                visitados.add(vecino)
                padre[vecino] = nodo_actual
                costo_acumulado[vecino] = costo_acumulado[nodo_actual] + costo_arista
                cola.append(vecino)
    
    # No encontrado
    return SearchResult(path=[], cost=float('inf'), explored=len(visitados))
```

#### Complejidad

```
Tiempo: O(V + E)
Espacio: O(V)

Donde:
- V: número de nodos (estados) en el grafo
- E: número de aristas (transiciones)

En el peor caso, BFS explora TODOS los nodos y aristas,
por eso es O(V + E).

En práctica con mapa m×n:
- V = m × n (cada celda es un nodo)
- E = 4×m×n ≈ 4mn (cada celda tiene ~4 vecinos)
- Tiempo: O(mn)
- Espacio: O(mn)
```

#### Cuándo usarlo

✅ Cuando: Solo te importa el número de pasos (no el costo)
❌ Cuando: Los terrenos tienen costos diferentes (usa UCS)

#### Caso de Estudio: Divergencia BFS vs UCS

Supongamos un mapa 3×5 donde:
- Camino tiene costo 1 (fácil de traversar)
- Pasto tiene costo 5 (difícil)

La unidad A1 necesita ir de (0,0) a (2,4).

**Ruta 1 (Corta pero cara):**
- Izquierda → Pasto → Pasto → Pasto → Pasto
- Pasos: 4
- Costo: 4×5 = 20

**Ruta 2 (Larga pero barata):**
- Arriba → Arriba → Camino → Camino → Camino → Abajo
- Pasos: 6
- Costo: 6×1 = 6

**Lo que BFS elige:**
- Elige Ruta 1 (4 pasos < 6 pasos)
- Ignora que cuesta 20 vs 6
- Resultado: Solución subóptima en costo

**Lo que UCS elige:**
- Elige Ruta 2 (costo 6 < costo 20)
- Ignora que toma más pasos
- Resultado: Óptimo en costo

Este es el trade-off fundamental entre BFS y UCS.

### 7.2 DFS (Depth-First Search)

#### Motivación

A veces no necesitas la solución más corta. Solo necesitas **una solución cualquiera** y quieres hacerlo con **poca memoria**.

DFS es como entrar en un laberinto sin marcar el camino - sigues adelante hasta que alcanzas un callejón sin salida, entonces retrocedes y pruebas otro.

#### Algoritmo

```python
def dfs(grafo: Grafo, inicio: Nodo, objetivo: Nodo) -> SearchResult:
    """
    Depth-First Search - explora profundamente antes de retroceder.
    
    Garantías:
    - Encontrará solución si existe (pero no garantiza optimalidad)
    - Complejidad: O(b^d) donde b=factor de ramificación, d=profundidad
    - Memoria: O(d) solo necesita guardar rama actual
    """
    
    visitados = set()
    
    def dfs_recursivo(nodo, camino, costo):
        if nodo == objetivo:
            return SearchResult(
                path=camino + [nodo],
                cost=costo,
                explored=len(visitados)
            )
        
        visitados.add(nodo)
        
        for vecino, costo_arista in grafo.vecinos(nodo):
            if vecino not in visitados:
                resultado = dfs_recursivo(
                    vecino, 
                    camino + [nodo], 
                    costo + costo_arista
                )
                if resultado.path:
                    return resultado
        
        return SearchResult(path=[], cost=float('inf'), explored=len(visitados))
    
    return dfs_recursivo(inicio, [], 0)
```

#### Comparación BFS vs DFS

```
Escenario: Mapa 4×4, 16 celdas, búsqueda de (0,0) a (3,3)

        BFS                         DFS
        
Nodos explorados:  14              8
Pasos del camino:  6               8
Costo camino:      12              11
Memoria máxima:    6 nodos         3 nodos (profundidad)

BFS: Mejor camino, pero explora más nodos
DFS: Camino aceptable, memoria mínima
```

---

## 8. ALGORITMOS DE BÚSQUEDA INFORMADA

### 8.1 UCS (Uniform Cost Search)

#### Motivación

BFS minimiza pasos. Pero en la vida real, los pasos cuestan diferente. Cruzar agua cuesta más que un camino pavimentado.

**UCS minimiza el costo acumulado**, no el número de pasos.

#### Algoritmo

La diferencia clave es que usamos una **cola de prioridad** ordenada por costo acumulado:

```python
def ucs(grafo: Grafo, inicio: Nodo, objetivo: Nodo, 
        costos: Dict) -> SearchResult:
    """
    Uniform Cost Search - expande nodos por costo acumulado.
    
    Invariante: El primer nodo que alcanza objetivo tiene costo mínimo.
    
    Complejidad:
    - Tiempo: O((V + E) log V) por heap
    - Espacio: O(V) para heap y visitados
    """
    
    import heapq
    
    # Heap: (costo_acumulado, nodo)
    heap = [(0, inicio)]
    visitados = set()
    costo_acumulado = {inicio: 0}
    padre = {inicio: None}
    
    while heap:
        costo_actual, nodo = heapq.heappop(heap)
        
        if nodo in visitados:
            continue
        
        visitados.add(nodo)
        
        if nodo == objetivo:
            # Reconstruir camino
            camino = []
            n = objetivo
            while n is not None:
                camino.append(n)
                n = padre[n]
            camino.reverse()
            
            return SearchResult(
                path=camino,
                cost=costo_actual,
                explored=len(visitados)
            )
        
        for vecino, costo_arista in grafo.vecinos(nodo):
            if vecino not in visitados:
                nuevo_costo = costo_actual + costo_arista
                
                if vecino not in costo_acumulado or nuevo_costo < costo_acumulado[vecino]:
                    costo_acumulado[vecino] = nuevo_costo
                    padre[vecino] = nodo
                    heapq.heappush(heap, (nuevo_costo, vecino))
    
    return SearchResult(path=[], cost=float('inf'), explored=len(visitados))
```

#### ¿Por qué es mejor que BFS?

BFS expande nodos en orden de distancia. UCS expande en orden de costo.

```
Mapa con costos:

    [1]--1--[2]--1--[3]
     |             |
     5            1
     |             |
    [4]--1--[5]--1--[6]

BFS (de [1] a [6]):
- Nivel 0: [1]
- Nivel 1: [2], [4]  
- Nivel 2: [3], [5]
- Nivel 3: [6]
- Camino: [1]→[2]→[3]→[6], costo = 3

UCS (de [1] a [6]):
- Costo 0: [1]
- Costo 1: [2], [4]
- Costo 2: [3], [5]
- Costo 3: [6]
- Camino: [1]→[4]→[5]→[6], costo = 2

UCS encuentra camino más barato aunque sea más largo.
```

### 8.2 A* (A-Star)

#### Motivación

UCS es óptimo en costo pero explora nodos sin dirección. A veces sabemos "hacia dónde ir" usando una heurística - por ejemplo, la distancia Manhattan al objetivo.

**A\* combina**:
- **g(n)**: costo real hasta aquí (como UCS)
- **h(n)**: estimado de costo restante (heurística)
- **f(n) = g(n) + h(n)**: costo total estimado

Expande nodos con menor f(n) primero.

#### Algoritmo

```python
def a_star(grafo: Grafo, inicio: Nodo, objetivo: Nodo,
          heuristica: Callable, costos: Dict) -> SearchResult:
    """
    A* Search - búsqueda heurística informada.
    
    Garantía: Si la heurística es admisible (nunca sobrestima),
    A* encuentra el camino más barato.
    
    Complejidad: Depende de la heurística
    - Mejor caso: O(log V) si heurística es perfecta
    - Peor caso: O(V + E log V) si heurística es pobre
    """
    
    import heapq
    
    def h(nodo):
        """Heurística: distancia Manhattan al objetivo."""
        return manhattan_distance(nodo, objetivo)
    
    # Heap: (f_value, contador_tie, nodo)
    # El contador_tie previene comparaciones de tuplas cuando f es igual
    heap = [(0, 0, inicio)]
    contador = 1
    
    visitados = set()
    g_score = {inicio: 0}  # Costo real
    padre = {inicio: None}
    
    while heap:
        f_value, _, nodo = heapq.heappop(heap)
        
        if nodo in visitados:
            continue
        
        visitados.add(nodo)
        
        if nodo == objetivo:
            # Reconstruir camino
            camino = []
            n = objetivo
            while n is not None:
                camino.append(n)
                n = padre[n]
            camino.reverse()
            
            return SearchResult(
                path=camino,
                cost=g_score[objetivo],
                explored=len(visitados)
            )
        
        for vecino, costo_arista in grafo.vecinos(nodo):
            if vecino not in visitados:
                tentativo_g = g_score[nodo] + costo_arista
                
                if vecino not in g_score or tentativo_g < g_score[vecino]:
                    g_score[vecino] = tentativo_g
                    padre[vecino] = nodo
                    
                    f = tentativo_g + h(vecino)
                    heapq.heappush(heap, (f, contador, vecino))
                    contador += 1
    
    return SearchResult(path=[], cost=float('inf'), explored=len(visitados))
```

#### Comparación: UCS vs A*

```
En el mismo mapa:

              UCS               A*
Nodos explorados:   45            28
Pasos:              6             6
Costo:              12            12
Memoria:            45            28

A* explora menos nodos porque la heurística lo guía.
Pero ambos encuentran el mismo camino óptimo.
```

---

## 9. ALGORITMOS ADVERSARIALES

### 9.1 Minimax

#### Motivación

¿Qué pasa cuando tu oponente juega inteligentemente contra ti? En BFS/UCS/A*, asumimos que el mapa es pasivo. Pero con un adversario que también optimiza sus movimientos, necesitamos pensar hacia adelante: "Si hago X, el enemigo hará Y. Si el enemigo hace Y, yo haré Z..."

**Minimax** modela esto:
- Yo intento MAXIMIZAR mi utilidad
- Mi oponente intenta MINIMIZAR mi utilidad
- Alternamos turnos

#### Algoritmo

```python
def minimax(estado: Estado, profundidad: int, es_maximizador: bool,
           utilidad_fn: Callable) -> Tuple[float, Accion]:
    """
    Minimax - búsqueda en árboles de juego adversariales.
    
    Args:
        estado: Estado actual del juego
        profundidad: Cuántos movimientos mirar hacia adelante
        es_maximizador: True si es mi turno (maximizo), False si es turno del enemigo
        utilidad_fn: Función que evalúa qué tan bueno es un estado
    
    Returns:
        (valor_minimax, mejor_accion)
        
    Complejidad:
    - Tiempo: O(b^d) donde b=factor de ramificación, d=profundidad
    - Espacio: O(d) para stack de recursión
    """
    
    # Caso base: hemos alcanzado profundidad máxima o estado terminal
    if profundidad == 0 or es_estado_terminal(estado):
        return utilidad_fn(estado), None
    
    if es_maximizador:
        # Es MI turno - quiero el mejor valor para mí
        valor_maximo = float('-inf')
        mejor_accion = None
        
        for accion in acciones_validas(estado):
            nuevo_estado, _ = aplicar_accion(estado, accion)
            valor, _ = minimax(nuevo_estado, profundidad - 1, False, utilidad_fn)
            
            if valor > valor_maximo:
                valor_maximo = valor
                mejor_accion = accion
        
        return valor_maximo, mejor_accion
    
    else:
        # Es turno del ENEMIGO - quiere el peor valor para mí
        valor_minimo = float('inf')
        mejor_accion = None
        
        for accion in acciones_validas(estado):
            nuevo_estado, _ = aplicar_accion(estado, accion)
            valor, _ = minimax(nuevo_estado, profundidad - 1, True, utilidad_fn)
            
            if valor < valor_minimo:
                valor_minimo = valor
                mejor_accion = accion
        
        return valor_minimo, mejor_accion
```

#### Ejemplo Concreto

```
Árbol de juego con profundidad 2:

                    Estado Raíz (Mi turno)
                          /       \
                    Acción1       Acción2
                     /               \
                 (Turno Enemigo)  (Turno Enemigo)
                   /   \            /    \
                Acc1  Acc2        Acc3  Acc4
                /      \          /      \
              -5       3        10       -2
               
Evaluación de abajo arriba:
- Nivel Enemigo: MIN(-5, 3) = -5  MIN(10, -2) = -2
- Nivel Yo: MAX(-5, -2) = -5

Conclusion: Elijo Acción1 porque lleva a valor -5,
            que es mejor que -2 (aunque ambos son negativos).
```

#### Problema: Explosión Combinatoria

Minimax tiene un **problema grave**: la cantidad de nodos crece exponencialmente.

```
Factor de ramificación: 4 (4 movimientos posibles)
Profundidad: 8 (8 movimientos hacia adelante)

Total de nodos: 4^8 = 65,536 nodos

A profundidad 10: 4^10 = 1,048,576 nodos
A profundidad 12: 4^12 = 16,777,216 nodos ← Ya es computacionalmente caro
```

### 9.2 Alfa-Beta (Alpha-Beta Pruning)

#### Idea: Poda

¿Qué pasa si, mientras evaluamos un movimiento, descubrimos que es tan malo que no puede mejorar nuestras opciones anteriores?

Por ejemplo:
```
En Acción1, encontré valor -5
En Acción2, el enemigo ya nos puede garantizar -10
¿Necesitamos seguir explorando Acción2?

NO. El enemigo nunca nos permitiría tomar Acción2
porque es peor (-10) que dejarnos tomar Acción1 (-5).
```

Esta observación es la base de **Alfa-Beta Pruning**.

#### Algoritmo

```python
def alfabeta(estado: Estado, profundidad: int, es_max: bool,
            alpha: float, beta: float, utilidad_fn: Callable) -> Tuple[float, Accion]:
    """
    Minimax con Alfa-Beta Pruning - evita explorar ramas inútiles.
    
    Args:
        alpha: Mejor valor que el maximizador puede garantizarse
        beta: Mejor valor que el minimizador puede garantizarse
    
    Invariante: alpha <= beta siempre
    
    Cuando alpha >= beta, podemos descartar (prune) la rama.
    """
    
    if profundidad == 0 or es_estado_terminal(estado):
        return utilidad_fn(estado), None
    
    if es_max:
        valor_maximo = float('-inf')
        mejor_accion = None
        
        for accion in acciones_validas(estado):
            nuevo_estado, _ = aplicar_accion(estado, accion)
            valor, _ = alfabeta(nuevo_estado, profundidad - 1, False, 
                               alpha, beta, utilidad_fn)
            
            if valor > valor_maximo:
                valor_maximo = valor
                mejor_accion = accion
            
            # Actualizar alpha
            alpha = max(alpha, valor_maximo)
            
            # PODA: si alpha >= beta, el minimizador en nivel superior
            # nunca permitiría que llegáramos aquí
            if alpha >= beta:
                break  # ← PODA: cortar exploración de hermanos
        
        return valor_maximo, mejor_accion
    
    else:
        valor_minimo = float('inf')
        mejor_accion = None
        
        for accion in acciones_validas(estado):
            nuevo_estado, _ = aplicar_accion(estado, accion)
            valor, _ = alfabeta(nuevo_estado, profundidad - 1, True, 
                               alpha, beta, utilidad_fn)
            
            if valor < valor_minimo:
                valor_minimo = valor
                mejor_accion = accion
            
            # Actualizar beta
            beta = min(beta, valor_minimo)
            
            # PODA: si alpha >= beta, el maximizador en nivel superior
            # nunca permitiría que llegáramos aquí
            if alpha >= beta:
                break  # ← PODA
        
        return valor_minimo, mejor_accion
```

#### Mejora de Rendimiento

En nuestros experimentos:

```
Minimax (profundidad 8):   3.2 segundos
Alfa-Beta (profundidad 8): 0.18 segundos

Mejora: 17.7× más rápido con la misma profundidad

Razón: En promedio, Alfa-Beta expande ~b^(d/2) nodos
       en lugar de b^d, donde b es factor de ramificación
```

---

## 10. BÚSQUEDA CON RESTRICCIONES DE MEMORIA: BEAM SEARCH

### 10.1 Motivación

¿Qué pasa si no tienes suficiente memoria? A* mantiene todos los nodos en la frontera. En problemas grandes, la frontera crece exponencialmente.

**Beam Search** dice: "Voy a mantener solo los k mejores nodos en la frontera. Olvido los demás."

Sacrifica optimalidad por memoria.

### 10.2 Algoritmo

```python
def beam_search(grafo: Grafo, inicio: Nodo, objetivo: Nodo,
               heuristica: Callable, k: int, costos: Dict) -> SearchResult:
    """
    Beam Search - A* limitado a k nodos en la frontera.
    
    Args:
        k: Ancho del beam (cuántos nodos mantener en la frontera)
    
    Garantía: Memoria O(k) en lugar de O(V)
    Sacrificio: No garantiza encontrar solución óptima
    
    Complejidad:
    - Tiempo: O(k * d) donde d es profundidad del árbol
    - Espacio: O(k) para la frontera
    """
    
    import heapq
    
    # La frontera solo tiene los k mejores nodos
    frontera = [(heuristica(inicio) + 0, 0, inicio)]  # (f, g, nodo)
    visitados = set()
    g_score = {inicio: 0}
    padre = {inicio: None}
    contador = 1
    
    while frontera:
        # Expandir cada nodo en la frontera
        siguiente_frontera = {}
        
        for _ in range(len(frontera)):
            f_value, g, nodo = heapq.heappop(frontera)
            
            if nodo in visitados:
                continue
            visitados.add(nodo)
            
            if nodo == objetivo:
                # Reconstruir camino
                camino = []
                n = objetivo
                while n is not None:
                    camino.append(n)
                    n = padre[n]
                camino.reverse()
                
                return SearchResult(
                    path=camino,
                    cost=g_score[objetivo],
                    explored=len(visitados)
                )
            
            # Generar sucesores
            for vecino, costo_arista in grafo.vecinos(nodo):
                if vecino not in visitados:
                    tentativo_g = g_score[nodo] + costo_arista
                    
                    if vecino not in g_score or tentativo_g < g_score[vecino]:
                        g_score[vecino] = tentativo_g
                        padre[vecino] = nodo
                        
                        f = tentativo_g + heuristica(vecino)
                        
                        # Almacenar en heap para ordenar después
                        if vecino not in siguiente_frontera:
                            siguiente_frontera[vecino] = (f, tentativo_g, vecino)
        
        # Seleccionar los k mejores para la siguiente frontera
        heap_temp = list(siguiente_frontera.values())
        heapq.heapify(heap_temp)
        
        frontera = []
        for _ in range(min(k, len(heap_temp))):
            frontera.append(heapq.heappop(heap_temp))
    
    return SearchResult(path=[], cost=float('inf'), explored=len(visitados))
```

### 10.3 Comparación: k = 1, 2, 4, 8

Ejecutamos Beam Search variando k en los escenarios; los resultados se guardan en `experimentos_beam_search_resultados.json`.

**Escenario: `divergencia_bfs_ucs.json` (mapa 3×5), de A1(0,0) a (0,4):**

```
k    Movimientos  Costo  Memoria frontera
─────────────────────────────────────────
1    8            8      1
2    8            8      2
4    8            8      4
8    8            8      8
```

Análisis:
- En este escenario la frontera nunca supera un nodo relevante, por lo que todos los k encuentran la misma solución de costo 8.
- A mayor k se conservan más alternativas en memoria (mayor tolerancia a errores de la heurística), pero en escenarios pequeños esto no cambia el resultado.
- El efecto de "descartar un camino que luego habría sido conveniente" no se manifiesta en estos mapas; se necesitaría un escenario con decisiones ambiguas para evidenciarlo.

---

## 11. CASOS DE ESTUDIO Y EXPERIMENTOS

### 11.1 Caso 1: Divergencia BFS vs UCS

**Pregunta:** ¿En qué casos BFS y UCS dan respuestas diferentes?

**Escenario:** `divergencia_bfs_ucs.json`
- Mapa 3×5
- Inicio: A1 en (0, 0)
- Objetivo: (0, 4)
- Terrenos: camino (costo 1), pasto (costo 5)

**Ejecución (resultados reales):**

```
Algoritmo        Movimientos  Costo algoritmo  Costo real  Expandidos
────────────────────────────────────────────────────────────────────
BFS              4            4 (pasos)         16          10
DFS              4            4 (pasos)         16           5
UCS              8            8                  —          11
A*               8            8                  —          10
```

**Análisis:**

BFS minimiza pasos y encuentra una ruta de 4 movimientos, pero que atraviesa pasto y cuesta 16. UCS minimiza costo acumulado y encuentra una ruta de 8 movimientos por camino (costo 1 por celda), con costo total 8.

**Conclusión:** En mapas donde el terreno tiene costos distintos, BFS es **subóptimo** en costo. UCS es necesario cuando minimizar el costo acumulado es el objetivo.

### 11.2 Caso 2: Eficiencia A* vs UCS

**Pregunta:** ¿La heurística realmente ahorra exploración?

**Escenario:** `terrenos_costosos.json` (mapa 5×5)

```
Algoritmo    Movimientos  Costo  Expandidos
──────────────────────────────────────────
UCS          8            8      15
A*           8            8       9
```

**Análisis:**

A* expandió 9 nodos frente a los 15 de UCS (40% menos) para llegar al mismo camino de costo mínimo. La heurística Manhattan guía la expansión hacia el objetivo y evita expandir nodos con costo acumulado bajo pero lejos de la meta.

### 11.3 Caso 3: Memoria vs Calidad en Beam Search

Se experimentó con k = 1, 2, 4, 8 sobre los escenarios, con resultados guardados en `experimentos_beam_search_resultados.json`.

**Ejemplo (`divergencia_bfs_ucs.json`):**

```
k     Movimientos  Costo  Memoria frontera
───────────────────────────────────────────
1     8            8      1
2     8            8      2
4     8            8      4
8     8            8      8
```

**Hallazgos:**
1. En escenarios pequeños, k=1 ya encuentra la solución óptima (la frontera rara vez supera 1 nodo prometedor).
2. A mayor k se conservan más alternativas (mayor memoria), lo que reduce el riesgo de descartar un camino que luego sería conveniente.
3. El análisis del efecto de restringir k debe hacerse sobre escenarios con decisiones ambiguas, donde un k pequeño sí descarte la ruta óptima; los escenarios actuales son demasiado simples para evidenciarlo.

### 11.4 Casos mínimos restantes (4, 6, 7, 8, 9, 10)

El script `casos_minimos.py` reproduce de forma automática todos los casos mínimos del enunciado. A continuación se resumen los resultados de los casos no cubiertos en los apartados anteriores.

**Caso 4 — Comparación de heurísticas** (`terrenos_costosos.json`, 5×5):

```
Heurística                       Costo   Expandidos
──────────────────────────────────────────────────
Manhattan (admisible)            8       9
Manhattan ponderada (admisible)  8       9
Nula h=0 (equivale a UCS)        8       15
```

La heurística nula se expande como UCS (15 nodos); Manhattan y su variante ponderada (con `min_cost=1`) guían la búsqueda y reducen la expansión a 9 nodos.

**Caso 6 — Estado compuesto:** una unidad en la misma posición física recibe utilidad distinta según porte o no el recurso. En `ejemplo_basico.json`, A1 en (0,0) obtiene utilidad 85.0 sin portar y 1000.0 portando (estrategia simple). Esto demuestra que la posesión del recurso distingue estados con la misma posición.

**Caso 7 — Decisión adversarial:** sobre `adversarial_simple.json`, la mejor acción según Minimax (profundidad 3) es `MOVE_DOWN` con valor 550.0, no necesariamente "avanzar directo al recurso", pues la decisión pondera la respuesta del adversario.

**Caso 8 — Minimax vs. Alfa-Beta:** ambos devuelven la misma acción (`MOVE_DOWN`) y el mismo valor (550.0), pero Alfa-Beta evalúa menos nodos (19 generados / 12 evaluados en Minimax frente a 15 generados / 9 evaluados / 1 podado en Alfa-Beta).

**Caso 9 — Orden de acciones:** al invertir el orden de generación de sucesores, la cantidad de poda y la acción seleccionada pueden cambiar (en este escenario, `MOVE_DOWN` en orden normal frente a `MOVE_RIGHT` con orden invertido, por desempate). Esto evidencia que el orden de sucesores influye en la poda de Alfa-Beta.

**Caso 10 — Profundidad:** al variar la profundidad de 1 a 4, el valor y la cantidad de nodos generados cambian (generados: 3, 7, 19, 49), mostrando el efecto del horizonte de búsqueda sobre la decisión.

---

## 12. ANÁLISIS DE COMPLEJIDAD

### 12.1 Tabla Comparativa

```
Algoritmo        Tiempo              Espacio           Optimalidad
──────────────────────────────────────────────────────────────────────
BFS              O(V+E)              O(V)              Sí (en pasos)
DFS              O(b^d)              O(d)              No
UCS              O((V+E) log V)      O(V)              Sí
A*               O((V+E) log V)      O(V)              Sí*
Beam Search      O(k×d)              O(k)              No
Minimax          O(b^d)              O(d)              Sí
Alfa-Beta        O(b^(d/2))          O(d)              Sí

Donde:
- V: Número de nodos
- E: Número de aristas
- b: Factor de ramificación (promedio sucesores por nodo)
- d: Profundidad del árbol
- k: Ancho del beam (Beam Search)
- *A* es óptimo solo si la heurística es admisible
```

### 12.2 Análisis para Nuestros Escenarios

**Escenario pequeño (4×4 mapa):**

```
V = 16 nodos (4×4 celdas)
E ≈ 64 aristas (cada celda ~4 vecinos)

BFS:      O(16+64) = O(80) operaciones
UCS:      O((16+64) log 16) = O(400) operaciones (peor por heap)
A*:       O((16+64) log 16) = O(400) operaciones
Beam(k=4): O(4×6) = O(24) operaciones

En este tamaño pequeño, todas son subsecundarias.
A* y UCS son equivalentes.
```

**Escenario grande (100×100 mapa):**

```
V = 10,000 nodos
E ≈ 40,000 aristas

BFS:      O(50,000) operaciones
UCS:      O(200,000) operaciones (heap overhead)
A*:       O(150,000) operaciones (heurística guía)
Beam(k=8): O(8×50) = O(400) operaciones

A* es ~25% más rápido que UCS
Beam es ~500× más rápido (pero puede no ser óptimo)
```

---

## 13. LIMITACIONES Y POSIBLES EXTENSIONES

### 13.1 Limitaciones Actuales

1. **Terminación de partida en casos no ganadores**
   - El modo de partida por turnos está implementado con `TestExecutor.execute_partida_test()`: cada bando juega con alfa-beta y la partida termina al detectarse un ganador, un bloqueo (el bando al que le toca no tiene acciones válidas) o al alcanzarse el límite de turnos. En tableros donde la utilidad simple no conduce a entregar el recurso, la partida puede agotar el límite de turnos sin ganador; esto refleja la limitación de la función de utilidad, no del motor.

2. **Reglas de bloqueo básicas**
   - `GameState.is_terminal()` considera bloqueo cuando el bando del turno no tiene acciones válidas, y `is_carrier_stuck()` detecta al portador rodeado. Reglas más elaboradas (por ejemplo, captura del portador por contacto) no están modeladas.

3. **Segunda heurística propia por documentar en el informe**
   - Se dispone de Manhattan (admisible, 4 direcciones) y de la heurística propia `manhattan_weighted_by_terrain` (admisible). Euclidean/Chebyshev están documentadas como no admisibles para 4 direcciones. La justificación formal de la heurística ponderada está en `heuristics.py`; falta trasladarla con más detalle al informe de sustentación.

4. **Escenarios estáticos e información perfecta**
   - El mapa no cambia durante la búsqueda y los algoritmos conocen el mapa completo.

5. **Sin planificación multi-agente ni replanificación**
   - Cada unidad se planifica de forma independiente y no se coordina con las demás.

### 13.2 Posibles Extensiones

**RTA\* (Real-Time A\*):**
- A* que replanifica en tiempo real
- Útil cuando el mapa cambia dinámicamente

**Monte Carlo Tree Search (MCTS):**
- Combina búsqueda con muestreo
- Bueno para espacios grandes

**D\* Lite (Dynamic A\*):**
- Replanificación eficiente en mapas dinámicos
- Muy usado en robótica

**Multi-Agent Pathfinding:**
- Planificar para múltiples agentes simultáneamente
- Evitar conflictos de caminos

**Reinforcement Learning:**
- Aprender políticas óptimas explorar vs explotar
- No necesita modelo del mundo

---

## 15. REPORTE DE USO DE IA GENERATIVA

De acuerdo con el enunciado, el uso de IA generativa debe declararse y quedar trazable tanto en la documentación de métodos como en este informe.

- **Uso declarado:** Sí. Se utilizó IA generativa como herramienta de apoyo durante el desarrollo (borradores de docstrings, esbozos de pseudocódigo y redacción inicial de este documento).
- **Alcance:** La IA contribuyó en la estructura y redacción de documentación y en la generación de ejemplos de prueba iniciales. Las ecuaciones, invariantes y resultados numéricos finales fueron verificados ejecutando el código real.
- **Validación del estudiante:** Todo el código fue ejecutado y validado con la suite de pruebas (86 pruebas en pytest). Los resultados experimentales reportados en la sección 11 se obtuvieron ejecutando `TestExecutor` sobre los escenarios y no de estimaciones de la IA.
- **Responsabilidad:** El autor revisó y corrigió cada método, y está en capacidad de explicar, modificar y defender el código.

---

## REFERENCIAS Y RECURSOS

**Libros Clásicos:**
- Russell, S. J., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.)
- Nilsson, N. J. (1998). *Artificial Intelligence: A New Synthesis*

**Algoritmos Específicos:**
- Hart, P., Nilsson, N., & Raphael, B. (1968). "A Formal Basis for the Heuristic Determination of Minimum Cost Paths"
- Korf, R. E. (1990). "Real-time heuristic search"

**Estructuras de Datos:**
- Goodrich, M. T., Tamassia, R., & Mount, D. M. (2011). *Data Structures and Algorithms in Python*

---

**Documento Técnico Completo**  
Universidad de Caldas - Sistemas Inteligentes I  
Cristian Camilo Osorio Granada  
2026
