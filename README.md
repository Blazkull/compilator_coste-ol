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

## Ejecución

Una vez activado el entorno, inicia la aplicación ejecutando el punto de entrada principal:

```powershell
python src/main.py
```

### Ejecutar Pruebas Automatizadas

Para validar que las reglas del motor léxico (y sintáctico) están funcionando sin errores, ejecuta el script personalizado de pruebas desde la terminal:

```powershell
python run_tests.py
```

## Documentación

Toda la documentación técnica y de planificación se encuentra en la carpeta `/docs`.
- Si necesitas aprender a utilizar la interfaz y las palabras clave del lenguaje, consulta [docs/manual_de_uso.md](docs/manual_de_uso.md).
- Para ver la hoja de ruta de desarrollo, consulta [docs/sprints.md](docs/sprints.md).

---
*Proyecto académico enfocado en el aprendizaje de la teoría de compiladores.*
