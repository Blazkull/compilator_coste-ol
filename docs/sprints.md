# Planificación de Sprints: Compilador "COSTEÑOL"

Este documento organiza el desarrollo del compilador en un marco de trabajo ágil basado en Sprints. Cada iteración tiene objetivos claros y entregables funcionales.

## Sprint 0: Fundamentos y Arquitectura (Completado)

**Objetivo:** Establecer las bases teóricas, la estructura técnica del proyecto y las reglas iniciales del lenguaje.

- **Tareas:**
  - [x] Investigación sobre compiladores y tecnologías.
  - [x] Definición de las reglas léxicas del lenguaje Costeñol (`Captura`, `Mensaje`, Tipos, etc).
  - [x] Diseño de la arquitectura del software (Diagramas).
  - [x] Creación de la estructura de carpetas modular para Python.
  - [x] Configuración del entorno virtual (`.venv`).
- **Entregable:** Documentación inicial completa y repositorio configurado.

---

## Sprint 1: Analizador Léxico y Base de UI (Actividad Inicial)

**Objetivo:** Implementar el "Scanner" que descompone el texto en Tokens y conectarlo a una versión temprana de la interfaz gráfica.

- **Tareas:**
  - [ ] Implementar el motor de expresiones regulares (`src/lexer/scanner.py` y `src/lexer/tokens.py`).
  - [ ] Crear la base de la Interfaz Gráfica con Tkinter estilo VSCode (Tema oscuro, caja de texto y tabla/consola) (`src/gui/app.py`).
  - [ ] Conectar el motor léxico a la GUI: al presionar "Analizar" se muestran los tokens.
  - [ ] Escribir pruebas unitarias iniciales para asegurar que las variables y palabras reservadas se reconozcan correctamente (`tests/test_lexer.py`).
- **Entregable:** GUI funcional donde el usuario puede escribir código y visualizar la tabla de tokens extraída.

---

## Sprint 2: Analizador Sintáctico (Parser)

**Objetivo:** Validar que los tokens extraídos sigan la estructura gramatical del lenguaje Costeñol.

- **Tareas:**
  - [ ] Definir la Gramática Libre de Contexto para el Costeñol (asignaciones, declaraciones, uso de Captura y Mensaje).
  - [ ] Implementar el árbol de validación sintáctica (`src/parser/`).
  - [ ] Detectar errores de sintaxis (ej. falta de `;` al final de la línea o paréntesis sin cerrar).
  - [ ] Actualizar la GUI para mostrar errores sintácticos en el panel de la consola inferior.
- **Entregable:** El compilador ahora puede aceptar o rechazar una línea de código indicando si está bien o mal escrita gramaticalmente.

---

## Sprint 3: Analizador Semántico

**Objetivo:** Darle sentido lógico al código validando tipos y alcance (scope).

- **Tareas:**
  - [ ] Implementar tabla de símbolos para rastrear las variables declaradas y su tipo (`Texto`, `Entero`, etc).
  - [ ] Validar que no se asigne un texto a una variable declarada como `Entero`.
  - [ ] Validar que no se usen variables sin haber sido declaradas previamente.
  - [ ] Reportar advertencias y errores semánticos en la consola de la GUI.
- **Entregable:** El compilador entiende el contexto y prohíbe operaciones inválidas, aumentando su robustez.

---

## Sprint 4: Pulido Final y UI VSCode

**Objetivo:** Refinar el software, mejorar la experiencia de usuario en la interfaz visual y realizar pruebas finales.

- **Tareas:**
  - [ ] Añadir "Resaltado de Sintaxis" básico al área de texto de Tkinter (colorear palabras clave automáticamente al estilo VSCode).
  - [ ] Añadir numeración de líneas al campo de texto.
  - [ ] Ejecutar pruebas con múltiples combinaciones de código erróneo para evaluar el manejo de fallos.
  - [ ] Refactorización de código y empaquetado final (`main.py` depurado).
- **Entregable:** Versión 1.0 del Compilador Costeñol, estable y con interfaz profesional.
