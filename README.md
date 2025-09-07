# Buddy System — Documentación del algoritmo (JS)

## 1) Propósito
Implementar un **asignador de memoria tipo Buddy** sobre un bloque total de memoria (aquí: `1024 KB`) usando un **árbol binario completo implícito**. Cada **nodo** representa un bloque de tamaño potencia de dos y con una **dirección inicial**. El algoritmo:
- **Redondea hacia arriba** el tamaño solicitado a la **siguiente potencia de dos**.
- **Divide** recursivamente bloques hasta obtener uno del tamaño requerido.
- **Asigna** el bloque hoja resultante.
- **Libera** y **fusiona** (coalescing) dos buddies libres para reconstruir bloques mayores.

> En este código, la lógica vive en las clases `Node` y `BuddyTree`. La UI solo pinta y lanza las llamadas.

---

## 2) Estructuras de datos

### 2.1 `Node`
Campos relevantes para el algoritmo:
- `id`: identificador único (solo utilidad local).
- `tamano`: tamaño del bloque (**potencia de 2**).
- `direccion_inicio`: desplazamiento del bloque desde 0 (base absoluta del bloque).
- `padre`, `izquierdo`, `derecho`: enlaces del árbol binario.
- `esta_dividido`: `true` si el nodo ya fue **particionado** en dos buddies (no es hoja disponible).
- `esta_asignado`: `true` si el bloque hoja está **ocupado**.
- `processId`, `requestedSize`: metadatos de asignación (no afectan a la corrección del algoritmo).

**Invariantes de nodo:**
- Si `esta_dividido === true` ⇒ el nodo es **padre** y **no** puede estar asignado.
- Si `esta_asignado === true` ⇒ el nodo es **hoja**, `esta_dividido === false`.
- Si un nodo es hoja y libre ⇒ `!esta_dividido && !esta_asignado`.

### 2.2 `BuddyTree`
- `raiz`: nodo con `tamano_total`, **debe ser potencia de 2** (validado en el constructor).
- `nodos_asignados: Map<direccion_inicio, Node>`: índice rápido para liberar por dirección.

**Chequeos estructurales clave:**
- **Constructor**: valida que `tamano_total` sea potencia de 2 (`(x & (x-1)) === 0`).
- **Asignar**: rechaza tamaños `<= 0` y solicitudes mayores que la raíz.
- **Liberar**: verifica que la dirección exista en `nodos_asignados`.

---

## 3) Funciones núcleo del algoritmo

### 3.1 ` _nextPowerOfTwo(n) `
Devuelve la **menor potencia de 2 ≥ n**. Garantiza que todo bloque asignado es potencia de dos.
- Caso borde: `n === 0` → `1`.

### 3.2 `allocate(tamano_solicitado)`
1. **Normaliza**: `tamano_requerido = _nextPowerOfTwo(tamano_solicitado)`.
2. **Valida contra la raíz**.
3. **Busca/Divide**: llama a ` _findAndSplit(raiz, tamano_requerido)`.
4. Si obtiene un nodo hoja adecuado:
   - Marca `esta_asignado = true`.
   - Registra en `nodos_asignados` por `direccion_inicio`.
5. Si no hay bloque disponible: reporta error.

**Complejidad** (sin UI): `O(log M)`, donde `M` es el tamaño de la memoria total (en KB) porque la altura del árbol es `log2(M)`.

### 3.3 `_findAndSplit(nodo_actual, tamano_requerido)`
Regla de decisión **clásica de Buddy**:

- **Podas/descartes**:
  - Si `nodo_actual` es nulo, o su tamaño `< tamano_requerido`, o **ya está asignado** ⇒ `null`.

- **Caso exacto (hoja)**:
  - Si `nodo_actual.tamano === tamano_requerido` **y** `!nodo_actual.esta_dividido` ⇒ **éste es el bloque** (retorna el nodo).

- **No conviene dividir más**:
  - Si al dividir el tamaño por 2 **quedaría menor** que `tamano_requerido` ⇒  
    - Si el nodo **no está dividido**, devolver el **nodo actual** (el bloque es suficientemente grande, pero una división adicional ya no produciría un buddy del tamaño requerido; esta es la condición que evita sobre-dividir).  
    - Si ya está dividido ⇒ `null`.

- **División**:
  - Si el nodo aún **no está dividido** y **sí se puede**:  
    - Marca `esta_dividido = true`.
    - Crea `izquierdo` y `derecho` con `tamano/2`, direcciones contiguas (`direccion_inicio` y `direccion_inicio + tamano/2`).

  - **Búsqueda recursiva** en **izquierdo**; si falla, intenta **derecho**.

> **Efecto práctico**: estrategia **depth-first, left-first** (asignación hacia la izquierda primero). Es una política válida de Buddy.

### 3.4 `free(direccion)`
1. Busca el nodo asignado en `nodos_asignados` por `direccion`.
2. Marca como **libre** (`esta_asignado = false`, limpia metadatos).
3. Llama a ` _tryMerge(nodo.padre) ` para intentar **coalescing** ascendente.

### 3.5 `_tryMerge(padre)`
Verifica la **condición de coalescing de buddies** en el **padre**:
- Ambos hijos existen **y** son **hojas libres**:
  - `izquierdo` y `derecho` **no** están divididos (`!esta_dividido`)
  - **no** están asignados (`!esta_asignado`)

Si la condición se cumple, **fusiona** a través de la rutina de merge (en este código la fusión real del árbol se ejecuta en `renderMergeAnimation` y luego re-intenta merge en el abuelo).

> **Nota de diseño**: La comprobación de fusión es lógica/algorítmica aquí, pero la **eliminación de hijos** y la marca `padre.esta_dividido = false` ocurre tras la animación. Luego se invoca recursivamente ` _tryMerge(padre.padre) ` para **coalescer hacia arriba** mientras sea posible—comportamiento standard del Buddy.

---

## 4) Flujo de asignación paso a paso (ejemplo)
Supón memoria total = `1024 KB`, solicitud = `100 KB`.
1. `nextPowerOfTwo(100) = 128` ⇒ se requiere bloque de `128 KB`.
2. `_findAndSplit` en raíz (`1024`):
   - 1024 ≠ 128 y `1024/2 = 512 ≥ 128` ⇒ **dividir** en dos de `512`.
   - Baja por el **izquierdo** (`512`) y repite: 512/2 = 256 ≥ 128 ⇒ **dividir**.
   - En `256`: 256/2 = 128 **no es menor** que 128, puede dividirse ⇒ **dividir**.
   - En el hijo `128` **exacto y hoja** ⇒ **asignar** ese nodo.
3. El bloque de `128` queda **asignado**; ancestros permanecen **divididos**.

---

## 5) Flujo de liberación y fusión (coalescing)
Al liberar el bloque `128`:
1. Se marca el nodo `128` como **libre**.
2. `_tryMerge(padre)` verifica si el **buddy hermano** (el otro `128`) también está **libre** y **no dividido**:
   - Si **sí**, se **eliminan ambos hijos** y el padre vuelve a ser un **bloque de 256 libre**.
3. Repite hacia arriba: ahora intenta fusionar el `256` con su buddy `256` para crear un `512`, y así hasta donde la condición se cumpla.

> Esto garantiza el **invariante Buddy**: dos buddies del mismo tamaño, contiguos y libres, se **fusionan** en un bloque mayor.

---

## 6) Propiedades, comprobaciones y garantías
- **Potencias de dos**: el sistema **solo** maneja bloques potencias de 2.  
  - Comprobado al inicio (memoria total) y al solicitar (`_nextPowerOfTwo`).

- **No sobre-división**: la condición  
  `if (nodo.tamano / 2 < tamano_requerido) return !nodo.esta_dividido ? nodo : null;`  
  evita dividir en tamaños menores al requerido y acepta el bloque actual como candidato (si es hoja), reduciendo fragmentación por exceso de splits.

- **Correctitud de dirección**: cada nodo tiene `direccion_inicio` y los hijos son contiguos y no solapados:
  - `hijoIzq.dir = padre.dir`
  - `hijoDer.dir = padre.dir + padre.tamano/2`

- **Índice de liberación**: `nodos_asignados` se indexa por **dirección de inicio** del bloque asignado. Esto:
  - Evita buscar por árbol al liberar.
  - Requiere que la **dirección de inicio** sea **única por hoja** (lo es mientras el árbol define particiones deterministas).

- **Fusión segura**: la condición de merge garantiza:
  - Nunca se fusionan bloques **con descendencia** (`!esta_dividido` en hijos).
  - Nunca se fusionan bloques **ocupados**.

- **Complejidad**:
  - **Asignar**: `O(log M)` (altura del árbol).
  - **Liberar + coalescing**: `O(log M)` en el peor caso (fusiona hasta la raíz).

- **Fragmentación interna (propia del Buddy)**:
  - En el peor caso, hasta **50%** del bloque asignado puede quedar sin usar (p.ej., pides 65 KB y se asigna 128 KB).  
  - El código registra el tamaño solicitado para mostrar “uso” visual, pero lógicamente el bloque asignado es el total de la potencia de dos.

---

## 7) Pseudocódigo esencial

### 7.1 `allocate`
```text
function allocate(req):
  if req <= 0: return null
  need = nextPow2(req)
  if need > root.size: error

  node = findAndSplit(root, need)
  if node != null:
    node.assigned = true
    indexByAddress[node.addr] = node
    return node
  else:
    error "no hay espacio"
```

### 7.2 `findAndSplit`
```text
function findAndSplit(n, need):
  if n == null or n.size < need or n.assigned:
    return null

  if n.size == need and !n.divided:
    return n

  if n.size/2 < need:
    return !n.divided ? n : null

  if !n.divided:
    n.divided = true
    n.left  = Node(n.size/2, n.addr)
    n.right = Node(n.size/2, n.addr + n.size/2)

  return findAndSplit(n.left, need) or findAndSplit(n.right, need)
```

### 7.3 `free`
```text
function free(addr):
  n = indexByAddress[addr]
  if n == null: error
  n.assigned = false
  delete indexByAddress[addr]
  tryMerge(n.parent)
```

### 7.4 `tryMerge`
```text
function tryMerge(p):
  if p == null: return
  if p.left and p.right and
     !p.left.divided and !p.left.assigned and
     !p.right.divided and !p.right.assigned:
      // merge children into parent
      remove p.left, p.right
      p.divided = false
      tryMerge(p.parent)
```

---

## 8) Casos borde y comportamiento
- **Solicitud mayor a la memoria total**: se rechaza explícitamente.
- **Solicitud 0 o negativa**: se ignora / devuelve `null`.
- **Árbol ya dividido**: si un nodo intermedio ya fue partido y no hay hojas adecuadas debajo, el recorrido retorna `null` y continúa en el hermano (por la recursión OR).
- **Preferencia izquierda**: `findAndSplit` siempre intenta **izquierda** primero, lo que **concentra asignaciones** en la mitad baja de la memoria (política determinista; aceptable, pero hay alternativas).

---

## 9) Diferencias respecto a un Buddy “clásico con listas”
Este diseño usa **árbol explícito**; muchos buddies clásicos usan **listas libres por orden** (una lista por tamaño potencia de 2):

- **Árbol (aquí)**:
  - Fácil visualizar la jerarquía y verificar buddies por **parentesco**.
  - Fusión simple: “si ambos hijos están libres ⇒ colapsar”.
  - Coste de recorrido: `O(log M)` por asignación.

- **Listas por orden (clásico)**:
  - Insertas y sacas de listas de tamaño exacto; si no hay, **divides** de una lista mayor y **empujas** los dos buddies a la lista del orden inferior, etc.
  - Suelen dar **constantes** muy buenas y localización inmediata por tamaño.
  - Requiere manejar correctamente **emparejamientos** para coalescing (localizar el **buddy por XOR** con el offset).

Tu enfoque de **árbol** es totalmente válido didácticamente (y muy claro).

---

## 10) Limitaciones y mejoras sugeridas
1. **Búsqueda “best-fit” por orden**: hoy la estrategia es depth-first a la izquierda. Podrías:
   - Hacer una **BFS** por niveles para priorizar bloques **exactos** antes de dividir más.
   - O implementar **listas por orden** para asignación más directa.

2. **Liberación por `processId`** (además de dirección): mantener un `Map<processId, Node>` para liberar por PID.

3. **Reuso/colisiones de dirección**: La `direccion_inicio` identifica un bloque hoja en el layout actual. Tras merges, la misma dirección puede **volver** a representar un bloque más grande—esto **no rompe** el índice porque liberas antes de re-asignar, pero si más adelante agregas **persistencia** o **historial**, conviene documentar este matiz.

4. **Verificación formal de invariantes** (tests):
   - “No hay nodos con `esta_dividido && esta_asignado`”.
   - “Las sumas de tamaños de hojas libres + asignadas = tamaño total”.
   - “No hay solapamiento de rangos `[direccion, direccion+tamano)`”.

5. **Métrica de fragmentación interna**: almacenar por asignación el “desperdicio” `tamano_bloque - requestedSize` y mostrar métricas acumuladas.

6. **Política de colocación**: permitir conmutar entre **left-first**, **right-first**, o **alternante** para estudiar el impacto en fragmentación y coalescing.

---

## 11) Resumen conceptual (para estudiar)
- Un **Buddy** divide la memoria en **bloques potencia de dos**.
- Para **asignar** `R`, usa el **menor 2^k ≥ R`.
- **Divide** hasta alcanzar `2^k`. Si dividir una vez más daría menos que `2^k`, **no divides** y te quedas con el bloque actual.
- Para **liberar**, marca el bloque como libre y **fusiona** si su **buddy** está libre y es hoja. Repite hacia arriba.
- **Garantías**: altura `O(log M)`, coalescing exacto, fragmentación interna ≤ 50% por bloque.

---

## 12) Qué hace la UI (solo por contexto)
- Llama a `buddySystem.allocate(size)` y `buddySystem.free(direccion)`.
- Dibuja el árbol, barras de uso proporcional a `requestedSize / tamano`, y **animaciones** de split/merge.
- `nodos_asignados` permite liberar rápido desde el botón “Liberar”.

---

## 13) Checklist mental al leer/expandir el código
- [ ] ¿El total es potencia de 2? (constructor)  
- [ ] ¿Redondeo solicitudes a potencia de 2? (`_nextPowerOfTwo`)  
- [ ] ¿Evito dividir cuando `size/2 < need`? (sí)  
- [ ] ¿Asigno solo hojas no divididas? (sí)  
- [ ] ¿Coalesce solo si ambos hijos son **hojas libres**? (sí)  
- [ ] ¿Propago merge hacia arriba? (sí)  
- [ ] **Complejidades logarítmicas** (sí)  
