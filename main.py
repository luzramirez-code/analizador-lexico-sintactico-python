"""Programa principal: conecta Lexer y Parser."""

from lexer import analizar_lexico, ErrorLexico
from parser import analizar_sintactico, ErrorSintactico


def procesar_archivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            codigo = archivo.read()

        print(f"\nAnalizando archivo: {ruta}")
        tokens = analizar_lexico(codigo)

        print("\nTOKENS GENERADOS:")
        for token in tokens:
            print(token)

        analizar_sintactico(tokens)
        print("\nRESULTADO: analisis lexico y sintactico correcto.")

    except (ErrorLexico, ErrorSintactico) as error:
        print(f"\nERROR: {error}")
    except OSError as error:
        print(f"No se pudo abrir el archivo: {error}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python main.py ejemplos/nombre_del_ejemplo.py")
    else:
        procesar_archivo(sys.argv[1])
