import re
from enum import Enum

class TokenType(Enum):
    TIPO_DATO = r'\b(Texto|Entero|Real|Logico)\b'
    COMANDO_IO = r'\b(Captura|Mensaje)\b'
    IDENTIFICADOR = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
    NUMERO_REAL = r'\b\d+,\d+\b'
    NUMERO_ENTERO = r'\b\d+\b'
    CADENA_TEXTO = r'"[^"]*"'
    OPERADOR_ASIGNACION = r'='
    OPERADOR_ARITMETICO = r'[\+\-\*/]'
    SEPARADOR = r'\.'
    DELIMITADOR_FIN = r';'
    PARENTESIS_ABRE = r'\('
    PARENTESIS_CIERRA = r'\)'
    COMA = r','
    ESPACIOS = r'\s+'
    
# Diccionario ordenado para la construcción del Regex maestro.
# El orden es vital: Las palabras reservadas (TIPO_DATO, COMANDO_IO) 
# y números reales deben procesarse ANTES que los identificadores y enteros genéricos.
TOKEN_REGEX = [
    ('TIPO_DATO', TokenType.TIPO_DATO.value),
    ('COMANDO_IO', TokenType.COMANDO_IO.value),
    ('NUMERO_REAL', TokenType.NUMERO_REAL.value),
    ('NUMERO_ENTERO', TokenType.NUMERO_ENTERO.value),
    ('IDENTIFICADOR', TokenType.IDENTIFICADOR.value),
    ('CADENA_TEXTO', TokenType.CADENA_TEXTO.value),
    ('OPERADOR_ASIGNACION', TokenType.OPERADOR_ASIGNACION.value),
    ('OPERADOR_ARITMETICO', TokenType.OPERADOR_ARITMETICO.value),
    ('SEPARADOR', TokenType.SEPARADOR.value),
    ('DELIMITADOR_FIN', TokenType.DELIMITADOR_FIN.value),
    ('PARENTESIS_ABRE', TokenType.PARENTESIS_ABRE.value),
    ('PARENTESIS_CIERRA', TokenType.PARENTESIS_CIERRA.value),
    ('COMA', TokenType.COMA.value),
    ('ESPACIOS', TokenType.ESPACIOS.value),
]

# Construir el patrón maestro uniéndolos con el operador OR "|"
MASTER_REGEX = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_REGEX))
