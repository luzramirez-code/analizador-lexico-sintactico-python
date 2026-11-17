from dataclasses import dataclass
import re


# 1. ANALIZADOR LEXICO

@dataclass
class Token:
    tipo: str
    valor: str
    linea: int

    def __str__(self):
        return f"Token({self.tipo}, {self.valor!r}, linea={self.linea})"


class ErrorLexico(Exception):
    pass


PALABRAS_RESERVADAS = {
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
    "pass": "PASS"
}

OPERADORES = {
    "==": "IGUAL_IGUAL",
    "!=": "DIFERENTE",
    "<=": "MENOR_IGUAL",
    ">=": "MAYOR_IGUAL",
    "=": "ASIGNACION",
    "<": "MENOR",
    ">": "MAYOR",
    "+": "SUMA",
    "-": "RESTA",
    "*": "MULTIPLICACION",
    "/": "DIVISION"
}

DELIMITADORES = {
    "(": "PARENTESIS_ABRE",
    ")": "PARENTESIS_CIERRA",
    ":": "DOS_PUNTOS",
    ",": "COMA"
}


def analizar_lexico(codigo):
    tokens = []
    pila_indentacion = [0]
    lineas = codigo.splitlines()

    for numero_linea, linea in enumerate(lineas, start=1):

        if not linea.strip() or linea.lstrip().startswith("#"):
            continue

        espacios = len(linea) - len(linea.lstrip(" "))

        if "\t" in linea[:espacios]:
            raise ErrorLexico(
                f"Tabulacion no permitida en linea {numero_linea}"
            )

        if espacios > pila_indentacion[-1]:
            pila_indentacion.append(espacios)
            tokens.append(Token("INDENT", espacios, numero_linea))

        elif espacios < pila_indentacion[-1]:

            while espacios < pila_indentacion[-1]:
                pila_indentacion.pop()
                tokens.append(Token("DEDENT", "", numero_linea))

            if espacios != pila_indentacion[-1]:
                raise ErrorLexico(
                    f"Indentacion inconsistente en linea {numero_linea}"
                )

        texto = linea.strip()
        posicion = 0

        patron = re.compile(
            r'"[^"]*"|\'[^\']*\'|'
            r'\d+\.\d+|\d+|'
            r'[a-zA-Z_][a-zA-Z_0-9]*|'
            r'==|!=|<=|>=|'
            r'[=<>+\-*/(),:]'
        )

        while posicion < len(texto):

            if texto[posicion].isspace():
                posicion += 1
                continue

            coincidencia = patron.match(texto, posicion)

            if not coincidencia:
                raise ErrorLexico(
                    f"Caracter no reconocido "
                    f"'{texto[posicion]}' en linea {numero_linea}"
                )

            valor = coincidencia.group(0)

            if valor in PALABRAS_RESERVADAS:
                tipo = PALABRAS_RESERVADAS[valor]

            elif valor in OPERADORES:
                tipo = OPERADORES[valor]

            elif valor in DELIMITADORES:
                tipo = DELIMITADORES[valor]

            elif valor.startswith(("'", '"')):
                tipo = "CADENA"

            elif re.fullmatch(r'\d+\.\d+', valor):
                tipo = "REAL"

            elif valor.isdigit():
                tipo = "ENTERO"

            elif re.fullmatch(r'[a-zA-Z_][a-zA-Z_0-9]*', valor):
                tipo = "IDENTIFICADOR"

            else:
                raise ErrorLexico(
                    f"Token no reconocido: {valor}"
                )

            tokens.append(Token(tipo, valor, numero_linea))
            posicion = coincidencia.end()

        tokens.append(Token("NEWLINE", "\\n", numero_linea))

    while len(pila_indentacion) > 1:
        pila_indentacion.pop()
        tokens.append(Token("DEDENT", "", len(lineas)))

    tokens.append(Token("EOF", "", len(lineas)))

    return tokens


# 2. ANALIZADOR SINTACTICO

class ErrorSintactico(Exception):
    pass


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0

    def actual(self):
        return self.tokens[self.posicion]

    def avanzar(self):
        token = self.actual()
        self.posicion += 1
        return token

    def aceptar(self, tipo):
        if self.actual().tipo == tipo:
            return self.avanzar()
        return None

    def esperar(self, tipo):
        token = self.aceptar(tipo)

        if token is None:
            actual = self.actual()
            raise ErrorSintactico(
                f"Se esperaba {tipo}, pero se encontro "
                f"{actual.tipo} ({actual.valor!r}) "
                f"en linea {actual.linea}"
            )

        return token

    def saltar_newline(self):
        while self.aceptar("NEWLINE"):
            pass

    # PROGRAMA

    def analizar(self):
        self.saltar_newline()

        while self.actual().tipo != "EOF":
            self.sentencia()
            self.saltar_newline()

        print("Analisis sintactico finalizado correctamente.")

    # SENTENCIAS

    def sentencia(self):

        if self.actual().tipo == "DEF":
            self.definicion_funcion()

        elif self.actual().tipo == "FOR":
            self.bucle_for()

        elif self.actual().tipo == "IDENTIFICADOR":
            self.sentencia_simple()

        else:
            token = self.actual()
            raise ErrorSintactico(
                f"Sentencia inesperada en linea {token.linea}: "
                f"{token.valor}"
            )

    def sentencia_simple(self):

        nombre = self.esperar("IDENTIFICADOR")

        if self.aceptar("ASIGNACION"):
            self.expresion()
            self.esperar("NEWLINE")

        elif self.aceptar("PARENTESIS_ABRE"):

            if self.actual().tipo != "PARENTESIS_CIERRA":
                self.lista_argumentos()

            self.esperar("PARENTESIS_CIERRA")
            self.esperar("NEWLINE")

        else:
            raise ErrorSintactico(
                f"Se esperaba asignacion o llamada "
                f"despues de {nombre.valor}"
            )

    # DEFINICION DE FUNCIONES

    def definicion_funcion(self):

        self.esperar("DEF")
        self.esperar("IDENTIFICADOR")
        self.esperar("PARENTESIS_ABRE")

        if self.actual().tipo == "IDENTIFICADOR":
            self.lista_parametros()

        self.esperar("PARENTESIS_CIERRA")
        self.esperar("DOS_PUNTOS")
        self.esperar("NEWLINE")

        self.bloque()

    def lista_parametros(self):

        self.esperar("IDENTIFICADOR")

        while self.aceptar("COMA"):
            self.esperar("IDENTIFICADOR")

    # BUCLE FOR

    def bucle_for(self):

        self.esperar("FOR")
        self.esperar("IDENTIFICADOR")
        self.esperar("IN")

        self.lista_expresiones()

        self.esperar("DOS_PUNTOS")
        self.esperar("NEWLINE")

        self.bloque()

        if self.aceptar("ELSE"):
            self.esperar("DOS_PUNTOS")
            self.esperar("NEWLINE")
            self.bloque()

    def lista_expresiones(self):

        self.expresion()

        while self.aceptar("COMA"):
            self.expresion()

    # BLOQUES DE CODIGO

    def bloque(self):

        self.esperar("INDENT")
        self.saltar_newline()

        while self.actual().tipo not in ("DEDENT", "EOF"):
            self.sentencia()
            self.saltar_newline()

        self.esperar("DEDENT")

    # EXPRESIONES Y PRECEDENCIA

    def expresion(self):
        self.expresion_or()

    def expresion_or(self):
        self.expresion_and()

        while self.aceptar("OR"):
            self.expresion_and()

    def expresion_and(self):
        self.expresion_not()

        while self.aceptar("AND"):
            self.expresion_not()

    def expresion_not(self):

        if self.aceptar("NOT"):
            self.expresion_not()
        else:
            self.comparacion()

    def comparacion(self):

        self.expresion_aritmetica()

        comparadores = (
            "IGUAL_IGUAL", "DIFERENTE",
            "MENOR", "MAYOR",
            "MENOR_IGUAL", "MAYOR_IGUAL"
        )

        while self.actual().tipo in comparadores:
            self.avanzar()
            self.expresion_aritmetica()

    def expresion_aritmetica(self):

        self.termino()

        while self.actual().tipo in ("SUMA", "RESTA"):
            self.avanzar()
            self.termino()

    def termino(self):

        self.factor()

        while self.actual().tipo in (
            "MULTIPLICACION", "DIVISION"
        ):
            self.avanzar()
            self.factor()

    def factor(self):

        if self.actual().tipo in (
            "IDENTIFICADOR",
            "ENTERO",
            "REAL",
            "CADENA",
            "TRUE",
            "FALSE"
        ):
            self.avanzar()

        elif self.aceptar("PARENTESIS_ABRE"):
            self.expresion()
            self.esperar("PARENTESIS_CIERRA")

        else:
            token = self.actual()
            raise ErrorSintactico(
                f"Expresion no valida en linea {token.linea}: "
                f"{token.valor!r}"
            )

    def lista_argumentos(self):

        self.expresion()

        while self.aceptar("COMA"):
            self.expresion()


def analizar_sintactico(tokens):
    parser = Parser(tokens)
    parser.analizar()


# 3. CODIGOS DE PRUEBA

EJEMPLOS = {

    "logicas": """
mayor = edad >= 18
activo = True
puede_entrar = mayor and activo
resultado = not (False or mayor)
""",

    "funciones": """
def calcular_promedio(nota1, nota2, nota3):
    suma = nota1 + nota2 + nota3
    promedio = suma / 3
    return promedio
""",

    "for": """
for numero in 1, 2, 3, 4:
    mostrar(numero)
else:
    mostrar("Fin del recorrido")
"""
}


# ============================================================
# 4. PROGRAMA PRINCIPAL
# ============================================================

def ejecutar_analisis(codigo):

    print("=" * 55)
    print("CODIGO FUENTE")
    print("=" * 55)
    print(codigo)

    try:

        # Analisis lexico
        tokens = analizar_lexico(codigo)

        print("\n" + "=" * 55)
        print("TOKENS GENERADOS")
        print("=" * 55)

        for token in tokens:
            print(token)

        print("\nAnalisis lexico correcto.")

        # Analisis sintactico
        print("\n" + "=" * 55)
        print("ANALISIS SINTACTICO")
        print("=" * 55)

        analizar_sintactico(tokens)

        print("\nRESULTADO FINAL:")
        print("El codigo cumple con la gramatica implementada.")

    except ErrorLexico as error:
        print("\nERROR LEXICO:")
        print(error)

    except ErrorSintactico as error:
        print("\nERROR SINTACTICO:")
        print(error)


# Cambiar entre: "logicas", "funciones" o "for"
EJEMPLO = "logicas"


if __name__ == "__main__":
    ejecutar_analisis(EJEMPLOS[EJEMPLO])
