# Analizador léxico y sintáctico de un subconjunto de Python

**Asignatura:** Diseño de Compiladores - INF 3631  
**Estudiante:** Univ. Luz Belén Ramírez Apaza  
**Gestión:** II/2026

## Descripción
Proyecto demostrativo que implementa un analizador léxico (Lexer) y un analizador sintáctico (Parser) para un subconjunto didáctico de Python, basado en tres estructuras:

1. Expresiones lógicas: `and`, `or`, `not`, `True`, `False` y comparaciones.
2. Definición de funciones: `def`, parámetros y bloque indentado.
3. Bucle `for`: variables de destino, `in`, secuencia, bloque y `else` opcional.

No es un compilador completo de Python. La implementación reconoce únicamente las construcciones documentadas.

## Archivos
- `lexer.py`: reconoce lexemas y genera tokens, incluidos `INDENT`, `DEDENT` y `NEWLINE`.
- `parser.py`: valida la estructura de los tokens mediante descenso recursivo.
- `main.py`: conecta Lexer y Parser.
- `ejemplos/`: programas de prueba.

## Requisitos
Python 3.10 o superior. No requiere instalar paquetes externos.

## Ejecución
Desde la carpeta raíz del proyecto:

```bash
python main.py ejemplos/expresiones_logicas.py
python main.py ejemplos/funciones.py
python main.py ejemplos/bucle_for.py
```

El programa imprime los tokens y comunica si el análisis léxico y sintáctico fue correcto.

## Alcance y limitaciones
- Se reconocen bloques mediante indentación con espacios; no se admiten tabulaciones para indentar.
- Se admiten asignaciones simples, llamadas, `return`, `pass`, expresiones lógicas, comparaciones y operaciones aritméticas.
- La lista de expresiones del `for` se limita a expresiones separadas por comas; no implementa toda la sintaxis de iterables de Python.
- No se implementan clases, decoradores, imports, comprensiones, argumentos por defecto, anotaciones de tipos ni todas las reglas del lenguaje Python.
- El `else` del `for` se reconoce sintácticamente; este proyecto no ejecuta el programa.

## Autor
Univ. Luz Belén Ramírez Apaza
