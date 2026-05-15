import re
from .tokens import MASTER_REGEX

class LexicalError(Exception):
    def __init__(self, message, line, column):
        super().__init__(f"Hey loco que pasa vale mia — línea {line}, columna {column}: {message}")
        self.line = line
        self.column = column

class Token:
    def __init__(self, type_name, value, line, column):
        self.type = type_name
        self.value = value
        self.line = line
        self.column = column
        
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', Linea: {self.line}, Col: {self.column})"

def tokenize(code: str):
    """
    Escanea el código fuente y genera una lista de tokens.
    Lanza LexicalError si encuentra un caracter no reconocido.
    """
    tokens = []
    line_num = 1
    line_start = 0
    position = 0
    length = len(code)
    
    while position < length:
        match = MASTER_REGEX.match(code, position)
        if match:
            type_name = match.lastgroup
            value = match.group(type_name)
            column = position - line_start + 1
            
            if type_name != 'ESPACIOS':
                tokens.append(Token(type_name, value, line_num, column))
            elif '\n' in value:
                # Actualizar línea y columna si hay saltos de línea en los espacios
                line_num += value.count('\n')
                line_start = position + value.rfind('\n') + 1
                
            position = match.end()
        else:
            # Si no hay match, hay un caracter ilegal
            column = position - line_start + 1
            illegal_char = code[position]
            raise LexicalError(f"Caracter ilegal '{illegal_char}'", line_num, column)
            
    return tokens
