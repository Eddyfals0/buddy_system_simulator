import math

class Nodo:
    def __init__(self, tamano, direccion_inicio, padre=None):
        self.tamano = tamano
        self.direccion_inicio = direccion_inicio
        self.padre = padre
        self.izquierdo = None
        self.derecho = None
        self.esta_dividido = False
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
        if not (tamano_total > 0 and (tamano_total & (tamano_total - 1)) == 0):
            raise ValueError("El tamaño total debe ser una potencia de 2.")
        self.raiz = Nodo(tamano_total, 0)
        self.nodos_asignados = {}

    def _siguiente_potencia_de_dos(self, n):
        if n == 0:
            return 1
        return 1 << (n - 1).bit_length()

    def asignar(self, tamano_solicitado):
        if tamano_solicitado <= 0:
            print("El tamaño solicitado debe ser > 0.")
            return None

        tamano_requerido = self._siguiente_potencia_de_dos(tamano_solicitado)

        if tamano_requerido > self.raiz.tamano:
            print(f"Error: El tamaño requerido ({tamano_requerido}) es mayor que el total ({self.raiz.tamano}).")
            return None

        nodo = self._encontrar_y_dividir(self.raiz, tamano_requerido)

        if nodo:
            nodo.esta_asignado = True
            self.nodos_asignados[nodo.direccion_inicio] = nodo
            print(f"✅ Asignado: Bloque de {nodo.tamano}B en dir {nodo.direccion_inicio} (solicitado: {tamano_solicitado})")
            return nodo.direccion_inicio
        else:
            print(f"❌ Falló la asignación: No hay espacio para un bloque de {tamano_requerido}B (solicitado: {tamano_solicitado})")
            return None

    def _encontrar_y_dividir(self, nodo_actual, tamano_requerido):
        if not nodo_actual.esta_dividido and not nodo_actual.esta_asignado and nodo_actual.tamano == tamano_requerido:
            return nodo_actual

        if nodo_actual.tamano < tamano_requerido or nodo_actual.esta_asignado:
            return None

        if not nodo_actual.esta_dividido:
            nodo_actual.esta_dividido = True
            mitad_tamano = nodo_actual.tamano // 2
            nodo_actual.izquierdo = Nodo(mitad_tamano, nodo_actual.direccion_inicio, padre=nodo_actual)
            nodo_actual.derecho = Nodo(mitad_tamano, nodo_actual.direccion_inicio + mitad_tamano, padre=nodo_actual)

        nodo_encontrado = self._encontrar_y_dividir(nodo_actual.izquierdo, tamano_requerido)
        if nodo_encontrado:
            return nodo_encontrado
        return self._encontrar_y_dividir(nodo_actual.derecho, tamano_requerido)

    def liberar(self, direccion):
        if direccion not in self.nodos_asignados:
            print(f"Error: Intento de liberar memoria no asignada en la dirección {direccion}")
            return False

        nodo = self.nodos_asignados.pop(direccion)
        nodo.esta_asignado = False
        print(f"🗑️  Liberando: Bloque de {nodo.tamano}B en dir {nodo.direccion_inicio}")
        self._intentar_fusionar(nodo.padre)
        return True

    def _intentar_fusionar(self, padre):
        if padre is None:
            return

        hijo_izq, hijo_der = padre.izquierdo, padre.derecho
        if (hijo_izq and not hijo_izq.esta_dividido and not hijo_izq.esta_asignado and
            hijo_der and not hijo_der.esta_dividido and not hijo_der.esta_asignado):
            print(f"🤝 Fusionando: {hijo_izq.direccion_inicio} y {hijo_der.direccion_inicio} -> bloque de {padre.tamano}B")
            padre.izquierdo = None
            padre.derecho = None
            padre.esta_dividido = False
            self._intentar_fusionar(padre.padre)

    def imprimir_arbol(self, nodo=None, prefijo="", es_izquierdo=True):
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

    def listar_asignados(self):
        if not self.nodos_asignados:
            print("No hay bloques asignados.")
            return
        print("Bloques asignados (dir -> tamaño):")
        for d, n in sorted(self.nodos_asignados.items()):
            print(f"  {d:>6} -> {n.tamano}B")

# --------- Menú interactivo ---------

def leer_int(mensaje, minimo=None, maximo=None):
    while True:
        try:
            val = int(input(mensaje).strip())
            if minimo is not None and val < minimo:
                print(f"Debe ser >= {minimo}.")
                continue
            if maximo is not None and val > maximo:
                print(f"Debe ser <= {maximo}.")
                continue
            return val
        except ValueError:
            print("Entrada inválida. Escribe un número entero.")

def es_potencia_de_dos(x:int)->bool:
    return x > 0 and (x & (x-1)) == 0

def menu():
    print("\n=== Buddy System - Menú ===")
    print("1) Asignar bloque (agregar nodo)")
    print("2) Liberar bloque por dirección (eliminar nodo)")
    print("3) Mostrar árbol")
    print("4) Listar bloques asignados")
    print("5) Reiniciar sistema con otro tamaño")
    print("0) Salir")

def crear_sistema():
    while True:
        tam = leer_int("Tamaño total (potencia de 2, p.ej. 64, 256, 1024): ", minimo=1)
        if es_potencia_de_dos(tam):
            return ArbolBuddySystem(tam)
        print("El tamaño debe ser potencia de 2.")

if __name__ == "__main__":
    print("--- Inicializando Sistema Buddy ---")
    buddy = crear_sistema()
    buddy.imprimir_arbol()

    while True:
        menu()
        op = input("Elige una opción: ").strip()

        if op == "1":
            size = leer_int("Tamaño a asignar (bytes): ", minimo=1)
            buddy.asignar(size)
            print()
            buddy.imprimir_arbol()

        elif op == "2":
            if not buddy.nodos_asignados:
                print("No hay bloques asignados para liberar.")
            else:
                buddy.listar_asignados()
                direccion = leer_int("Escribe la dirección a liberar: ", minimo=0)
                buddy.liberar(direccion)
                print()
                buddy.imprimir_arbol()

        elif op == "3":
            buddy.imprimir_arbol()

        elif op == "4":
            buddy.listar_asignados()

        elif op == "5":
            print("Reiniciando sistema...")
            buddy = crear_sistema()
            buddy.imprimir_arbol()

        elif op == "0":
            print("Saliendo. ¡Hasta luego!")
            break

        else:
            print("Opción no válida.")
