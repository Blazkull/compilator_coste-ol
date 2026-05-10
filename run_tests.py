import sys
import os
import unittest

# Añadir src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from tests.test_lexer import TestLexer

def run_custom_tests():
    print("========================================")
    print(" EJECUTANDO PRUEBAS DEL COMPILADOR ")
    print("========================================\n")
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLexer)
    
    passed = 0
    failed = 0
    
    for test in suite:
        test_name = test._testMethodName
        description = test.shortDescription() or test_name
        
        # Ejecutar la prueba individualmente
        result = test.defaultTestResult()
        test.run(result)
        
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
