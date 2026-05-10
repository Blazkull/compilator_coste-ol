# Arquitectura del Compilador "COSTEÑOL"

Este documento detalla la función específica de cada archivo y carpeta dentro del proyecto. La modularidad es clave para mantener el código ordenado y permitir realizar pruebas automatizadas de forma aislada.

## Estructura Principal

```text
compilator_costeñol/
├── .venv/                  # Entorno virtual de Python (Aislamiento de dependencias).
├── docs/                   # Documentación teórica y de planificación.
├── src/                    # Código fuente principal del compilador.
├── tests/                  # Pruebas unitarias automatizadas.
├── README.md               # Presentación principal del proyecto.
└── requirements.txt        # Lista de dependencias (Librerías necesarias).
```

## Directorio `docs/` (Documentación)
- `tarea.md`: El requerimiento original del proyecto.
- `investigacion.md`: Reseña sobre compiladores existentes, herramientas y la definición técnica del lenguaje Costeñol.
- `actividad_inicial.md`: Diseño conceptual del Analizador Léxico y diagramas de flujo.
- `sprints.md`: Planificación del desarrollo iterativo del proyecto.
- `arquitectura.md`: (Este archivo) Explicación del propósito de cada componente del código.
- `manual_de_uso.md`: Guía para el usuario final sobre cómo operar el compilador visual.

## Directorio `src/` (Código Fuente)
Aquí reside la lógica del compilador, dividida en paquetes (carpetas con un archivo `__init__.py`).

- `main.py`
  - **Función:** Es el punto de entrada (Entry Point) del software. Su única responsabilidad es inicializar la Interfaz Gráfica (GUI) y poner en marcha la aplicación. No debe contener lógica profunda de compilación.

### Paquete `src/lexer/` (Analizador Léxico)
Encargado de la Fase 1: Leer el texto plano y convertirlo en "Tokens".
- `tokens.py`
  - **Función:** Define las constantes y expresiones regulares (Regex) de las reglas del Costeñol. Aquí se guardan los diccionarios que identifican qué es un `Entero`, qué es `Captura`, cómo lucen las variables y qué operadores existen.
- `scanner.py`
  - **Función:** Contiene el motor principal de tokenización. Toma una cadena de texto proveniente de la interfaz gráfica, la cruza contra los patrones definidos en `tokens.py` y devuelve un arreglo estructurado de Tokens (o un error si encuentra un carácter inválido).

### Paquete `src/parser/` (Analizador Sintáctico)
Encargado de la Fase 2: Validar la estructura gramatical.
- `__init__.py` / `parser.py` (En desarrollo)
  - **Función:** Toma la lista de Tokens generada por el Lexer y valida que estén en el orden correcto (ej: que a un Tipo de Dato le siga el nombre de una variable y luego un `;`). Genera el Árbol de Sintaxis Abstracta (AST).

### Paquete `src/gui/` (Interfaz Gráfica)
- `app.py`
  - **Función:** Construye la ventana visual utilizando **Tkinter**. Contiene la lógica para el "Tema VSCode", el campo de texto con números de línea, el botón de análisis y la consola inferior/tabla que muestra los resultados enviados por el `scanner.py` o `parser.py`.

## Directorio `tests/` (Pruebas Automatizadas)
- `test_lexer.py`
  - **Función:** Contiene pruebas unitarias construidas con `unittest` o `pytest`. Evalúa de forma automática todas las combinaciones posibles (código válido, código con errores, espacios en blanco, combinaciones de variables) enviándolas directamente al `scanner.py` sin pasar por la interfaz gráfica. Si se cambia alguna regla en el futuro, este archivo garantiza que nada se rompa.
