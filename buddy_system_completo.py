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



class BuddySistem:
    def __init__(self, tamano_total):
        
        #Checa si es un exponente de 2 o si es 0
        if not (tamano_total > 0 and (tamano_total & (tamano_total -1) == 0)):
            raise ValueError("El tamaño")
        print 