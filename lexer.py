"""Analizador lexico para un subconjunto didactico de Python.

Reconoce:
- Palabras reservadas: def, for, in, else, and, or, not, True, False, return, pass
- Identificadores, enteros, reales y cadenas
- Operadores y delimitadores
- INDENT, DEDENT y NEWLINE para representar bloques por indentacion

No pretende implementar todo el lenguaje Python.
"""

import re
from dataclasses import dataclass


@dataclass
class Token:
    tipo: str
    valor: str
    linea: int
    columna: int

    def __repr__(self):
        return f"Token({self.tipo}, {self.valor!r}, linea={self.linea}, columna={self.columna})"


PALABRAS = {
    "def": "DEF",
    "for": "FOR",
    "in": "IN",
    "else": "ELSE",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
    "True": "TRUE",
    "False": "FALSE",
    "return": "RETURN",
    "pass": "PASS",
}

DOS_CARACTERES = {
    "==": "EQ", "!=": "NE", "<=": "LE", ">=": "GE",
}

UN_CARACTER = {
    "+": "PLUS", "-": "MINUS", "*": "STAR", "/": "SLASH",
    "%": "PERCENT", "=": "ASSIGN", "<": "LT", ">": "GT",
    "(": "LPAREN", ")": "RPAREN", "[": "LBRACKET", "]": "RBRACKET",
    ",": "COMMA", ":": "COLON", ".": "DOT",
}


class ErrorLexico(Exception):
    pass


class Lexer:
    def __init__(self, codigo):
        self.codigo = codigo

    def analizar(self):
        tokens = []
        niveles = [0]
        lineas = self.codigo.splitlines()

        for num_linea, linea in enumerate(lineas, start=1):
            if not linea.strip() or linea.lstrip().startswith("#"):
                continue

            prefijo = len(linea) - len(linea.lstrip(" "))
            contenido = linea[prefijo:]

            if "\t" in linea[:prefijo]:
                raise ErrorLexico(
                    f"Tabulacion no permitida para indentacion en linea {num_linea}"
                )

            if prefijo > niveles[-1]:
                niveles.append(prefijo)
                tokens.append(Token("INDENT", "", num_linea, 1))
            else:
                while prefijo < niveles[-1]:
                    niveles.pop()
                    tokens.append(Token("DEDENT", "", num_linea, 1))
                if prefijo != niveles[-1]:
                    raise ErrorLexico(
                        f"Indentacion inconsistente en linea {num_linea}"
                    )

            i = 0
            while i < len(contenido):
                c = contenido[i]

                if c in " \t\r":
                    i += 1
                    continue

                if contenido.startswith("#", i):
                    break

                columna = prefijo + i + 1

                if c in ("'", '"'):
                    comilla = c
                    inicio = i
                    i += 1
                    while i < len(contenido) and contenido[i] != comilla:
                        if contenido[i] == "\\" and i + 1 < len(contenido):
                            i += 2
                        else:
                            i += 1
                    if i >= len(contenido):
                        raise ErrorLexico(
                            f"Cadena sin cerrar en linea {num_linea}, columna {columna}"
                        )
                    i += 1
                    tokens.append(Token("STRING", contenido[inicio:i], num_linea, columna))
                    continue

                if c.isalpha() or c == "_":
                    inicio = i
                    i += 1
                    while i < len(contenido) and (contenido[i].isalnum() or contenido[i] == "_"):
                        i += 1
                    palabra = contenido[inicio:i]
                    tipo = PALABRAS.get(palabra, "IDENT")
                    tokens.append(Token(tipo, palabra, num_linea, columna))
                    continue

                if c.isdigit():
                    inicio = i
                    i += 1
                    while i < len(contenido) and contenido[i].isdigit():
                        i += 1
                    tipo = "INT"
                    if i < len(contenido) and contenido[i] == ".":
                        if i + 1 < len(contenido) and contenido[i + 1].isdigit():
                            tipo = "FLOAT"
                            i += 1
                            while i < len(contenido) and contenido[i].isdigit():
                                i += 1
                    tokens.append(Token(tipo, contenido[inicio:i], num_linea, columna))
                    continue

                par = contenido[i:i + 2]
                if par in DOS_CARACTERES:
                    tokens.append(Token(DOS_CARACTERES[par], par, num_linea, columna))
                    i += 2
                    continue

                if c in UN_CARACTER:
                    tokens.append(Token(UN_CARACTER[c], c, num_linea, columna))
                    i += 1
                    continue

                raise ErrorLexico(
                    f"Caracter no reconocido {c!r} en linea {num_linea}, columna {columna}"
                )

            tokens.append(Token("NEWLINE", "\\n", num_linea, len(linea) + 1))

        while len(niveles) > 1:
            niveles.pop()
            tokens.append(Token("DEDENT", "", len(lineas) or 1, 1))

        tokens.append(Token("EOF", "", len(lineas) + 1, 1))
        return tokens


def analizar_lexico(codigo):
    return Lexer(codigo).analizar()
