import sys
import os
import unittest

# Añadir el directorio raíz al path para poder importar src como paquete
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lexer.scanner import tokenize, LexicalError

class TestLexer(unittest.TestCase):
    def test_declaracion_variables(self):
        """Prueba: Declaración simple -> 'num1 Entero; nombre Texto;'"""
        code = "num1 Entero; nombre Texto;"
        tokens = tokenize(code)
        
        self.assertEqual(len(tokens), 6)
        self.assertEqual(tokens[0].type, "IDENTIFICADOR")
        self.assertEqual(tokens[0].value, "num1")
        self.assertEqual(tokens[1].type, "TIPO_DATO")
        self.assertEqual(tokens[1].value, "Entero")
        self.assertEqual(tokens[2].type, "DELIMITADOR_FIN")
        
    def test_asignacion_matematica(self):
        """Prueba: Asignación con paréntesis -> 'suma = num1 + (num2 * num3);'"""
        code = "suma = num1 + (num2 * num3);"
        tokens = tokenize(code)
        
        # suma, =, num1, +, (, num2, *, num3, ), ; -> 10 tokens
        self.assertEqual(len(tokens), 10)
        self.assertEqual(tokens[1].type, "OPERADOR_ASIGNACION")
        self.assertEqual(tokens[3].type, "OPERADOR_ARITMETICO")
        self.assertEqual(tokens[4].type, "PARENTESIS_ABRE")
        
    def test_numeros_reales(self):
        """Prueba: Reconocimiento de reales -> 'pi = 3,1416;'"""
        code = "pi = 3,1416;"
        tokens = tokenize(code)
        
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[2].type, "NUMERO_REAL")
        self.assertEqual(tokens[2].value, "3,1416")
        
    def test_cadenas_texto(self):
        """Prueba: Reconocimiento de cadenas -> 'nombre = "Esto es una prueba";'"""
        code = 'nombre = "Esto es una prueba";'
        tokens = tokenize(code)
        
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[2].type, "CADENA_TEXTO")
        self.assertEqual(tokens[2].value, '"Esto es una prueba"')
        
    def test_comandos_io(self):
        """Prueba: Entrada/Captura -> 'Captura.Texto();'"""
        code = "Captura.Texto();"
        tokens = tokenize(code)
        
        # Captura, ., Texto, (, ), ; -> 6 tokens
        self.assertEqual(len(tokens), 6)
        self.assertEqual(tokens[0].type, "COMANDO_IO")
        self.assertEqual(tokens[1].type, "SEPARADOR")
        self.assertEqual(tokens[2].type, "TIPO_DATO")
        
    def test_error_lexico(self):
        """Prueba: Fallo intencional con caracter ilegal -> 'num@1 Entero;'"""
        code = "num@1 Entero;"
        with self.assertRaises(LexicalError):
            tokenize(code)
            
    def test_comando_mensaje(self):
        """Prueba: Salida/Mensaje -> 'Mensaje.Texto("Hola Mundo");'"""
        code = 'Mensaje.Texto("Hola Mundo");'
        tokens = tokenize(code)
        
        self.assertEqual(len(tokens), 7)
        self.assertEqual(tokens[0].type, "COMANDO_IO")
        self.assertEqual(tokens[0].value, "Mensaje")
        
    def test_ignorar_espacios_y_saltos(self):
        """Prueba: Ignorar \n y espacios -> 'num1 \\n Entero   ;'"""
        code = """
        num1 
        Entero   ;
        """
        tokens = tokenize(code)
        
        # Deben ser solo 3 tokens, ignorando \n y espacios
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[0].type, "IDENTIFICADOR")
        self.assertEqual(tokens[1].type, "TIPO_DATO")
        self.assertEqual(tokens[2].type, "DELIMITADOR_FIN")
        
    def test_operaciones_complejas(self):
        """Prueba: Operación compleja -> 'res = ( 10 + 20 ) / 5 - num1;'"""
        code = "res = ( 10 + 20 ) / 5 - num1;"
        tokens = tokenize(code)
        self.assertEqual(len(tokens), 12)
        self.assertEqual(tokens[9].type, "OPERADOR_ARITMETICO")
        self.assertEqual(tokens[9].value, "-")

if __name__ == '__main__':
    unittest.main(verbosity=2)
