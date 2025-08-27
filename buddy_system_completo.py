# SIMULADOR COMPLETO DEL BUDDY SYSTEM EN PYTHON
# =============================================
# Este código implementa el Buddy System completo como el HTML pero en consola
# con explicaciones muy detalladas de cada paso

import time

class Block:
    def __init__(self, id, size, is_free=True, process_id=None, parent_id=None, requested_size=None):
        self.id = id
        self.size = size
        self.is_free = is_free
        self.process_id = process_id
        self.parent_id = parent_id
        self.children = []
        self.requested_size = requested_size

    def __repr__(self):
        if self.is_free:
            return f"Bloque {self.id}: {self.size} KB (Libre)"
        else:
            return f"Bloque {self.id}: {self.size} KB (Proceso {self.process_id}, {self.requested_size} KB)"

class BuddySystem:
    def __init__(self, total_memory=1024):
        self.total_memory = total_memory
        self.memory_blocks = {}
        self.next_block_id = 1
        self.next_process_id = 1
        self.initialize_memory()
    
    def initialize_memory(self):
        """Inicializa la memoria con un solo bloque grande"""
        print("🔄 INICIALIZANDO EL SISTEMA BUDDY...")
        print(f"   Memoria total: {self.total_memory} KB")
        
        # Crear el bloque raíz (todo el espacio de memoria)
        root_block = Block(
            id=self.next_block_id,
            size=self.total_memory,
            is_free=True,
            parent_id=None
        )
        
        self.memory_blocks[root_block.id] = root_block
        self.next_block_id += 1
        
        print(f"   ✓ Bloque raíz creado: {root_block}")
        print("   ✓ Sistema listo para asignar memoria\n")
    
    def get_required_block_size(self, size):
        """Calcula la potencia de 2 más pequeña que sea >= al tamaño solicitado"""
        if size <= 0:
            return 0
        
        power_of_2 = 1
        while power_of_2 < size:
            power_of_2 *= 2
            
        return power_of_2
    
    def find_best_fit_block(self, required_size):
        """Encuentra el mejor bloque disponible (más pequeño que pueda contener el proceso)"""
        print(f"🔍 BUSCANDO EL MEJOR BLOQUE PARA {required_size} KB...")
        
        best_fit = None
        candidates = []
        
        # Revisar todos los bloques disponibles
        for block_id, block in self.memory_blocks.items():
            if block.is_free and len(block.children) == 0 and block.size >= required_size:
                candidates.append(block)
                print(f"   ✓ Candidato: {block}")
                
                if best_fit is None or block.size < best_fit.size:
                    best_fit = block
                    print(f"      → Nuevo mejor candidato!")
        
        if best_fit:
            print(f"   🎯 MEJOR BLOQUE ENCONTRADO: {best_fit}")
        else:
            print(f"   ❌ No se encontró ningún bloque adecuado")
        
        return best_fit
    
    def split_block(self, block_to_split, required_size):
        """Divide un bloque en dos bloques hijos"""
        print(f"\n✂️  DIVIDIENDO BLOQUE {block_to_split.id} ({block_to_split.size} KB)...")
        
        new_size = block_to_split.size // 2
        print(f"   Tamaño de cada hijo: {new_size} KB")
        
        # Crear el hijo izquierdo
        left_child = Block(
            id=self.next_block_id,
            size=new_size,
            is_free=True,
            parent_id=block_to_split.id
        )
        self.next_block_id += 1
        
        # Crear el hijo derecho
        right_child = Block(
            id=self.next_block_id,
            size=new_size,
            is_free=True,
            parent_id=block_to_split.id
        )
        self.next_block_id += 1
        
        # Actualizar el bloque padre
        block_to_split.children = [left_child.id, right_child.id]
        block_to_split.is_free = False  # Ya no es una hoja
        
        # Agregar los hijos al diccionario
        self.memory_blocks[left_child.id] = left_child
        self.memory_blocks[right_child.id] = right_child
        
        print(f"   ✓ Hijo izquierdo creado: {left_child}")
        print(f"   ✓ Hijo derecho creado: {right_child}")
        print(f"   ✓ Bloque padre actualizado: {block_to_split}")
        
        return left_child, right_child
    
    def allocate_memory(self, requested_size):
        """Asigna memoria para un proceso"""
        print(f"\n🚀 SOLICITUD DE ASIGNACIÓN: {requested_size} KB")
        print("=" * 50)
        
        # Paso 1: Validar la solicitud
        if requested_size <= 0:
            print("❌ Error: El tamaño debe ser positivo")
            return None
        
        if requested_size > self.total_memory:
            print(f"❌ Error: El tamaño ({requested_size} KB) excede la memoria total ({self.total_memory} KB)")
            return None
        
        # Paso 2: Calcular el tamaño de bloque necesario
        required_size = self.get_required_block_size(requested_size)
        print(f"📏 CÁLCULO DE TAMAÑO:")
        print(f"   Proceso solicitado: {requested_size} KB")
        print(f"   Potencia de 2 necesaria: {required_size} KB")
        
        if required_size != requested_size:
            print(f"   ⚠️  Fragmentación interna: {required_size - requested_size} KB desperdiciados")
        
        # Paso 3: Buscar el mejor bloque
        block_to_split = self.find_best_fit_block(required_size)
        
        if not block_to_split:
            print("❌ No hay suficiente memoria disponible")
            return None
        
        # Paso 4: Dividir bloques si es necesario
        final_block_id = block_to_split.id
        
        if block_to_split.size > required_size:
            print(f"\n🔄 DIVISIÓN DE BLOQUES NECESARIA...")
            current_block = block_to_split
            
            while current_block.size // 2 >= required_size:
                print(f"\n   📊 Estado actual: Bloque {current_block.id} ({current_block.size} KB)")
                print(f"   🎯 Necesitamos: {required_size} KB")
                print(f"   ➗ Podemos dividir: {current_block.size} → {current_block.size // 2} + {current_block.size // 2}")
                
                left_child, right_child = self.split_block(current_block, required_size)
                
                # Continuar con el hijo izquierdo
                current_block = left_child
                final_block_id = current_block.id
                
                time.sleep(0.5)  # Pausa para visualizar el proceso
        
        # Paso 5: Asignar el proceso
        print(f"\n✅ ASIGNANDO PROCESO...")
        block_to_allocate = self.memory_blocks[final_block_id]
        block_to_allocate.is_free = False
        block_to_allocate.process_id = f"P{self.next_process_id}"
        block_to_allocate.requested_size = requested_size
        
        print(f"   ✓ Proceso {block_to_allocate.process_id} asignado")
        print(f"   ✓ Bloque: {block_to_allocate}")
        
        self.next_process_id += 1
        
        # Paso 6: Mostrar estado final
        self.show_memory_state()
        
        return block_to_allocate
    
    def deallocate_memory(self, block_id):
        """Libera memoria de un proceso"""
        print(f"\n🗑️  LIBERANDO MEMORIA...")
        
        block = self.memory_blocks.get(block_id)
        if not block:
            print(f"❌ Bloque {block_id} no encontrado")
            return
        
        if block.is_free:
            print(f"❌ Bloque {block_id} ya está libre")
            return
        
        print(f"   Liberando: {block}")
        
        # Marcar como libre
        block.is_free = True
        block.process_id = None
        block.requested_size = None
        
        print(f"   ✓ Bloque marcado como libre")
        
        # Intentar fusionar con el hermano
        self.try_merge_with_buddy(block.parent_id)
        
        self.show_memory_state()
    
    def try_merge_with_buddy(self, parent_id):
        """Intenta fusionar dos bloques hermanos si ambos están libres"""
        if parent_id is None:
            return
        
        parent = self.memory_blocks.get(parent_id)
        if not parent or len(parent.children) == 0:
            return
        
        left_child_id = parent.children[0]
        right_child_id = parent.children[1]
        
        left_child = self.memory_blocks.get(left_child_id)
        right_child = self.memory_blocks.get(right_child_id)
        
        if left_child and right_child and left_child.is_free and right_child.is_free:
            print(f"\n🔗 FUSIONANDO BLOQUES HERMANOS...")
            print(f"   Bloque izquierdo: {left_child}")
            print(f"   Bloque derecho: {right_child}")
            
            # Eliminar los hijos
            del self.memory_blocks[left_child_id]
            del self.memory_blocks[right_child_id]
            
            # Restaurar el padre
            parent.children = []
            parent.is_free = True
            
            print(f"   ✓ Fusionados en: {parent}")
            
            # Intentar fusionar recursivamente
            self.try_merge_with_buddy(parent.parent_id)
    
    def show_memory_state(self):
        """Muestra el estado actual de la memoria"""
        print(f"\n📊 ESTADO ACTUAL DE LA MEMORIA:")
        print("-" * 40)
        
        # Mostrar bloques en orden jerárquico
        self._show_block_tree(self._find_root_block())
        
        # Calcular estadísticas
        total_allocated = sum(1 for block in self.memory_blocks.values() if not block.is_free)
        total_free = sum(1 for block in self.memory_blocks.values() if block.is_free)
        
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   Bloques totales: {len(self.memory_blocks)}")
        print(f"   Bloques ocupados: {total_allocated}")
        print(f"   Bloques libres: {total_free}")
    
    def _find_root_block(self):
        """Encuentra el bloque raíz"""
        for block in self.memory_blocks.values():
            if block.parent_id is None:
                return block
        return None
    
    def _show_block_tree(self, block, level=0):
        """Muestra el árbol de bloques de forma jerárquica"""
        if not block:
            return
        
        indent = "  " * level
        if block.is_free:
            print(f"{indent}🟢 {block}")
        else:
            print(f"{indent}🔴 {block}")
        
        # Mostrar hijos
        for child_id in block.children:
            child = self.memory_blocks.get(child_id)
            if child:
                self._show_block_tree(child, level + 1)

def main():
    """Función principal con ejemplos interactivos"""
    print("🎯 SIMULADOR COMPLETO DEL BUDDY SYSTEM")
    print("=" * 50)
    
    # Crear el sistema
    buddy_system = BuddySystem(total_memory=1024)
    
    # Ejemplo 1: Proceso pequeño
    print("\n" + "="*60)
    print("📝 EJEMPLO 1: Proceso pequeño (50 KB)")
    print("="*60)
    buddy_system.allocate_memory(50)
    
    # Ejemplo 2: Proceso mediano
    print("\n" + "="*60)
    print("📝 EJEMPLO 2: Proceso mediano (200 KB)")
    print("="*60)
    buddy_system.allocate_memory(200)
    
    # Ejemplo 3: Proceso grande
    print("\n" + "="*60)
    print("📝 EJEMPLO 3: Proceso grande (400 KB)")
    print("="*60)
    buddy_system.allocate_memory(400)
    
    # Ejemplo 4: Liberar memoria
    print("\n" + "="*60)
    print("📝 EJEMPLO 4: Liberar proceso P1")
    print("="*60)
    buddy_system.deallocate_memory(1)  # Liberar el primer proceso
    
    print("\n🎉 SIMULACIÓN COMPLETADA!")
    print("Este simulador muestra cómo funciona el Buddy System real:")
    print("1. Divide bloques dinámicamente")
    print("2. Busca el mejor ajuste")
    print("3. Fusiona bloques cuando se liberan")
    print("4. Minimiza la fragmentación externa")

if __name__ == "__main__":
    main()
