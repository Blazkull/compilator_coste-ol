class SyntaxErrorCosteñol(Exception):
    """Excepción lanzada cuando hay un error de sintaxis en el código."""
    def __init__(self, message, token):
        super().__init__(message)
        self.token = token
        self.message = message

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
        self.current_token = self.tokens[self.current_index] if self.tokens else None

    def advance(self):
        """Avanza al siguiente token."""
        self.current_index += 1
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]
        else:
            self.current_token = None

    def match(self, expected_type):
        """Si el token actual es del tipo esperado, avanza. Si no, lanza error."""
        if self.current_token and self.current_token.type == expected_type:
            self.advance()
        else:
            actual_type = self.current_token.type if self.current_token else "EOF (Fin de Archivo)"
            val = self.current_token.value if self.current_token else "Nada"
            raise SyntaxErrorCosteñol(
                f"Error Sintáctico: Se esperaba '{expected_type}', pero se encontró '{actual_type}' ('{val}').",
                self.current_token
            )

    def parse(self):
        """Punto de entrada principal para parsear todo el programa."""
        while self.current_token is not None:
            self.parse_statement()

    def parse_statement(self):
        """
        Determina qué tipo de sentencia se va a analizar mirando el token actual.
        Puede ser:
        - Comando IO (Mensaje)
        - Identificador (Declaración, Asignación normal o Captura)
        """
        if self.current_token.type == 'COMANDO_IO':
            if self.current_token.value == 'Mensaje':
                self.parse_mensaje()
            else:
                # Si empieza con Captura directamente, es error, porque Captura debe asignarse a algo.
                raise SyntaxErrorCosteñol(
                    "Error Sintáctico: El comando 'Captura' debe ser asignado a una variable.",
                    self.current_token
                )

        elif self.current_token.type == 'IDENTIFICADOR':
            # Miramos el SIGUIENTE token (lookahead) para saber si es declaración o asignación
            next_idx = self.current_index + 1
            if next_idx < len(self.tokens):
                next_token = self.tokens[next_idx]
                if next_token.type == 'TIPO_DATO':
                    self.parse_declaracion()
                elif next_token.type == 'OPERADOR_ASIGNACION':
                    self.parse_asignacion_o_captura()
                else:
                    raise SyntaxErrorCosteñol(
                        f"Error Sintáctico: Después del identificador se esperaba un Tipo de Dato o un '='. Se encontró '{next_token.value}'.",
                        next_token
                    )
            else:
                raise SyntaxErrorCosteñol(
                    "Error Sintáctico: Sentencia incompleta después del identificador.",
                    self.current_token
                )
        else:
            raise SyntaxErrorCosteñol(
                f"Error Sintáctico: Toda sentencia debe empezar con un Identificador o 'Mensaje'. Se encontró '{self.current_token.value}'.",
                self.current_token
            )

    def parse_declaracion(self):
        """Regla 1: [IDENTIFICADOR] [TIPO_DATO] [DELIMITADOR_FIN]"""
        self.match('IDENTIFICADOR')
        self.match('TIPO_DATO')
        self.match('DELIMITADOR_FIN')

    def parse_asignacion_o_captura(self):
        """
        Regla 2 y 3:
        Asignación matemática: [IDENTIFICADOR] [OPERADOR_ASIGNACION] [EXPRESION] [DELIMITADOR_FIN]
        Captura: [IDENTIFICADOR] [OPERADOR_ASIGNACION] [COMANDO_IO] [SEPARADOR] [TIPO_DATO] [PARENTESIS_ABRE] [PARENTESIS_CIERRA] [DELIMITADOR_FIN]
        """
        self.match('IDENTIFICADOR')
        self.match('OPERADOR_ASIGNACION')
        
        # Lookahead para ver si es Captura o una expresión normal
        if self.current_token and self.current_token.type == 'COMANDO_IO' and self.current_token.value == 'Captura':
            self.parse_captura_tail()
        else:
            self.parse_expresion()
            self.match('DELIMITADOR_FIN')

    def parse_captura_tail(self):
        """Lo que sigue después del '=' cuando se hace una Captura."""
        self.match('COMANDO_IO') # Captura
        self.match('SEPARADOR') # .
        self.match('TIPO_DATO') # Entero, Texto, etc
        self.match('PARENTESIS_ABRE') # (
        self.match('PARENTESIS_CIERRA') # )
        self.match('DELIMITADOR_FIN') # ;

    def parse_mensaje(self):
        """Regla 4: [COMANDO_IO] [SEPARADOR] [TIPO_DATO] [PARENTESIS_ABRE] [CADENA_TEXTO/IDENTIFICADOR] [PARENTESIS_CIERRA] [DELIMITADOR_FIN]"""
        self.match('COMANDO_IO')
        self.match('SEPARADOR')
        self.match('TIPO_DATO')
        self.match('PARENTESIS_ABRE')
        
        # Permitimos imprimir tanto un string literal como una variable
        if self.current_token and self.current_token.type == 'CADENA_TEXTO':
            self.match('CADENA_TEXTO')
        elif self.current_token and self.current_token.type == 'IDENTIFICADOR':
            self.match('IDENTIFICADOR')
        else:
            raise SyntaxErrorCosteñol(
                "Error Sintáctico: El Mensaje debe contener una Cadena de Texto o un Identificador.",
                self.current_token
            )
            
        self.match('PARENTESIS_CIERRA')
        self.match('DELIMITADOR_FIN')

    def parse_expresion(self):
        """
        Parsea expresiones matemáticas simples.
        Una expresión tiene al menos un 'termino', seguido de opcionalmente operadores y otros terminos.
        """
        self.parse_termino()
        
        while self.current_token and self.current_token.type == 'OPERADOR_ARITMETICO':
            self.match('OPERADOR_ARITMETICO')
            self.parse_termino()

    def parse_termino(self):
        """
        Un término puede ser un número (entero/real), un identificador (variable), un string, o una sub-expresión entre paréntesis.
        """
        if not self.current_token:
            raise SyntaxErrorCosteñol("Error Sintáctico: Expresión incompleta, se llegó al fin del archivo.", None)
            
        if self.current_token.type == 'NUMERO_ENTERO':
            self.match('NUMERO_ENTERO')
        elif self.current_token.type == 'NUMERO_REAL':
            self.match('NUMERO_REAL')
        elif self.current_token.type == 'CADENA_TEXTO':
            self.match('CADENA_TEXTO')
        elif self.current_token.type == 'IDENTIFICADOR':
            self.match('IDENTIFICADOR')
        elif self.current_token.type == 'PARENTESIS_ABRE':
            self.match('PARENTESIS_ABRE')
            self.parse_expresion()
            self.match('PARENTESIS_CIERRA')
        else:
            raise SyntaxErrorCosteñol(
                f"Error Sintáctico: Se esperaba un número, identificador o cadena en la expresión. Se encontró '{self.current_token.value}'.",
                self.current_token
            )
