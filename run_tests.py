import sys
import os
import unittest

# Añadir src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from tests.test_lexer import TestLexer
from tests.test_parser import TestParser

def run_custom_tests():
    print("========================================")
    print(" EJECUTANDO PRUEBAS DEL COMPILADOR ")
    print("========================================\n")
    
    loader = unittest.TestLoader()
    suite_lexer = loader.loadTestsFromTestCase(TestLexer)
    suite_parser = loader.loadTestsFromTestCase(TestParser)
    
    all_tests = unittest.TestSuite([suite_lexer, suite_parser])
    
    passed = 0
    failed = 0
    
    for test in all_tests:
        # Algunos test pueden venir envueltos si es un TestSuite, así que los desglosamos
        for t in test:
            test_name = t._testMethodName
            description = t.shortDescription() or test_name
            
            # Ejecutar la prueba individualmente
            result = t.defaultTestResult()
            t.run(result)
            
            if result.wasSuccessful():
                print(f"[OK]    | {description}")
                passed += 1
            else:
                print(f"[FALLO] | {description}")
                failed += 1
            
    print("\n----------------------------------------")
    print(" RESUMEN DE PRUEBAS ")
    print("----------------------------------------")
    print(f"Total de Pruebas: {passed + failed}")
    print(f"Exitosas:         {passed}")
    print(f"Fallidas:         {failed}")
    
    if failed == 0:
        print("\n>>> TODAS LAS PRUEBAS PASARON EXITOSAMENTE <<<")
    else:
        print("\n>>> ALGUNAS PRUEBAS FALLARON. REVISA EL CÓDIGO. <<<")

if __name__ == '__main__':
    run_custom_tests()
