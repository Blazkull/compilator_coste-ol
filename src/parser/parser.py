from src.semantic.symbol_table import SymbolTable, SemanticErrorCosteñol

class SyntaxErrorCosteñol(Exception):
    """Excepción lanzada cuando hay un error de sintaxis en el código."""
    def __init__(self, message, token):
        self.token = token
        line = token.line if token else "Desconocida"
        self.message = f"{message} (Línea: {line})"
        super().__init__(self.message)

# --- Clases para el Árbol de Sintaxis Abstracta (AST) ---
class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class DeclarationNode(ASTNode):
    def __init__(self, name, var_type):
        self.name = name
        self.var_type = var_type

class AssignmentNode(ASTNode):
    def __init__(self, name, value_node):
        self.name = name
        self.value_node = value_node

class ConcatenationNode(ASTNode):
    def __init__(self, nodes):
        self.nodes = nodes

class CaptureNode(ASTNode):
    def __init__(self, name, var_type):
        self.name = name
        self.var_type = var_type

class MessageNode(ASTNode):
    def __init__(self, msg_type, arguments):
        self.msg_type = msg_type
        self.arguments = arguments

class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right, result_type):
        self.left = left
        self.op = op
        self.right = right
        self.result_type = result_type

class LiteralNode(ASTNode):
    def __init__(self, value, val_type):
        self.value = value
        self.val_type = val_type

class VariableNode(ASTNode):
    def __init__(self, name, var_type):
        self.name = name
        self.var_type = var_type

class IfNode(ASTNode):
    def __init__(self, condition, then_statements, else_statements=None):
        self.condition = condition
        self.then_statements = then_statements
        self.else_statements = else_statements

class WhileNode(ASTNode):
    def __init__(self, condition, body_statements):
        self.condition = condition
        self.body_statements = body_statements

class ComparisonNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

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
        token = self.current_token
        if self.current_token and self.current_token.type == expected_type:
            self.advance()
            return token
        else:
            actual_type = self.current_token.type if self.current_token else "EOF (Fin de Archivo)"
            val = self.current_token.value if self.current_token else "Nada"
            raise SyntaxErrorCosteñol(
                f"mi llave barros schelotto — Se esperaba '{expected_type}', pero se encontró '{actual_type}' ('{val}').",
                self.current_token
            )

    def parse(self):
        """Punto de entrada principal para parsear todo el programa."""
        statements = []
        while self.current_token is not None:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return ProgramNode(statements)

    def parse_block(self):
        """Parsea un bloque encerrado entre llaves { }."""
        self.match('LLAVE_ABRE')
        statements = []
        while self.current_token and self.current_token.type != 'LLAVE_CIERRA':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        self.match('LLAVE_CIERRA')
        return statements

    def parse_statement(self):
        """
        Determina qué tipo de sentencia se va a analizar mirando el token actual.
        """
        if self.current_token.type == 'COMANDO_IO':
            if self.current_token.value == 'Mensaje':
                return self.parse_mensaje()
            else:
                raise SyntaxErrorCosteñol(
                    "mi llave barros schelotto — El comando 'Captura' debe ser asignado a una variable.",
                    self.current_token
                )

        elif self.current_token.type == 'CONTROL':
            if self.current_token.value == 'Si':
                return self.parse_if()
            elif self.current_token.value == 'Mientras':
                return self.parse_while()
            else:
                raise SyntaxErrorCosteñol(
                    f"mi llave barros schelotto — No se esperaba '{self.current_token.value}' aquí.",
                    self.current_token
                )

        elif self.current_token.type == 'IDENTIFICADOR':
            next_idx = self.current_index + 1
            if next_idx < len(self.tokens):
                next_token = self.tokens[next_idx]
                if next_token.type == 'TIPO_DATO':
                    return self.parse_declaracion()
                elif next_token.type == 'OPERADOR_ASIGNACION':
                    return self.parse_asignacion_o_captura()
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
                f"mi llave barros schelotto — Toda sentencia debe empezar con un Identificador, 'Mensaje' o control. Se encontró '{self.current_token.value}'.",
                self.current_token
            )

    def parse_if(self):
        """Regla Si: Si ( [ExpLogica] ) { [Cuerpo] } [Sino { [Cuerpo] }]"""
        self.match('CONTROL') # Si
        self.match('PARENTESIS_ABRE')
        condition = self.parse_expresion_logica()
        self.match('PARENTESIS_CIERRA')
        
        then_branch = self.parse_block()
        else_branch = None
        
        if self.current_token and self.current_token.type == 'CONTROL' and self.current_token.value == 'Sino':
            self.match('CONTROL')
            else_branch = self.parse_block()
            
        return IfNode(condition, then_branch, else_branch)

    def parse_while(self):
        """Regla Mientras: Mientras ( [ExpLogica] ) { [Cuerpo] }"""
        self.match('CONTROL') # Mientras
        self.match('PARENTESIS_ABRE')
        condition = self.parse_expresion_logica()
        self.match('PARENTESIS_CIERRA')
        
        body = self.parse_block()
        return WhileNode(condition, body)

    def parse_expresion_logica(self):
        """Parsea comparaciones simples: [ExpArit] [Comparador] [ExpArit]"""
        left, left_type = self.parse_expresion()
        
        if self.current_token and self.current_token.type == 'COMPARADOR':
            op_token = self.match('COMPARADOR')
            right, right_type = self.parse_expresion()
            
            # Semántico: Solo comparar números o textos entre sí
            if (left_type in ['Entero', 'Real'] and right_type in ['Entero', 'Real']) or (left_type == 'Texto' and right_type == 'Texto'):
                return ComparisonNode(left, op_token.value, right)
            else:
                raise SemanticErrorCosteñol(
                    f"Joda loco estas barrilete — No se puede comparar un '{left_type}' con un '{right_type}'.",
                    op_token
                )
        
        # Si no hay comparador, puede ser un booleano directo
        if left_type == 'Logico' or isinstance(left, LiteralNode) and left.val_type == 'Logico':
            return left
            
        raise SyntaxErrorCosteñol(
            "mi llave barros schelotto — Se esperaba una comparación o un valor lógico.",
            self.current_token
        )

    def parse_declaracion(self):
        """Regla 1: [IDENTIFICADOR] [TIPO_DATO] [DELIMITADOR_FIN]"""
        name_token = self.match('IDENTIFICADOR')
        type_token = self.match('TIPO_DATO')
        self.match('DELIMITADOR_FIN')
        
        self.symtab.define(name_token.value, type_token.value, name_token)
        return DeclarationNode(name_token.value, type_token.value)

    def parse_asignacion_o_captura(self):
        """Regla 2 y 3: Asignación o Captura"""
        name_token = self.match('IDENTIFICADOR')
        var_type = self.symtab.lookup(name_token.value, name_token)
        self.match('OPERADOR_ASIGNACION')
        
        if self.current_token and self.current_token.type == 'COMANDO_IO' and self.current_token.value == 'Captura':
            return self.parse_captura_tail(var_type, name_token)
        else:
            values = []
            val_node, expr_type = self.parse_expresion()
            values.append(val_node)
            
            while self.current_token and self.current_token.type == 'COMA':
                if var_type != 'Texto':
                    raise SemanticErrorCosteñol(
                        f"Joda loco estas barrilete — Solo las variables de tipo 'Texto' admiten concadenación con comas.",
                        self.current_token
                    )
                self.match('COMA')
                v_node, _ = self.parse_expresion()
                values.append(v_node)

            self.match('DELIMITADOR_FIN')
            
            final_value = ConcatenationNode(values) if len(values) > 1 else values[0]
            return AssignmentNode(name_token.value, final_value)

    def parse_captura_tail(self, var_type, name_token):
        self.match('COMANDO_IO') # Captura
        self.match('SEPARADOR') # .
        captura_type_token = self.match('TIPO_DATO')
        
        if captura_type_token.value != var_type:
            raise SemanticErrorCosteñol(
                f"Joda loco estas barrilete — Se intenta capturar un '{captura_type_token.value}' en la variable '{name_token.value}' que es de tipo '{var_type}'.",
                captura_type_token
            )
            
        self.match('PARENTESIS_ABRE')
        self.match('PARENTESIS_CIERRA')
        self.match('DELIMITADOR_FIN')
        return CaptureNode(name_token.value, var_type)

    def parse_mensaje(self):
        self.match('COMANDO_IO')
        self.match('SEPARADOR')
        msg_type_token = self.match('TIPO_DATO')
        self.match('PARENTESIS_ABRE')
        
        arguments = []
        def parse_argument():
            if self.current_token and self.current_token.type == 'CADENA_TEXTO':
                if msg_type_token.value != 'Texto':
                     raise SemanticErrorCosteñol(
                        f"Joda loco estas barrilete — 'Mensaje.{msg_type_token.value}' no puede imprimir una cadena de Texto directa.",
                        msg_type_token
                    )
                token = self.match('CADENA_TEXTO')
                arguments.append(LiteralNode(token.value.strip('"'), 'Texto'))
            elif self.current_token and self.current_token.type == 'IDENTIFICADOR':
                id_token = self.match('IDENTIFICADOR')
                var_type = self.symtab.lookup(id_token.value, id_token)
                if msg_type_token.value != 'Texto' and var_type != msg_type_token.value:
                    raise SemanticErrorCosteñol(
                        f"Joda loco estas barrilete — 'Mensaje.{msg_type_token.value}' no puede imprimir la variable '{id_token.value}' de tipo '{var_type}'.",
                        id_token
                    )
                arguments.append(VariableNode(id_token.value, var_type))
            else:
                raise SyntaxErrorCosteñol(
                    "mi llave barros schelotto — El Mensaje debe contener una Cadena de Texto o un Identificador.",
                    self.current_token
                )

        parse_argument()
        while self.current_token and self.current_token.type == 'COMA':
            self.match('COMA')
            parse_argument()
            
        self.match('PARENTESIS_CIERRA')
        self.match('DELIMITADOR_FIN')
        return MessageNode(msg_type_token.value, arguments)

    def parse_expresion(self):
        left_node, left_type = self.parse_termino()
        
        while self.current_token and self.current_token.type == 'OPERADOR_ARITMETICO':
            op_token = self.match('OPERADOR_ARITMETICO')
            right_node, right_type = self.parse_termino()
            
            if left_type == 'Texto' or right_type == 'Texto':
                raise SemanticErrorCosteñol(
                    f"Joda loco estas barrilete — No se permite el operador '{op_token.value}' con cadenas de Texto. La concadenación en Costeñol se hace con comas ( , ).",
                    op_token
                )
            
            res_type = 'Real' if (left_type == 'Real' or right_type == 'Real') else 'Entero'
            left_node = BinaryOpNode(left_node, op_token.value, right_node, res_type)
            left_type = res_type
                
        return left_node, left_type

    def parse_termino(self):
        if not self.current_token:
            raise SyntaxErrorCosteñol("mi llave barros schelotto — Expresión incompleta, se llegó al fin del archivo.", None)
            
        if self.current_token.type == 'NUMERO_ENTERO':
            token = self.match('NUMERO_ENTERO')
            return LiteralNode(int(token.value), 'Entero'), 'Entero'
        elif self.current_token.type == 'NUMERO_REAL':
            token = self.match('NUMERO_REAL')
            return LiteralNode(float(token.value.replace(',', '.')), 'Real'), 'Real'
        elif self.current_token.type == 'CADENA_TEXTO':
            token = self.match('CADENA_TEXTO')
            return LiteralNode(token.value.strip('"'), 'Texto'), 'Texto'
        elif self.current_token.type == 'BOOLEANO':
            token = self.match('BOOLEANO')
            val = True if token.value == 'Verdad' else False
            return LiteralNode(val, 'Logico'), 'Logico'
        elif self.current_token.type == 'IDENTIFICADOR':
            id_token = self.match('IDENTIFICADOR')
            var_type = self.symtab.lookup(id_token.value, id_token)
            return VariableNode(id_token.value, var_type), var_type
        elif self.current_token.type == 'PARENTESIS_ABRE':
            self.match('PARENTESIS_ABRE')
            nodes = []
            node, expr_type = self.parse_expresion()
            nodes.append(node)
            
            while self.current_token and self.current_token.type == 'COMA':
                self.match('COMA')
                next_node, _ = self.parse_expresion()
                nodes.append(next_node)
                expr_type = 'Texto' # Si hay comas, el resultado es Texto
            
            self.match('PARENTESIS_CIERRA')
            return (ConcatenationNode(nodes) if len(nodes) > 1 else node), expr_type
        else:
            raise SyntaxErrorCosteñol(
                f"mi llave barros schelotto — Se esperaba un número, identificador o cadena en la expresión. Se encontró '{self.current_token.value}'.",
                self.current_token
            )
