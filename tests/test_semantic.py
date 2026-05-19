import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.lexer.scanner import tokenize
from src.parser.parser import Parser
from src.semantic.symbol_table import SemanticErrorCosteñol

class TestSemantic(unittest.TestCase):
    
    def _parse(self, code):
        """Helper para evitar repetir código."""
        tokens = tokenize(code)
        parser = Parser(tokens)
        parser.parse()
        
    def test_declaracion_duplicada(self):
        """Prueba Semántica: Falla al declarar dos veces la misma variable."""
        with self.assertRaises(SemanticErrorCosteñol) as context:
            self._parse("num1 Entero; num1 Texto;")
        self.assertIn("ya fue declarada previamente", context.exception.message)
            
    def test_uso_no_declarado(self):
        """Prueba Semántica: Falla al asignar a variable no declarada."""
        with self.assertRaises(SemanticErrorCosteñol) as context:
            self._parse("fantasma = 10;")
        self.assertIn("no ha sido declarada", context.exception.message)
            
    def test_tipo_incorrecto_asignacion(self):
        """Prueba Semántica: Falla al asignar Texto a un Entero."""
        with self.assertRaises(SemanticErrorCosteñol) as context:
            self._parse('num1 Entero; num1 = "Hola";')
        self.assertIn("No se puede asignar una expresión de tipo 'Texto'", context.exception.message)
            
    def test_tipo_incorrecto_captura(self):
        """Prueba Semántica: Falla al capturar Texto en variable Real."""
        with self.assertRaises(SemanticErrorCosteñol) as context:
            self._parse('pi Real; pi = Captura.Texto();')
        self.assertIn("Se intenta capturar un 'Texto'", context.exception.message)
            
    def test_tipo_incorrecto_mensaje(self):
        """Prueba Semántica: Falla al imprimir Entero con Mensaje.Texto."""
        with self.assertRaises(SemanticErrorCosteñol) as context:
            self._parse('num1 Entero; num1 = 5; Mensaje.Texto(num1);')
        self.assertIn("no puede imprimir la variable 'num1' de tipo 'Entero'", context.exception.message)

    def test_operacion_con_texto(self):
        """Prueba Semántica: Falla al sumar Textos."""
        with self.assertRaises(SemanticErrorCosteñol) as context:
            self._parse('nombre Texto; res Entero; nombre = "a"; res = nombre + 5;')
        self.assertIn("No se permite el operador", context.exception.message)

    def test_asignacion_valida_promocion(self):
        """Prueba Semántica: Permite asignar Entero a Real."""
        try:
            self._parse('num1 Real; num1 = 5;')
        except SemanticErrorCosteñol:
            self.fail("Falló en una asignación semántica válida (Entero -> Real).")

    def test_complejo_multilinea_valido(self):
        """Prueba Semántica: Multiples líneas válidas."""
        codigo = '''
        num1 Entero;
        num2 Real;
        num1 = 5;
        num2 = num1 + 3;
        texto1 Texto;
        texto1 = "Exito";
        Mensaje.Texto(texto1);
        '''
        try:
            self._parse(codigo)
        except SemanticErrorCosteñol:
            self.fail("Falló en un bloque válido de varias líneas.")
            
    def test_complejo_error_anidado(self):
        """Prueba Semántica: Multiples líneas con error al final."""
        codigo = '''
        num1 Entero;
        num2 Real;
        num1 = 5;
        num2 = num1 + 3;
        texto1 Texto;
        texto1 = num1 + 10;
        '''
        with self.assertRaises(SemanticErrorCosteñol) as context:
            self._parse(codigo)
        self.assertIn("No se puede asignar una expresión de tipo 'Entero'", context.exception.message)

if __name__ == '__main__':
    unittest.main()
