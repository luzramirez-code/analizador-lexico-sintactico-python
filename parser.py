"""Analizador sintactico descendente recursivo para el subconjunto de Python."""

from lexer import Token


class ErrorSintactico(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def actual(self):
        return self.tokens[self.pos]

    def comprobar(self, *tipos):
        return self.actual().tipo in tipos

    def avanzar(self):
        token = self.actual()
        if token.tipo != "EOF":
            self.pos += 1
        return token

    def esperar(self, tipo):
        if not self.comprobar(tipo):
            t = self.actual()
            raise ErrorSintactico(
                f"Se esperaba {tipo}, se encontro {t.tipo} ({t.valor!r}) "
                f"en linea {t.linea}, columna {t.columna}"
            )
        return self.avanzar()

    def analizar(self):
        self.saltar_newlines()
        while not self.comprobar("EOF"):
            self.sentencia()
            self.saltar_newlines()
        return True

    def saltar_newlines(self):
        while self.comprobar("NEWLINE"):
            self.avanzar()

    def sentencia(self):
        if self.comprobar("DEF"):
            self.definicion_funcion()
        elif self.comprobar("FOR"):
            self.bucle_for()
        else:
            self.sentencia_simple()
            self.esperar("NEWLINE")

    def definicion_funcion(self):
        self.esperar("DEF")
        self.esperar("IDENT")
        self.esperar("LPAREN")
        if not self.comprobar("RPAREN"):
            self.lista_identificadores()
        self.esperar("RPAREN")
        self.esperar("COLON")
        self.esperar("NEWLINE")
        self.bloque()

    def lista_identificadores(self):
        self.esperar("IDENT")
        while self.comprobar("COMMA"):
            self.avanzar()
            self.esperar("IDENT")

    def bucle_for(self):
        self.esperar("FOR")
        self.lista_identificadores()
        self.esperar("IN")
        self.lista_expresiones()
        self.esperar("COLON")
        self.esperar("NEWLINE")
        self.bloque()

        if self.comprobar("ELSE"):
            self.avanzar()
            self.esperar("COLON")
            self.esperar("NEWLINE")
            self.bloque()

    def bloque(self):
        self.esperar("INDENT")
        self.saltar_newlines()
        if self.comprobar("DEDENT"):
            raise ErrorSintactico("El bloque no puede estar vacio en este subconjunto")
        while not self.comprobar("DEDENT", "EOF"):
            self.sentencia()
            self.saltar_newlines()
        self.esperar("DEDENT")

    def sentencia_simple(self):
        if self.comprobar("RETURN"):
            self.avanzar()
            if not self.comprobar("NEWLINE"):
                self.expresion()
        elif self.comprobar("PASS"):
            self.avanzar()
        elif self.comprobar("IDENT"):
            self.avanzar()
            if self.comprobar("ASSIGN"):
                self.avanzar()
                self.expresion()
            elif self.comprobar("LPAREN"):
                self.llamada_despues_nombre()
            else:
                t = self.actual()
                raise ErrorSintactico(
                    f"Se esperaba asignacion o llamada en linea {t.linea}"
                )
        else:
            self.expresion()

    def llamada_despues_nombre(self):
        self.esperar("LPAREN")
        if not self.comprobar("RPAREN"):
            self.lista_expresiones()
        self.esperar("RPAREN")

    def lista_expresiones(self):
        self.expresion()
        while self.comprobar("COMMA"):
            self.avanzar()
            self.expresion()

    # Precedencia: or < and < not < comparaciones < suma < producto
    def expresion(self):
        self.expresion_or()

    def expresion_or(self):
        self.expresion_and()
        while self.comprobar("OR"):
            self.avanzar()
            self.expresion_and()

    def expresion_and(self):
        self.expresion_not()
        while self.comprobar("AND"):
            self.avanzar()
            self.expresion_not()

    def expresion_not(self):
        if self.comprobar("NOT"):
            self.avanzar()
            self.expresion_not()
        else:
            self.comparacion()

    def comparacion(self):
        self.suma()
        if self.comprobar("EQ", "NE", "LT", "GT", "LE", "GE"):
            self.avanzar()
            self.suma()

    def suma(self):
        self.producto()
        while self.comprobar("PLUS", "MINUS"):
            self.avanzar()
            self.producto()

    def producto(self):
        self.factor()
        while self.comprobar("STAR", "SLASH", "PERCENT"):
            self.avanzar()
            self.factor()

    def factor(self):
        if self.comprobar("IDENT", "INT", "FLOAT", "STRING", "TRUE", "FALSE"):
            self.avanzar()
        elif self.comprobar("LPAREN"):
            self.avanzar()
            self.expresion()
            self.esperar("RPAREN")
        else:
            t = self.actual()
            raise ErrorSintactico(
                f"Expresion invalida: {t.tipo} ({t.valor!r}) "
                f"en linea {t.linea}, columna {t.columna}"
            )


def analizar_sintactico(tokens):
    return Parser(tokens).analizar()
