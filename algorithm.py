# Para simular la estructura de los bloques de memoria, podemos usar una clase.
class Block:
    def __init__(self, id, size, is_free=True):
        self.id = id
        self.size = size
        self.is_free = is_free
        self.children = []

    def __repr__(self):
        # Esto ayuda a que la impresión del objeto sea más legible.
        return f"Block(id={self.id}, size={self.size}KB, is_free={self.is_free})"

def get_required_block_size(size):
    """
    Calcula la menor potencia de 2 que es mayor o igual al tamaño solicitado.
    Esto determina el tamaño del bloque que el sistema necesita encontrar.
    
    :param size: El tamaño solicitado en KB (int).
    :return: El tamaño del bloque requerido, una potencia de 2 (int).
    """
    if size <= 0:
        return 0
    
    power_of_2 = 1
    while power_of_2 < size:
        power_of_2 *= 2
        
    return power_of_2

def find_best_fit_block(required_size, memory_blocks):
    """
    Encuentra el bloque libre más pequeño que puede satisfacer la solicitud (Best-Fit).
    Itera a través de todos los bloques de memoria existentes.
    
    :param required_size: El tamaño del bloque necesario (calculado por get_required_block_size).
    :param memory_blocks: Un diccionario que contiene todos los bloques de memoria.
    :return: El objeto del bloque encontrado o None si no hay espacio.
    """
    best_fit = None
    
    # Itera sobre todos los bloques de memoria actuales.
    for block in memory_blocks.values():
        
        # Un bloque es candidato si cumple tres condiciones:
        # 1. Está libre (block.is_free).
        # 2. Es una "hoja" en el árbol, es decir, no ha sido dividido (not block.children).
        # 3. Su tamaño es suficiente para la solicitud (block.size >= required_size).
        if block.is_free and not block.children and block.size >= required_size:
            
            # Si es el primer bloque candidato que encontramos, lo guardamos.
            if best_fit is None:
                best_fit = block
            # Si ya teníamos un candidato, lo reemplazamos solo si el nuevo es más pequeño.
            # Esto asegura que encontremos el bloque que mejor se ajusta, minimizando el desperdicio.
            elif block.size < best_fit.size:
                best_fit = block
                
    # Devuelve el mejor bloque encontrado o None si ninguno cumplió las condiciones.
    return best_fit

# --- Ejemplo de uso ---
if __name__ == "__main__":
    # 1. Creamos un diccionario para simular el estado de la memoria.
    #    Imaginemos que la memoria ya ha sido dividida en varios bloques.
    memory_blocks = {
        1: Block(id=1, size=128, is_free=False), # Ocupado
        2: Block(id=2, size=64, is_free=True),   # Libre
        3: Block(id=3, size=256, is_free=True),  # Libre
        4: Block(id=4, size=64, is_free=True),   # Libre pero del mismo tamaño que el bloque 2
        5: Block(id=5, size=512, is_free=True)   # Libre pero muy grande
    }
    
    # 2. Definimos el tamaño del proceso que queremos asignar.
    process_size_kb = 50
    print(f"Buscando espacio para un proceso de {process_size_kb} KB...")
    
    # 3. Calculamos el tamaño de bloque que necesitamos.
    required_size = get_required_block_size(process_size_kb)
    print(f"Se necesita un bloque de al menos {required_size} KB.")
    
    # 4. Buscamos el mejor bloque disponible.
    best_block = find_best_fit_block(required_size, memory_blocks)
    
    # 5. Mostramos el resultado.
    if best_block:
        print(f"\nEl mejor bloque encontrado es: {best_block}")
        print("Este bloque es el más pequeño de los disponibles que puede contener el proceso.")
    else:
        print("\nNo se encontró ningún bloque de memoria libre que cumpla con los requisitos.")

