import os
import subprocess

diagrams = {
    "docs/diagrama1.mmd": """graph TD
    A[compilator_costeñol] --> B[.venv]
    A --> C[docs]
    A --> D[src]
    A --> E[tests]
    A --> F[requirements.txt]

    C --> C1[tarea.md]
    C --> C2[investigacion.md]
    C --> C3[actividad_inicial.md]

    D --> D1[main.py]
    D --> D2[lexer/]
    D2 --> D2A[__init__.py]
    D2 --> D2B[scanner.py]
    D2 --> D2C[tokens.py]
    D --> D3[parser/]
    D3 --> D3A[__init__.py]
    D --> D4[gui/]
    D4 --> D4A[__init__.py]
    D4 --> D4B[app.py]

    E --> E1[__init__.py]
    E --> E2[test_lexer.py]""",

    "docs/diagrama2.mmd": """flowchart LR
    User([Usuario]) -->|Escribe Código| GUI[Interfaz Tkinter]
    GUI -->|String| Lexer[Analizador Léxico]
    Lexer -->|Lista de Tokens| Parser[Analizador Sintáctico]
    Parser -->|Árbol de Sintaxis| Semantic[Analizador Semántico]

    Lexer -.->|Retorna Tabla de Tokens| GUI
    Parser -.->|Retorna Errores/Éxito| GUI""",

    "docs/diagrama3.mmd": """flowchart TD
    A([Usuario]) -->|Ingresa código en GUI| B(Interfaz Tkinter Estilo VSCode)
    B -->|Clic en Analizar| C{Motor Léxico Regex}

    C -->|Leer token a token| D[Identifica: num1 -> IDENTIFICADOR]
    C --> E[Ignora: espacios en blanco]
    C --> F[Identifica: Entero -> TIPO_DATO]
    C --> G[Identifica: ; -> DELIMITADOR]

    D --> H((Lista de Tokens))
    F --> H
    G --> H

    H -->|Devuelve Array| I[Tabla Treeview de Tkinter]
    I -->|Muestra resultados| J([Usuario])"""
}

# Crear archivos .mmd
for filename, content in diagrams.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

# Ejecutar mmdc para cada uno
for filename in diagrams.keys():
    out_png = filename.replace(".mmd", ".png")
    print(f"Generando {out_png}...")
    subprocess.run(f"npx --yes @mermaid-js/mermaid-cli -i {filename} -o {out_png} -b transparent", shell=True)

print("Imágenes generadas correctamente.")
