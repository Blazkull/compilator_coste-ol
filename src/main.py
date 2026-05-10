import sys
import os

# Añadir el directorio raíz al path para poder importar src como paquete
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gui.app import start_app

def main():
    # Lanzar la Interfaz Gráfica
    start_app()

if __name__ == "__main__":
    main()

