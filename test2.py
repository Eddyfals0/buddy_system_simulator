import math

class Nodo:
    def __init__(self, tamano, direccion_inicio, padre=None):
        self.tamano = tamano
        self.direccion_inicio = direccion_inicio
        self.padre = padre
        self.izquierdo = None
        self.derecho = None
        self.esta_dividido = False
        # Nuevo estado para saber si el bloque está asignado.
        self.esta_asignado = False

    def __repr__(self):
        estado = "Dividido"
        if self.esta_asignado:
            estado = "Asignado"
        elif not self.esta_dividido:
            estado = "Libre"
            
        return f"[Dir: {self.direccion_inicio}, Tamaño: {self.tamano}, Estado: {estado}]"

class ArbolBuddySystem:
    def __init__(self, tamano_total):
        
        #Chequeo de valores de 2^n
        if not (tamano_total > 0 and (tamano_total & (tamano_total - 1)) == 0):
            raise ValueError("El tamaño total debe ser una potencia de 2.")
        
        #el nodo princial
        self.raiz = Nodo(tamano_total, 0)
        # Usamos un diccionario para encontrar nodos asignados por su dirección.
        self.nodos_asignados = {}

    def _siguiente_potencia_de_dos(self, n):
        if n == 0:
            return 1
        return 1 << (n - 1).bit_length()

    def asignar(self, tamano_solicitado):
        """Asigna un bloque de memoria del tamaño solicitado."""
        if tamano_solicitado <= 0:
            return None
            
        tamano_requerido = self._siguiente_potencia_de_dos(tamano_solicitado)
        
        if tamano_requerido > self.raiz.tamano:
            print(f"Error: El tamaño requerido ({tamano_requerido}) es mayor que el total ({self.raiz.tamano}).")
            return None

        nodo = self._encontrar_y_dividir(self.raiz, tamano_requerido)

        if nodo:
            nodo.esta_asignado = True
            self.nodos_asignados[nodo.direccion_inicio] = nodo
            print(f"✅ Asignado: Bloque de tamaño {nodo.tamano} en la dirección {nodo.direccion_inicio} (solicitado: {tamano_solicitado})")
            return nodo.direccion_inicio
        else:
            print(f"❌ Falló la asignación: No hay espacio para un bloque de tamaño {tamano_requerido} (solicitado: {tamano_solicitado})")
            return None

    def _encontrar_y_dividir(self, nodo_actual, tamano_requerido):
        """Busca recursivamente un nodo y lo divide si es necesario."""
        # Caso 1: El nodo actual es perfecto: no está dividido, no está asignado y tiene el tamaño justo.
        if not nodo_actual.esta_dividido and not nodo_actual.esta_asignado and nodo_actual.tamano == tamano_requerido:
            return nodo_actual

        # Caso 2: El nodo es demasiado pequeño o está asignado.
        if nodo_actual.tamano < tamano_requerido or nodo_actual.esta_asignado:
            return None

        # Caso 3: El nodo es más grande de lo necesario, hay que dividirlo.
        if not nodo_actual.esta_dividido:
            # Dividir el nodo si aún no tiene hijos
            nodo_actual.esta_dividido = True
            mitad_tamano = nodo_actual.tamano // 2
            nodo_actual.izquierdo = Nodo(mitad_tamano, nodo_actual.direccion_inicio, padre=nodo_actual)
            nodo_actual.derecho = Nodo(mitad_tamano, nodo_actual.direccion_inicio + mitad_tamano, padre=nodo_actual)
        
        # Una vez dividido (o si ya lo estaba), buscar en los hijos.
        # Intentar primero con el hijo izquierdo.
        nodo_encontrado = self._encontrar_y_dividir(nodo_actual.izquierdo, tamano_requerido)
        if nodo_encontrado:
            return nodo_encontrado
        
        # Si no se pudo en el izquierdo, intentar con el derecho.
        return self._encontrar_y_dividir(nodo_actual.derecho, tamano_requerido)

    def liberar(self, direccion):
        """Libera un bloque de memoria en la dirección especificada."""
        if direccion not in self.nodos_asignados:
            print(f"Error: Intento de liberar memoria no asignada en la dirección {direccion}")
            return

        nodo = self.nodos_asignados.pop(direccion)
        nodo.esta_asignado = False 
        
        print(f"🗑️  Liberando: Bloque de tamaño {nodo.tamano} en la dirección {nodo.direccion_inicio}")
        
        # Intentar fusionar recursivamente hacia arriba.
        self._intentar_fusionar(nodo.padre)

    def _intentar_fusionar(self, padre):
        """Fusiona los hijos de un nodo padre si ambos están libres."""
        if padre is None:
            return # No se puede fusionar más allá de la raíz

        hijo_izquierdo, hijo_derecho = padre.izquierdo, padre.derecho
        
        # Condición para fusionar: ambos hijos existen y ninguno está dividido ni asignado.
        if (hijo_izquierdo and not hijo_izquierdo.esta_dividido and not hijo_izquierdo.esta_asignado and
            hijo_derecho and not hijo_derecho.esta_dividido and not hijo_derecho.esta_asignado):
            
            print(f"🤝 Fusionando: Bloques en {hijo_izquierdo.direccion_inicio} y {hijo_derecho.direccion_inicio} para crear un bloque de {padre.tamano}")
            
            padre.izquierdo = None
            padre.derecho = None
            padre.esta_dividido = False
            
            # Intentar fusionar el padre recién liberado.
            self._intentar_fusionar(padre.padre)

    def imprimir_arbol(self, nodo=None, prefijo="", es_izquierdo=True):
        """Imprime una representación visual del árbol de memoria."""
        if not nodo:
            if not self.raiz:
                return
            nodo = self.raiz
        
        estado = ""
        if nodo.esta_asignado:
            estado = "🔴 ASIGNADO"
        elif not nodo.esta_dividido:
            estado = "🟢 LIBRE"

        print(prefijo + ("└── " if es_izquierdo else "├── ") + f"({nodo.tamano}B @ {nodo.direccion_inicio}) {estado}")
        
        if nodo.izquierdo and nodo.derecho:
            nuevo_prefijo = prefijo + ("    " if es_izquierdo else "│   ")
            self.imprimir_arbol(nodo.derecho, nuevo_prefijo, False)
            self.imprimir_arbol(nodo.izquierdo, nuevo_prefijo, True)

# --- Ejemplo de Uso ---
if __name__ == "__main__":
    print("--- Inicializando Sistema Buddy con 64 bytes ---")
    buddy = ArbolBuddySystem(1024)
    buddy.imprimir_arbol()
    
    print(buddy.raiz)

    print("\n--- 1. Asignando 8 bytes (necesita un bloque de 8) ---")
    dir1 = buddy.asignar(8)
    buddy.imprimir_arbol()

    print("\n--- 2. Asignando 12 bytes (necesita un bloque de 16) ---")
    dir2 = buddy.asignar(12)
    buddy.imprimir_arbol()

    print("\n--- 3. Asignando 7 bytes (necesita un bloque de 8) ---")
    dir3 = buddy.asignar(7)
    buddy.imprimir_arbol()

    print("\n--- 4. Liberando el primer bloque de 8 bytes (en dir 0) ---")
    buddy.liberar(dir1)
    buddy.imprimir_arbol()

    print("\n--- 5. Liberando el tercer bloque de 8 bytes (en dir 8) ---")
    print("Esto debería causar una fusión para recrear el bloque de 16.")
    buddy.liberar(dir3)
    buddy.imprimir_arbol()

    print("\n--- 6. Liberando el bloque de 16 bytes (en dir 16) ---")
    print("Esto debería causar múltiples fusiones hasta restaurar el estado inicial.")
    buddy.liberar(dir2)
    buddy.imprimir_arbol()

