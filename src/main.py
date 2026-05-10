import sys
import os

# Añadir el directorio src al path para poder importar módulos
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gui.app import start_app

def main():
    # Lanzar la Interfaz Gráfica
    start_app()

if __name__ == "__main__":
    main()

