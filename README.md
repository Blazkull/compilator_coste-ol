# Compilador "COSTEÑOL"

Un compilador visual y educativo desarrollado en **Python** con **Tkinter**, diseñado para analizar de manera léxica, sintáctica y semántica el lenguaje ficticio "Costeñol".

## Características
- **Interfaz Estilo VSCode:** Editor de código con tema oscuro, numeración de líneas y consola integrada para reportes.
- **Análisis Léxico (Scanner):** Motor robusto basado en Expresiones Regulares (`re`) que descompone el texto de izquierda a derecha en Tokens categorizados.
- **Pruebas Automatizadas:** Listo para integrarse con `unittest` o `pytest` garantizando la estabilidad de las reglas gramaticales.

## Estructura del Proyecto

```text
compilator_costeñol/
├── .venv/                  # Entorno virtual de Python
├── docs/                   # Documentación teórica y manual de uso
├── src/                    # Código fuente del compilador (lexer, parser, gui)
├── tests/                  # Scripts de pruebas automatizadas
├── .gitignore              # Ignora archivos temporales y entornos
├── requirements.txt        # Dependencias del proyecto
└── run_tests.py            # Script personalizado para ejecutar pruebas
```

Para más detalles, revisa el archivo `docs/arquitectura.md`.

## Instalación y Configuración

Se recomienda ejecutar el proyecto dentro del entorno virtual provisto para aislar dependencias.

1. **Clonar/Abrir el repositorio** en tu entorno de desarrollo.
2. **Activar el entorno virtual:**
   - En **Windows**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - En **Linux/Mac**:
     ```bash
     source .venv/bin/activate
     ```
3. **Instalar dependencias:**
   *(Si el proyecto incluye librerías externas en el futuro)*
   ```powershell
   pip install -r requirements.txt
   ```

## 🚀 Guía de Uso Detallada

### 1. Iniciar la Interfaz Gráfica (IDE)

El proyecto cuenta con una interfaz visual amigable (estilo VSCode) donde podrás escribir y evaluar el código en tiempo real. Para iniciarla, ejecuta:

```powershell
python src/main.py
```

**¿Cómo usar la interfaz?**
1. **Editor de Código:** En el panel superior, escribe tu código respetando la sintaxis de Costeñol. Por defecto, verás un código de ejemplo cargado.
2. **Analizar:** Haz clic en el botón azul `▶ Analizar Código`.
3. **Consola de Resultados:** En la parte inferior aparecerá una tabla detallada con cada componente de tu código desglosado:
   - **Línea y Columna:** Ubicación exacta de la palabra.
   - **Tipo de Token:** La categoría a la que pertenece (Ej: `IDENTIFICADOR`, `TIPO_DATO`).
   - **Lexema:** La palabra o símbolo exacto que escribiste.
4. **Deshacer Errores:** El editor soporta `Ctrl+Z` para deshacer y `Ctrl+Y` para rehacer.

*Nota: Si ingresas un carácter ilegal (como un `@`), el panel inferior se pintará de rojo mostrándote la línea y columna exacta del error.*

### 2. Ejemplos de Sintaxis Soportada (Costeñol)

Puedes copiar y pegar los siguientes ejemplos en el editor para probar el motor:

**Declaración de variables:**
```text
num1 Entero;
nombre Texto;
```

**Comandos de Entrada y Salida:**
```text
nombre = Captura.Texto();
Mensaje.Texto("Hola Mundo");
```

**Asignaciones y Matemáticas:**
```text
pi = 3,1416;
suma = num1 + (num2 * num3);
```

### 3. Ejecutar Pruebas Automatizadas (Testing)

El compilador cuenta con un conjunto de pruebas unitarias (`unittest`) diseñadas para blindar el código y garantizar que el Analizador no falle ante escenarios complejos o espacios en blanco inesperados.

Para correr el reporte de pruebas, usa nuestro script personalizado que te mostrará exactamente qué línea de código se evaluó y si pasó la validación:

```powershell
python run_tests.py
```

Si deseas ver el formato genérico de Python, puedes usar alternativamente: `python -m unittest tests/test_lexer.py -v`.

## Documentación

Toda la documentación técnica y de planificación se encuentra en la carpeta `/docs`.
- Si necesitas aprender a utilizar la interfaz y las palabras clave del lenguaje, consulta [docs/manual_de_uso.md](docs/manual_de_uso.md).
- Para ver la hoja de ruta de desarrollo, consulta [docs/sprints.md](docs/sprints.md).

---
*Proyecto académico enfocado en el aprendizaje de la teoría de compiladores.*
