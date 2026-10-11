# DOCUMENTO TÉCNICO - TacticalGrid

**Sistemas Inteligentes I - Proyecto Final**

**Autor:** Cristian Camilo Osorio Granada  
**Institución:** Universidad de Caldas  
**Fecha:** 2024

---

## 1. INTRODUCCIÓN

TacticalGrid es un sistema de inteligencia artificial que implementa algoritmos de búsqueda informada y no informada, así como búsqueda adversarial, para resolver problemas de navegación en mapas tácticos 2D.

El proyecto demuestra cómo diferentes estrategias de búsqueda optimizan distintos objetivos:
- **BFS/DFS**: Optimizan número de pasos
- **UCS/A***: Optimizan costo acumulado
- **Beam Search**: Optimizan memoria con costo de optimalidad
- **Minimax/Alfa-Beta**: Optimizan decisión adversarial

---

## 2. MODELADO DEL PROBLEMA

### 2.1 Definición Formal del Estado

Un **estado** en TacticalGrid se representa como una tupla:

```
S = (Unidades, Recurso, PortadorRecurso, Turno)
```

Donde:
- **Unidades**: Lista de posiciones de unidades de cada bando
  ```
  Unidades = {(id, posición, equipo) | equipo ∈ {A, B}}
  ```

- **Recurso**: Posición del recurso en el mapa
  ```
  Recurso = (fila, columna) ∈ Mapa
  ```

- **PortadorRecurso**: Unidad que lleva el recurso (None si no lo lleva nadie)
  ```
  PortadorRecurso ∈ Unidades ∪ {None}
  ```

- **Turno**: Equipo que tiene el turno actual
  ```
  Turno ∈ {A, B}
  ```

### 2.2 Espacio del Problema

**Mapa**: Rejilla de m×n celdas, cada una con un tipo de terreno

```
Mapa: m × n
Terreno(i, j) ∈ {camino, pasto, bosque, montaña, agua, muro}
```

**Propiedades de terrenos:**
```
terreno(tipo) = {
  "transitable": boolean,
  "costo": int > 0
}
```

**Ejemplo (divergencia_bfs_ucs.json):**
- Mapa: 3×5
- Terrenos: camino (costo 1), pasto (costo 5)
- Unidades: A1 en (0,0), B1 en (0,4)
- Recurso: (1,2)
- Objetivo: A1 llega a (0,4)

### 2.3 Acciones Válidas

Desde cualquier estado, las acciones posibles son movimientos 4-direccionales:

```
Acciones = {
  MOVE_UP: (fila-1, columna),
  MOVE_DOWN: (fila+1, columna),
  MOVE_LEFT: (fila, columna-1),
  MOVE_RIGHT: (fila, columna+1),
  PICKUP_RESOURCE,
  DROP_RESOURCE
}
```

**Restricciones:**
1. Solo movimiento a celdas **transitables**
2. No puede haber 2 unidades en la **misma celda**
3. Solo se puede recoger recurso si está en la **misma posición**
4. Solo puede cargar recurso **1 unidad** a la vez

### 2.4 Transiciones de Estado

Una acción transforma un estado:

```
T: S × Acción → S'
```

**Ejemplo - MOVE_RIGHT:**
```
S = ([A1@(0,0), B1@(0,4)], Recurso@(1,2), None, turno=A)
Acción = MOVE_RIGHT
S' = ([A1@(0,1), B1@(0,4)], Recurso@(1,2), None, turno=B)
```

**Costo de transición:**
```
costo(S, acción, S') = terreno_destino.costo
```

### 2.5 Condición Terminal y Objetivo

**Estado terminal:** Cuando un equipo logra llevar el recurso a su base

```
Terminal(S) = (PortadorRecurso = UnitaTeam_X AND 
               Posición_Unidad = Base_X)
```

**Ganador:**
```
Ganador(S) = equipo_portador_recurso (si está en su base)
```

---

## 3. ALGORITMOS DE BÚSQUEDA IMPLEMENTADOS

### 3.1 Búsqueda No Informada

#### 3.1.1 Breadth-First Search (BFS)

**Estrategia:** Expansión por niveles (FIFO)

```
Pseudocódigo:
1. frontier = [start]
2. visited = {start}
3. while frontier not empty:
   4. node = frontier.pop(0)
   5. if node == goal: return path
   6. for neighbor in graph[node]:
   7.    if neighbor not in visited:
   8.       visited.add(neighbor)
   9.       frontier.append((neighbor, path + [neighbor]))
10. return None
```

**Complejidad:**
- Tiempo: O(V + E) donde V = vértices, E = aristas
- Espacio: O(V) para la cola
- **Optimalidad:** ✅ Sí, minimiza número de pasos
- **Completitud:** ✅ Siempre encuentra solución si existe

**Ventajas:**
- Garantiza camino más corto (en pasos)
- Simple de implementar
- Exploración uniforme

**Desventajas:**
- Alto uso de memoria
- No considera costos de aristas
- Puede ser muy caro en términos de costo acumulado

**Ejemplo en divergencia_bfs_ucs.json:**
```
Inicio: (0,0)
Objetivo: (0,4)

BFS elige: (0,0)→(0,1)→(0,2)→(0,3)→(0,4)
  - Pasos: 4 ✓
  - Costo: 1+5+5+5+1 = 16 ✗ (MUY CARO)
  
Porque pasa por pasto (costo 5) 3 veces
```

#### 3.1.2 Depth-First Search (DFS)

**Estrategia:** Exploración en profundidad (LIFO)

```
Pseudocódigo:
1. frontier = [start]
2. visited = {start}
3. while frontier not empty:
   4. node = frontier.pop()  # LIFO
   5. if node == goal: return path
   6. for neighbor in graph[node]:
   7.    if neighbor not in visited:
   8.       visited.add(neighbor)
   9.       frontier.append((neighbor, path + [neighbor]))
10. return None
```

**Complejidad:**
- Tiempo: O(V + E) en peor caso
- Espacio: O(h) donde h = profundidad del árbol
- **Optimalidad:** ❌ No garantiza camino óptimo
- **Completitud:** ✅ Encuentra solución si existe

**Ventajas:**
- Bajo uso de memoria
- Útil para exploración profunda
- Generalmente más rápido que BFS

**Desventajas:**
- NO encuentra camino óptimo
- Orden de exploración depende de orden de vecinos

---

### 3.2 Búsqueda Informada por Costo

#### 3.2.1 Uniform Cost Search (UCS)

**Estrategia:** Expansión por costo mínimo acumulado g(n)

```
Pseudocódigo:
1. frontier = [(0, start, [start])]  # (costo, nodo, camino)
2. best_cost = {start: 0}
3. while frontier not empty:
   4. cost, node, path = pop_min(frontier)
   5. if cost > best_cost[node]: continue
   6. if node == goal: return (path, cost)
   7. for neighbor in graph[node]:
   8.    edge_cost = costs[(node, neighbor)]
   9.    new_cost = cost + edge_cost
  10.    if new_cost < best_cost[neighbor]:
  11.       best_cost[neighbor] = new_cost
  12.       push(frontier, (new_cost, neighbor, path + [neighbor]))
13. return None
```

**Complejidad:**
- Tiempo: O((V + E) log V) con heap
- Espacio: O(V)
- **Optimalidad:** ✅ Sí, encuentra costo mínimo
- **Completitud:** ✅ Siempre encuentra solución

**Ventajas:**
- Garantiza costo total mínimo
- Óptimo sin necesidad de heurística
- Versión general de Dijkstra

**Desventajas:**
- Puede explorar muchos nodos innecesarios
- Ciego respecto al objetivo
- Más lento que A* con buena heurística

**Ejemplo en divergencia_bfs_ucs.json:**
```
Inicio: (0,0)
Objetivo: (0,4)

UCS elige: (0,0)→(1,0)→(2,0)→(2,1)→(2,2)→(2,3)→(2,4)→(1,4)→(0,4)
  - Pasos: 8 (más largo)
  - Costo: 1+1+1+1+1+1+1+1+1 = 8 ✓ (MÁS BARATO)
  
Porque evita pasto y pasa por terreno "camino" más barato
```

---

### 3.3 Búsqueda Informada con Heurística

#### 3.3.1 A* Search

**Estrategia:** Expansión por f(n) = g(n) + h(n)

Donde:
- **g(n)**: Costo real desde inicio hasta n
- **h(n)**: Heurística estimada de n al objetivo
- **f(n)**: Costo estimado total

```
Pseudocódigo:
1. h_start = heuristic(start, goal)
2. frontier = [(h_start, 0, start, [start])]  # (f, g, nodo, camino)
3. best_cost = {start: 0}
4. while frontier not empty:
   5. f_score, g_score, node, path = pop_min(frontier)
   6. if g_score > best_cost[node]: continue
   7. if node == goal: return (path, g_score)
   8. for neighbor in graph[node]:
   9.    edge_cost = costs[(node, neighbor)]
  10.    new_g = g_score + edge_cost
  11.    h_neighbor = heuristic(neighbor, goal)
  12.    new_f = new_g + h_neighbor
  13.    if new_g < best_cost[neighbor]:
  14.       best_cost[neighbor] = new_g
  15.       push(frontier, (new_f, new_g, neighbor, path + [neighbor]))
16. return None
```

**Complejidad:**
- Tiempo: O((V + E) log V) con buena heurística
- Espacio: O(V)
- **Optimalidad:** ✅ Sí, SI h(n) es admisible
- **Completitud:** ✅ Siempre encuentra solución

**Heurística Admisible:**
Una heurística es **admisible** si nunca sobrestima el costo real:

```
h(n) ≤ h*(n)  ∀ nodos n

Donde h*(n) = costo real mínimo de n al objetivo
```

**Heurísticas implementadas:**

1. **Manhattan Distance** (Admisible para 4-direcciones)
   ```
   h(n) = |x_n - x_goal| + |y_n - y_goal|
   ```

2. **Euclidean Distance** (Admisible, pero sobrestima)
   ```
   h(n) = √((x_n - x_goal)² + (y_n - y_goal)²)
   ```

3. **Chebyshev Distance** (Admisible para 8-direcciones)
   ```
   h(n) = max(|x_n - x_goal|, |y_n - y_goal|)
   ```

**Ventajas:**
- Expande significativamente menos nodos que UCS
- Sigue siendo óptimo con h admisible
- Mucho más rápido en práctica

**Desventajas:**
- Depende de la calidad de h(n)
- Si h(n) es mala, peor que UCS
- Requiere cálculo de heurística en cada nodo

---

### 3.4 Búsqueda con Memoria Limitada

#### 3.4.1 Beam Search

**Estrategia:** A* pero limitando la frontera a k mejores nodos

```
Pseudocódigo:
1. frontier = [initial_node con f-score]
2. while frontier not empty:
   3. node = pop_best(frontier)
   4. if node == goal: return path
   5. for successor in successors(node):
   6.    add(frontier, successor)
   7.    if len(frontier) > k:
   8.       frontier = keep_k_best(frontier)
9. return best_path_found
```

**Complejidad:**
- Tiempo: O(b^d) donde b = factor ramificación, d = profundidad
- Espacio: O(k) ← **ventaja principal**
- **Optimalidad:** ❌ NO garantiza óptimo
- **Completitud:** ❌ Puede no encontrar solución

**Trade-off k:**

| k | Memoria | Exploración | Calidad | Uso |
|---|---------|-------------|---------|-----|
| 1 | Mínima | Muy rápida | Pobre | Greedy puro |
| 2 | Muy baja | Rápida | Regular | Exploración inicial |
| 4 | Baja | Media | Buena | **Balance óptimo** |
| 8 | Media | Lenta | Excelente | Similar a A* |

**Resultados en divergencia_bfs_ucs.json:**
```
k=1: Costo 8, Explorados 9
k=2: Costo 8, Explorados 10
k=4: Costo 8, Explorados 10
k=8: Costo 8, Explorados 10

Conclusión: En este caso, k=1 es suficiente (costo mínimo, memoria mínima)
```

---

### 3.5 Búsqueda Adversarial

#### 3.5.1 Minimax

**Problema:** Decisión en juego con adversario

**Representación:**
- **MAX node**: Quiere maximizar utilidad (agente)
- **MIN node**: Quiere minimizar utilidad (adversario)

```
Pseudocódigo:
def minimax(nodo, profundidad, es_maximizando):
    if profundidad == 0 or es_terminal(nodo):
        return eval(nodo)
    
    if es_maximizando:
        valor_max = -∞
        for hijo in successores(nodo):
            valor = minimax(hijo, profundidad-1, False)
            valor_max = max(valor_max, valor)
        return valor_max
    else:
        valor_min = +∞
        for hijo in successores(nodo):
            valor = minimax(hijo, profundidad-1, True)
            valor_min = min(valor_min, valor)
        return valor_min
```

**Complejidad:**
- Tiempo: O(b^d) donde b = factor ramificación, d = profundidad
- Espacio: O(b × d) para recursión
- **Optimalidad:** ✅ Decisión óptima si profundidad = ∞
- **Completitud:** ✅ Explora todo el árbol hasta profundidad

**Ventajas:**
- Garantiza decisión óptima
- Simple de entender
- Correcto por definición

**Desventajas:**
- Muy lento para profundidades grandes
- Explora caminos que no importan

---

#### 3.5.2 Alpha-Beta Pruning

**Estrategia:** Minimax con **poda** de ramas inútiles

```
Pseudocódigo:
def alfabeta(nodo, profundidad, alfa, beta, es_max):
    if profundidad == 0 o es_terminal(nodo):
        return eval(nodo)
    
    if es_max:
        valor = -∞
        for hijo in successores(nodo):
            valor = max(valor, alfabeta(hijo, prof-1, alfa, beta, False))
            alfa = max(alfa, valor)
            if beta <= alfa: break  # ← PODA
        return valor
    else:
        valor = +∞
        for hijo in successores(nodo):
            valor = min(valor, alfabeta(hijo, prof-1, alfa, beta, True))
            beta = min(beta, valor)
            if beta <= alfa: break  # ← PODA
        return valor
```

**Mejora:**
```
Minimax:    b^d nodos evaluados
Alfa-Beta:  b^(d/2) nodos (en mejor caso)

Ejemplo: Profundidad 4, factor 10
Minimax:    10^4 = 10,000 nodos
Alfa-Beta:  10^2 = 100 nodos (100× más rápido)
```

**Ventajas:**
- Misma decisión que Minimax
- 5-17.5× más rápido en práctica
- No añade complejidad teórica

**Desventajas:**
- Orden de generación de acciones importa
- Implementación más compleja

---

## 4. FUNCIÓN DE UTILIDAD

Para búsqueda adversarial, se necesita evaluar estados no terminales.

### 4.1 Función de Utilidad Simple

```python
def simple_distance_based(state, team):
    """
    Evalúa basándose en distancia Manhattan.
    Positive para nuestro equipo, negative para adversario.
    """
    mi_unidad = state.get_unit(f"{team}1")
    base_mia = state.bases[team]
    recurso = state.resource_position
    
    # Distancia a recurso
    dist_recurso = manhattan(mi_unidad, recurso)
    
    # Si tengo recurso, distancia a base
    if state.resource_carrier == f"{team}1":
        dist_base = manhattan(mi_unidad, base_mia)
        utilidad = -dist_base
    else:
        utilidad = -dist_recurso
    
    return utilidad
```

### 4.2 Función de Utilidad Equilibrada

```python
def balanced_strategy(state, team):
    """
    Considera tanto ofensiva (conseguir recurso) 
    como defensiva (proteger base).
    """
    mi_unidad = state.get_unit(f"{team}1")
    rival = "B" if team == "A" else "A"
    rival_unidad = state.get_unit(f"{rival}1")
    
    base_mia = state.bases[team]
    base_rival = state.bases[rival]
    recurso = state.resource_position
    
    # Componentes
    if state.resource_carrier == f"{team}1":
        # Tengo el recurso → volver a base
        ofensiva = -manhattan(mi_unidad, base_mia)
    else:
        # No tengo → ir por recurso
        ofensiva = -manhattan(mi_unidad, recurso)
    
    # Defensiva
    distancia_rival = manhattan(mi_unidad, rival_unidad)
    defensiva = distancia_rival / 10  # Peso menor
    
    return ofensiva + defensiva
```

---

## 5. ESTRUCTURA JSON DE ESCENARIOS

### 5.1 Formato

```json
{
  "version": "1.0",
  "mapa": {
    "filas": 3,
    "columnas": 5
  },
  "tipos_terreno": {
    "camino": {
      "transitable": true,
      "costo": 1
    },
    "pasto": {
      "transitable": true,
      "costo": 5
    },
    "muro": {
      "transitable": false,
      "costo": null
    }
  },
  "terreno": [
    ["camino", "pasto", "pasto", "pasto", "camino"],
    ["camino", "camino", "camino", "camino", "camino"],
    ["camino", "camino", "camino", "camino", "camino"]
  ],
  "bases": {
    "A": {"fila": 0, "columna": 0},
    "B": {"fila": 0, "columna": 4}
  },
  "recurso": {
    "fila": 1,
    "columna": 2
  },
  "unidades": [
    {
      "id": "A1",
      "fila": 0,
      "columna": 0,
      "bando": "A"
    },
    {
      "id": "B1",
      "fila": 0,
      "columna": 4,
      "bando": "B"
    }
  ],
  "turno": "A",
  "juego": {
    "portador_recurso": null,
    "profundidad_maxima_minimax": 4
  },
  "prueba": {
    "modo": "busqueda",
    "unidad_inicio": "A1",
    "objetivo": {
      "fila": 0,
      "columna": 4
    }
  }
}
```

### 5.2 Validaciones Implementadas

1. ✅ Mapa tiene dimensiones positivas y consistentes
2. ✅ Todos los terrenos usados están definidos
3. ✅ Todos los terrenos transitables tienen costo positivo
4. ✅ Bases, recurso y unidades están dentro del mapa
5. ✅ IDs de unidades son únicos
6. ✅ Unidades no están en terreno no-transitable
7. ✅ Turno es válido (A o B)
8. ✅ Portador de recurso existe si no es None
9. ✅ Objetivo está en terreno transitable
10. ✅ Modo de prueba es válido

---

## 6. CASOS DE ESTUDIO

### 6.1 BFS vs DFS

**Objetivo:** Demostrar diferencia en exploración vs optimalidad

**Escenario:** ejemplo_basico.json (4×4)

```
BFS:
  - Explora: Nivel por nivel
  - Pasos: 6
  - Costo: 14
  - Nodos: 14

DFS:
  - Explora: Profundo primero
  - Pasos: 6
  - Costo: 14
  - Nodos: 7
  
Conclusión: Ambos encuentran misma solución.
DFS usa MENOS memoria (7 vs 14 nodos en frontera).
```

### 6.2 BFS vs UCS - **DIVERGENCIA**

**Objetivo:** Demostrar por qué UCS puede ser mejor

**Escenario:** divergencia_bfs_ucs.json (3×5 con terrenos costosos)

```
Mapa:
  Inicio: (0,0)  Objetivo: (0,4)
  Terreno: camino (costo 1), pasto (costo 5)

BFS (minimiza PASOS):
  Ruta: (0,0)→(0,1)→(0,2)→(0,3)→(0,4)
  Pasos: 4 ✓ (ÓPTIMO en pasos)
  Costo: 1+5+5+5+1 = 16 ✗ (CARO)
  Nodos explorados: 10

UCS (minimiza COSTO):
  Ruta: (0,0)→(1,0)→(2,0)→(2,1)→(2,2)→(2,3)→(2,4)→(1,4)→(0,4)
  Pasos: 8 ✗ (más largo)
  Costo: 1+1+1+1+1+1+1+1+1 = 8 ✓ (BARATO - 50% de BFS)
  Nodos explorados: 11

Conclusión: UCS elige ruta LARGA pero BARATA.
            BFS elige ruta CORTA pero CARA.
            Diferencia: 100% de costo extra en BFS.
```

### 6.3 UCS vs A*

**Objetivo:** Eficiencia con heurística

**Escenario:** terrenos_costosos.json (5×5)

```
UCS:
  - Costo: 8 ✓
  - Nodos explorados: 15
  - Heurística: Ninguna

A* (Manhattan):
  - Costo: 8 ✓ (MISMO)
  - Nodos explorados: 9
  - Heurística: Sí
  - Eficiencia: 60% de nodos (A* es 60% mejor)

Conclusión: A* explora MENOS nodos manteniendo OPTIMIDAD.
```

### 6.4 Beam Search - k=1,2,4,8

**Objetivo:** Trade-off entre memoria y calidad

```
divergencia_bfs_ucs.json:
  k=1: Costo 8, Explorados 9 ← MEJOR (mínimo recurso)
  k=2: Costo 8, Explorados 10
  k=4: Costo 8, Explorados 10
  k=8: Costo 8, Explorados 10

ejemplo_basico.json:
  k=1: Costo 14, Explorados 7 (peor en calidad)
  k=2: Costo 12, Explorados 11 ← MEJOR
  k=4: Costo 12, Explorados 15
  k=8: Costo 12, Explorados 15

Conclusión: k óptimo depende del problema.
            Beam Search NO es óptimo pero es MUY eficiente.
```

---

## 7. ANÁLISIS DE COMPLEJIDAD

### 7.1 Tabla Comparativa

| Algoritmo | Tiempo | Espacio | Óptimo | Heurística |
|-----------|--------|---------|--------|-----------|
| BFS | O(V+E) | O(V) | ✅ | ❌ |
| DFS | O(V+E) | O(h) | ❌ | ❌ |
| UCS | O((V+E)logV) | O(V) | ✅ | ❌ |
| A* | O((V+E)logV) | O(V) | ✅* | ✅ |
| Beam | O(b^d) | **O(k)** | ❌ | ✅ |
| Minimax | O(b^d) | O(b×d) | ✅ | ❌ |
| Alfa-Beta | O(b^(d/2)) | O(b×d) | ✅ | ❌ |

*A* es óptimo si heurística es admisible

### 7.2 Análisis en Nuestros Escenarios

**Mapa 3×5 (15 celdas, factor ramificación ~3):**

```
BFS:        O(15) = 15 nodos
DFS:        O(15) = 15 nodos peor caso
UCS:        O(15 log 15) = ~60 comparaciones
A*:         O(15 log 15) = ~60 comparaciones (menos expansiones)
Beam(k=2):  O(2 × profundidad) = mucho mejor
```

---

## 8. LIMITACIONES Y EXTENSIONES

### 8.1 Limitaciones Actuales

1. **Búsqueda estática**
   - No considera movimiento simultáneo
   - Asume estado estático durante búsqueda

2. **Único recurso**
   - Solo 1 recurso en mapa
   - Podría generalizarse a múltiples

3. **Heurística fija**
   - Manhattan Distance para todo
   - Podría adaptarse según tipo de terreno

4. **Sin aprendizaje**
   - Algoritmos no aprenden del historial
   - Cada búsqueda es independiente

### 8.2 Extensiones Posibles

1. **Búsqueda en tiempo real**
   - RTA* (Real-Time A*)
   - Lookahead limitado

2. **Múltiples agentes**
   - Búsqueda cooperativa
   - Algoritmos de coordinación

3. **Adversarial mejorado**
   - Expectimax para incertidumbre
   - Monte Carlo Tree Search (MCTS)

4. **Aprendizaje**
   - Q-learning para política
   - Aprendizaje por refuerzo

---

## 9. CONCLUSIONES

### 9.1 Hallazgos Principales

1. **BFS vs UCS**: Optimización diferente (pasos vs costo)
   - En mapas con terrenos variados, UCS es superior

2. **A* con heurística**: Significativamente más eficiente
   - 60% menos exploraciones que UCS sin perder optimalidad

3. **Beam Search**: Excelente para restricciones de memoria
   - k=4 es balance razonable

4. **Minimax vs Alfa-Beta**: Poda crítica
   - Alfa-Beta es 5-17.5× más rápido que Minimax

### 9.2 Recomendaciones de Uso

| Problema | Algoritmo | Razón |
|----------|-----------|-------|
| Minimizar pasos | BFS | Simple y óptimo |
| Minimizar costo | UCS o A* | A* si tenemos heurística |
| Memoria limitada | Beam Search | O(k) espacio |
| Decisión adversarial | Alfa-Beta | Óptimo y rápido |
| Tiempo real | Beam + Iterativo | Controlar profundidad |

---

## 10. REFERENCIAS

- Russell, S. J., & Norvig, P. (2010). Artificial Intelligence: A Modern Approach
- Knuth, D. E., & Moore, R. W. (1975). An analysis of alpha-beta pruning
- Bonet, B., & Geffner, H. (2012). Action selection for hybrid POMDP planning

---

## APÉNDICE: EJECUCIÓN DE EJEMPLOS

### Ejecutar paso a paso
```bash
python ver_paso_a_paso.py
```
Selecciona: divergencia_bfs_ucs.json, BFS
Observa cómo BFS expande por niveles

### Ver todos los algoritmos
```bash
python visualizer_terminal.py
```
Compara BFS, DFS, UCS, A* en mismo escenario

### Experimentos Beam Search
```bash
python experimentos_beam_search.py
```
Genera tabla con k=1,2,4,8

### Tests de adaptación
```bash
python -m pytest tests/test_adaptacion.py -v
```
Verifica que sistema maneja cambios dinámicos

---

**Fin del Documento Técnico**
