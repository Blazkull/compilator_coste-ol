import sys
import os
import unittest

# Añadir src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from tests.test_lexer import TestLexer
from tests.test_parser import TestParser
from tests.test_semantic import TestSemantic

def run_custom_tests():
    print("========================================")
    print(" EJECUTANDO PRUEBAS DEL COMPILADOR ")
    print("========================================\n")
    
    loader = unittest.TestLoader()
    suite_lexer = loader.loadTestsFromTestCase(TestLexer)
    suite_parser = loader.loadTestsFromTestCase(TestParser)
    suite_semantic = loader.loadTestsFromTestCase(TestSemantic)
    
    passed = 0
    failed = 0
    
    def run_suite(suite, name):
        nonlocal passed, failed
        print(f"\n--- Pruebas de {name} ---")
        for test in suite:
            test_name = test._testMethodName
            description = test.shortDescription() or test_name
            result = test.defaultTestResult()
            test.run(result)
            
            if result.wasSuccessful():
                print(f"Te vi bien ahí ✅ | {description}")
                passed += 1
            else:
                print(f"[FALLO] | {description}")
                failed += 1

    run_suite(suite_lexer, "Analizador Léxico")
    run_suite(suite_parser, "Analizador Sintáctico")
    run_suite(suite_semantic, "Analizador Semántico")
            
    print("\n----------------------------------------")
    print(" RESUMEN DE PRUEBAS ")
    print("----------------------------------------")
    print(f"Total de Pruebas: {passed + failed}")
    print(f"Exitosas:         {passed}")
    print(f"Fallidas:         {failed}")
    
    if failed == 0:
        print("\n>>> belloooo antioquia 🎉 — TODAS LAS PRUEBAS PASARON EXITOSAMENTE <<<")
    else:
        print("\n>>> ALGUNAS PRUEBAS FALLARON. REVISA EL CÓDIGO. <<<")

if __name__ == '__main__':
    run_custom_tests()
