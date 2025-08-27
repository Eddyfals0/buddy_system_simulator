# Simulador de Buddy System

Un simulador interactivo del algoritmo de gestión de memoria Buddy System implementado en JavaScript y HTML.

## Características

- **Simulación Visual**: Representación gráfica del árbol de bloques de memoria
- **Algoritmo Best-Fit**: Implementación del algoritmo de mejor ajuste
- **Interfaz Interactiva**: Permite asignar y liberar memoria de forma dinámica
- **Animaciones**: Transiciones suaves para división y fusión de bloques
- **Registro de Eventos**: Log detallado de todas las operaciones

## Cómo usar

1. Abre `index.html` en tu navegador
2. Ingresa el tamaño del proceso en KB
3. Haz clic en "Asignar Memoria" para reservar espacio
4. Usa el botón "Liberar" en los bloques asignados para liberar memoria
5. El botón "Reiniciar" limpia toda la memoria

## Algoritmo Implementado

El simulador implementa el **Buddy System** con las siguientes características:

- **División Binaria**: Los bloques se dividen en potencias de 2
- **Best-Fit**: Se selecciona el bloque libre más pequeño que puede contener el proceso
- **Fusión Automática**: Los bloques hermanos libres se fusionan automáticamente

## Archivos del Proyecto

- `index.html` - Página principal del simulador
- `algorithm.py` - Implementación del algoritmo en Python (para referencia)
- `admi_algorithm.html` - Documentación del algoritmo en JavaScript

## Tecnologías Utilizadas

- HTML5
- CSS3 (Tailwind CSS)
- JavaScript (ES6+)
- Python (para la implementación de referencia)

## Autor

Desarrollado como proyecto académico para Sistemas Operativos 2.

