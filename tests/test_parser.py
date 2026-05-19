import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.lexer.scanner import tokenize
from src.parser.parser import Parser, SyntaxErrorCosteñol

class TestParser(unittest.TestCase):
    
    def _parse(self, code):
        """Helper para evitar repetir código."""
        tokens = tokenize(code)
        parser = Parser(tokens)
        parser.parse()
        
    def test_declaracion_correcta(self):
        """Prueba Sintáctica: Declaración correcta -> 'num1 Entero;'"""
        try:
            self._parse("num1 Entero;")
        except SyntaxErrorCosteñol:
            self.fail("Falló en una declaración que debería ser válida.")
            
    def test_declaracion_incorrecta_orden(self):
        """Prueba Sintáctica: Fallo intencional por orden inverso -> 'Entero num1;'"""
        with self.assertRaises(SyntaxErrorCosteñol) as context:
            self._parse("Entero num1;")
        self.assertIn("Toda sentencia debe empezar con un Identificador", context.exception.message)
            
    def test_declaracion_sin_punto_y_coma(self):
        """Prueba Sintáctica: Fallo intencional por falta de punto y coma -> 'num1 Entero'"""
        with self.assertRaises(SyntaxErrorCosteñol):
            self._parse("num1 Entero")
            
    def test_asignacion_matematica(self):
        """Prueba Sintáctica: Asignación matemática con paréntesis -> 'res = (10 + 20) / 5;'"""
        try:
            self._parse("res Real; res = (10 + 20) / 5;")
        except SyntaxErrorCosteñol:
            self.fail("Falló en una asignación matemática válida.")
            
    def test_asignacion_incompleta(self):
        """Prueba Sintáctica: Fallo intencional por expresión matemática incompleta -> 'res = 10 + ;'"""
        with self.assertRaises(SyntaxErrorCosteñol):
            self._parse("res Entero; res = 10 + ;")
            
    def test_captura_correcta(self):
        """Prueba Sintáctica: Función Captura bien formada -> 'nombre = Captura.Texto();'"""
        try:
            self._parse("nombre Texto; nombre = Captura.Texto();")
        except SyntaxErrorCosteñol:
            self.fail("Falló en una Captura que debería ser válida.")
            
    def test_captura_sin_parentesis(self):
        """Prueba Sintáctica: Fallo intencional Captura sin paréntesis -> 'nombre = Captura.Texto;'"""
        with self.assertRaises(SyntaxErrorCosteñol):
            self._parse("nombre Texto; nombre = Captura.Texto;")
            
    def test_mensaje_correcto(self):
        """Prueba Sintáctica: Función Mensaje bien formada -> 'Mensaje.Texto("Hola Mundo");'"""
        try:
            self._parse('Mensaje.Texto("Hola Mundo");')
        except SyntaxErrorCosteñol:
            self.fail("Falló en un Mensaje que debería ser válido.")

    def test_varias_lineas(self):
        """Prueba Sintáctica: Bloque completo de código."""
        codigo = '''
        num1 Entero;
        nombre Texto;
        res Entero;
        nombre = Captura.Texto();
        res = num1 + 5;
        Mensaje.Texto(nombre);
        '''
        try:
            self._parse(codigo)
        except SyntaxErrorCosteñol:
            self.fail("Falló al parsear un bloque válido de varias líneas.")

    def test_precedencia_aritmetica(self):
        """Prueba Sintáctica: Precedencia aritmética correcta -> 'res = 2 + 3 * 4;'"""
        try:
            tokens = tokenize("res Entero; res = 2 + 3 * 4;")
            parser = Parser(tokens)
            ast = parser.parse()
            # Validar que el nodo raíz es un AssignmentNode
            stmt = ast.statements[1]
            self.assertEqual(stmt.name, "res")
            # El valor asignado debe ser un BinaryOpNode (+) donde el hijo derecho es otro BinaryOpNode (*)
            self.assertEqual(stmt.value_node.op, "+")
            self.assertEqual(stmt.value_node.right.op, "*")
        except Exception as e:
            self.fail(f"Falló la prueba de precedencia aritmética: {str(e)}")

if __name__ == '__main__':
    unittest.main()
