from src.semantic.symbol_table import SymbolTable, SemanticErrorCosteñol

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
        self.symtab = SymbolTable()

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
                f"mi llave barros schelotto — Se esperaba '{expected_type}', pero se encontró '{actual_type}' ('{val}').",
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
                    "mi llave barros schelotto — El comando 'Captura' debe ser asignado a una variable.",
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
                        f"mi llave barros schelotto — Después del identificador se esperaba un Tipo de Dato o un '='. Se encontró '{next_token.value}'.",
                        next_token
                    )
            else:
                raise SyntaxErrorCosteñol(
                    "mi llave barros schelotto — Sentencia incompleta después del identificador.",
                    self.current_token
                )
        else:
            raise SyntaxErrorCosteñol(
                f"mi llave barros schelotto — Toda sentencia debe empezar con un Identificador o 'Mensaje'. Se encontró '{self.current_token.value}'.",
                self.current_token
            )

    def parse_declaracion(self):
        """Regla 1: [IDENTIFICADOR] [TIPO_DATO] [DELIMITADOR_FIN]"""
        name_token = self.current_token
        self.match('IDENTIFICADOR')
        type_token = self.current_token
        self.match('TIPO_DATO')
        self.match('DELIMITADOR_FIN')
        
        # Análisis Semántico: Registrar variable
        self.symtab.define(name_token.value, type_token.value, name_token)

    def parse_asignacion_o_captura(self):
        """
        Regla 2 y 3:
        Asignación matemática: [IDENTIFICADOR] [OPERADOR_ASIGNACION] [EXPRESION] [DELIMITADOR_FIN]
        Captura: [IDENTIFICADOR] [OPERADOR_ASIGNACION] [COMANDO_IO] [SEPARADOR] [TIPO_DATO] [PARENTESIS_ABRE] [PARENTESIS_CIERRA] [DELIMITADOR_FIN]
        """
        name_token = self.current_token
        self.match('IDENTIFICADOR')
        
        # Análisis Semántico: Verificar que la variable esté declarada
        var_type = self.symtab.lookup(name_token.value, name_token)
        
        self.match('OPERADOR_ASIGNACION')
        
        # Lookahead para ver si es Captura o una expresión normal
        if self.current_token and self.current_token.type == 'COMANDO_IO' and self.current_token.value == 'Captura':
            self.parse_captura_tail(var_type, name_token)
        else:
            expr_type = self.parse_expresion()
            self.match('DELIMITADOR_FIN')
            
            # Análisis Semántico: Type checking para asignación normal
            if expr_type and expr_type != var_type:
                # Permitir Entero a Real
                if not (var_type == 'Real' and expr_type == 'Entero'):
                    raise SemanticErrorCosteñol(
                        f"Joda loco estas barrilete — No se puede asignar una expresión de tipo '{expr_type}' a la variable '{name_token.value}' de tipo '{var_type}'.",
                        name_token
                    )

    def parse_captura_tail(self, var_type, name_token):
        """Lo que sigue después del '=' cuando se hace una Captura."""
        self.match('COMANDO_IO') # Captura
        self.match('SEPARADOR') # .
        
        captura_type_token = self.current_token
        self.match('TIPO_DATO') # Entero, Texto, etc
        
        # Análisis Semántico: Validar que el tipo de Captura coincida con el tipo de la variable
        if captura_type_token.value != var_type:
            raise SemanticErrorCosteñol(
                f"Joda loco estas barrilete — Se intenta capturar un '{captura_type_token.value}' en la variable '{name_token.value}' que es de tipo '{var_type}'.",
                captura_type_token
            )
            
        self.match('PARENTESIS_ABRE') # (
        self.match('PARENTESIS_CIERRA') # )
        self.match('DELIMITADOR_FIN') # ;

    def parse_mensaje(self):
        """Regla 4: [COMANDO_IO] [SEPARADOR] [TIPO_DATO] [PARENTESIS_ABRE] [CADENA_TEXTO/IDENTIFICADOR] [PARENTESIS_CIERRA] [DELIMITADOR_FIN]"""
        self.match('COMANDO_IO')
        self.match('SEPARADOR')
        
        msg_type_token = self.current_token
        self.match('TIPO_DATO')
        self.match('PARENTESIS_ABRE')
        
        # Permitimos imprimir tanto un string literal como una variable
        if self.current_token and self.current_token.type == 'CADENA_TEXTO':
            # Análisis Semántico: Verificar que si se pasa una cadena, Mensaje sea de Texto
            if msg_type_token.value != 'Texto':
                 raise SemanticErrorCosteñol(
                    f"Joda loco estas barrilete — 'Mensaje.{msg_type_token.value}' no puede imprimir una cadena de Texto directa.",
                    msg_type_token
                )
            self.match('CADENA_TEXTO')
        elif self.current_token and self.current_token.type == 'IDENTIFICADOR':
            id_token = self.current_token
            self.match('IDENTIFICADOR')
            
            # Análisis Semántico: Validar variable y tipo
            var_type = self.symtab.lookup(id_token.value, id_token)
            if var_type != msg_type_token.value:
                raise SemanticErrorCosteñol(
                    f"Joda loco estas barrilete — 'Mensaje.{msg_type_token.value}' no puede imprimir la variable '{id_token.value}' de tipo '{var_type}'.",
                    id_token
                )
        else:
            raise SyntaxErrorCosteñol(
                "mi llave barros schelotto — El Mensaje debe contener una Cadena de Texto o un Identificador.",
                self.current_token
            )
            
        self.match('PARENTESIS_CIERRA')
        self.match('DELIMITADOR_FIN')

    def parse_expresion(self):
        """
        Parsea expresiones matemáticas simples.
        Retorna el tipo de dato inferido de la expresión (ej: 'Entero', 'Real').
        """
        left_type = self.parse_termino()
        
        while self.current_token and self.current_token.type == 'OPERADOR_ARITMETICO':
            op_token = self.current_token
            self.match('OPERADOR_ARITMETICO')
            right_type = self.parse_termino()
            
            # Análisis Semántico: Validar operaciones
            if left_type == 'Texto' or right_type == 'Texto':
                 raise SemanticErrorCosteñol(
                    "Joda loco estas barrilete — No se permiten operaciones aritméticas con cadenas de Texto.",
                    op_token
                )
            if left_type == 'Real' or right_type == 'Real':
                left_type = 'Real' # Promoción a Real
            else:
                left_type = 'Entero'
                
        return left_type

    def parse_termino(self):
        """
        Retorna el tipo del término analizado.
        """
        if not self.current_token:
            raise SyntaxErrorCosteñol("mi llave barros schelotto — Expresión incompleta, se llegó al fin del archivo.", None)
            
        if self.current_token.type == 'NUMERO_ENTERO':
            self.match('NUMERO_ENTERO')
            return 'Entero'
        elif self.current_token.type == 'NUMERO_REAL':
            self.match('NUMERO_REAL')
            return 'Real'
        elif self.current_token.type == 'CADENA_TEXTO':
            self.match('CADENA_TEXTO')
            return 'Texto'
        elif self.current_token.type == 'IDENTIFICADOR':
            id_token = self.current_token
            self.match('IDENTIFICADOR')
            # Retorna el tipo de la variable desde la tabla de símbolos
            return self.symtab.lookup(id_token.value, id_token)
        elif self.current_token.type == 'PARENTESIS_ABRE':
            self.match('PARENTESIS_ABRE')
            expr_type = self.parse_expresion()
            self.match('PARENTESIS_CIERRA')
            return expr_type
        else:
            raise SyntaxErrorCosteñol(
                f"mi llave barros schelotto — Se esperaba un número, identificador o cadena en la expresión. Se encontró '{self.current_token.value}'.",
                self.current_token
            )
