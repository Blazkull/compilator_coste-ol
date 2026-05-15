# Compilador "COSTEÑOL" 🦀

Un compilador visual y educativo desarrollado en **Python** con **Tkinter**, diseñado para analizar léxica, sintáctica y semánticamente el lenguaje ficticio **"Costeñol"**: un lenguaje de programación inspirado en el habla costeña colombiana.

---

## 🗂️ Estructura del Proyecto

```text
compilator_costeñol/
├── docs/                   # Documentación teórica y manual de uso
├── src/
│   ├── gui/                # Interfaz gráfica (estilo VSCode)
│   ├── lexer/
│   │   ├── tokens.py       # Definición de tokens y Regex maestro
│   │   └── scanner.py      # Motor de tokenización (escaneo)
│   ├── parser/
│   │   └── parser.py       # Parser de Descenso Recursivo + Análisis Semántico
│   ├── semantic/
│   │   └── symbol_table.py # Tabla de Símbolos y errores semánticos
│   └── main.py             # Punto de entrada de la aplicación
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   └── test_semantic.py
├── requirements.txt
└── run_tests.py
```

---

## ⚙️ Instalación y Ejecución

1. **Clonar el repositorio** y abrir una terminal en la raíz del proyecto.
2. **Activar el entorno virtual:**
   - Windows:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```
3. **Instalar dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```
4. **Iniciar la interfaz gráfica:**
   ```powershell
   python src/main.py
   ```

---

## 🔬 Cómo Funciona el Compilador

El compilador procesa el código Costeñol en **tres fases secuenciales**:

```
Código fuente → [LÉXICO] → Tokens → [SINTÁCTICO] → AST → [SEMÁNTICO] → OK / Error
```

### Fase 1 — Análisis Léxico (Scanner)

El módulo `src/lexer/scanner.py` recorre el código fuente carácter a carácter usando un **Regex maestro** construido en `tokens.py`. Descompone el texto en una lista de **Tokens**, donde cada token tiene:

- **Tipo** (ej. `IDENTIFICADOR`, `TIPO_DATO`)
- **Lexema** — la palabra o símbolo exacto (ej. `num1`, `Entero`)
- **Línea y Columna** de aparición

Si encuentra un carácter no reconocido (ej. `@`, `#`), lanza un `LexicalError` con la posición exacta del problema.

#### Tokens reconocidos

| Token | Patrón (Regex) | Ejemplos |
|---|---|---|
| `TIPO_DATO` | `Texto \| Entero \| Real \| Logico` | `Entero`, `Texto`, `Real`, `Logico` |
| `COMANDO_IO` | `Captura \| Mensaje` | `Captura`, `Mensaje` |
| `IDENTIFICADOR` | `[a-zA-Z_][a-zA-Z0-9_]*` | `num1`, `nombre`, `resultado` |
| `NUMERO_REAL` | `\d+,\d+` | `3,14`, `2,718` *(coma como separador decimal)* |
| `NUMERO_ENTERO` | `\d+` | `10`, `200`, `0` |
| `CADENA_TEXTO` | `"..."` | `"Hola Mundo"`, `"Costeñol"` |
| `OPERADOR_ASIGNACION` | `=` | `=` |
| `OPERADOR_ARITMETICO` | `+ - * /` | `+`, `-`, `*`, `/` |
| `SEPARADOR` | `.` | `.` *(en `Mensaje.Texto`)* |
| `DELIMITADOR_FIN` | `;` | `;` |
| `PARENTESIS_ABRE` | `(` | `(` |
| `PARENTESIS_CIERRA` | `)` | `)` |
| `COMA` | `,` | `,` *(también separador de argumentos)* |

> **Nota de precedencia:** El Regex maestro tiene orden estricto. `TIPO_DATO` y `COMANDO_IO` se procesan antes que `IDENTIFICADOR` para evitar que palabras reservadas como `Entero` sean clasificadas como identificadores. `NUMERO_REAL` se procesa antes que `NUMERO_ENTERO` por la misma razón.

---

### Fase 2 — Análisis Sintáctico (Parser)

El módulo `src/parser/parser.py` implementa un **Parser de Descenso Recursivo** que valida el orden correcto de los tokens. El parser reconoce **4 tipos de sentencias**:

#### Regla 1 — Declaración de Variable
```
[IDENTIFICADOR] [TIPO_DATO] ;
```
Ejemplo: `num1 Entero;` | `nombre Texto;` | `pi Real;`

#### Regla 2 — Asignación Matemática
```
[IDENTIFICADOR] = [EXPRESION] ;
```
Donde `EXPRESION` puede ser: un número, una variable, una cadena, o una expresión aritmética con paréntesis.

Ejemplo: `res = 10 + (num1 * 2);`

#### Regla 3 — Captura de Entrada
```
[IDENTIFICADOR] = Captura . [TIPO_DATO] ( ) ;
```
Ejemplo: `nombre = Captura.Texto();` | `edad = Captura.Entero();`

#### Regla 4 — Mensaje de Salida
```
Mensaje . [TIPO_DATO] ( [CADENA_TEXTO | IDENTIFICADOR] (, [CADENA_TEXTO | IDENTIFICADOR])* ) ;
```
Ejemplo: `Mensaje.Texto("Hola Mundo");` | `Mensaje.Entero(resultado);` | `Mensaje.Texto("Nombre:", nombre);`

---

### Fase 3 — Análisis Semántico

El análisis semántico se ejecuta **dentro del Parser** usando la **Tabla de Símbolos** (`src/semantic/symbol_table.py`). La tabla registra cada variable con su tipo al momento de declararla y verifica la coherencia de tipos en cada uso posterior.

#### Reglas Semánticas Implementadas

**RS-01 — Sin redeclaración de variables**
> No se puede declarar dos veces la misma variable en el mismo programa.
```
✅ num1 Entero;
❌ num1 Texto;   → Error: La variable 'num1' ya fue declarada previamente.
```

**RS-02 — Uso de variable no declarada**
> Toda variable debe haber sido declarada antes de ser usada en una asignación o expresión.
```
❌ resultado = 10;   → Error: La variable 'resultado' no ha sido declarada.
```

**RS-03 — Compatibilidad de tipos en asignación**
> El tipo de la expresión del lado derecho debe coincidir con el tipo de la variable. La única excepción permitida es asignar un `Entero` a una variable `Real` (promoción de tipo).
```
✅ num1 Real; num1 = 5;          → OK (Entero → Real, promoción permitida)
❌ num1 Entero; num1 = "Hola";   → Error: No se puede asignar 'Texto' a 'Entero'.
```

**RS-04 — Compatibilidad de tipos en Captura**
> El tipo declarado en `Captura.TipoDato()` debe coincidir exactamente con el tipo de la variable receptora.
```
✅ edad Entero; edad = Captura.Entero();   → OK
❌ pi Real; pi = Captura.Texto();          → Error: Se intenta capturar un 'Texto' en 'pi' de tipo 'Real'.
```

**RS-05 — Compatibilidad de tipos en Mensaje**
> `Mensaje.Entero()` o `Mensaje.Real()` solo pueden recibir variables de ese mismo tipo. `Mensaje.Texto()` es especial: puede recibir una cadena literal o cualquier variable (actúa como concatenación).
```
✅ Mensaje.Texto("Hola Mundo");       → OK (cadena literal)
✅ Mensaje.Entero(resultado);         → OK (variable Entero)
✅ Mensaje.Texto(nombre, apellido);   → OK (variables de cualquier tipo)
❌ num1 Texto; Mensaje.Entero(num1);  → Error: 'Mensaje.Entero' no puede imprimir 'num1' de tipo 'Texto'.
❌ Mensaje.Entero("Hola");            → Error: 'Mensaje.Entero' no puede imprimir cadena de Texto directa.
```

**RS-06 — Prohibición de aritmética con Texto**
> No se permiten operaciones aritméticas (`+ - * /`) si algún operando es de tipo `Texto`.
```
✅ res = 10 + 5;           → OK (Entero + Entero)
✅ res = 3,14 * 2;         → OK (Real * Entero → Real)
❌ res = nombre + 5;       → Error: No se permiten operaciones aritméticas con cadenas de Texto.
```

**RS-07 — Promoción de tipo en expresiones mixtas**
> En una expresión aritmética que mezcla `Entero` y `Real`, el resultado se promueve automáticamente a `Real`.
```
✅ pi Real; pi = 3 + 0,14;   → OK, resultado inferido como Real
```

---

## 🧪 Ejercicios de Prueba Básicos

Puedes copiar estos ejemplos directamente en el editor de la interfaz gráfica (o en los tests) para verificar el comportamiento del compilador.

### ✅ Ejercicio 1 — Programa mínimo válido
```
num1 Entero;
num1 = Captura.Entero();
Mensaje.Entero(num1);
```
**Resultado esperado:** Sin errores. El compilador reconoce una declaración, una captura y un mensaje correctamente tipados.

---

### ✅ Ejercicio 2 — Saludo con texto
```
nombre Texto;
nombre = Captura.Texto();
Mensaje.Texto("Hola:", nombre);
```
**Resultado esperado:** Sin errores. `Mensaje.Texto` acepta múltiples argumentos separados por coma.

---

### ✅ Ejercicio 3 — Operación aritmética con promoción de tipo
```
a Entero;
b Real;
resultado Real;
a = 5;
b = 1,5;
resultado = a + b;
Mensaje.Real(resultado);
```
**Resultado esperado:** Sin errores. `a` (Entero) + `b` (Real) = `resultado` de tipo `Real`. La promoción de tipo es válida.

---

### ✅ Ejercicio 4 — Programa completo
```
base Entero;
altura Real;
area Real;
base = Captura.Entero();
altura = Captura.Real();
area = base * altura;
Mensaje.Real(area);
```
**Resultado esperado:** Sin errores. Mezcla de captura, expresión aritmética y mensaje de salida.

---

### ❌ Ejercicio 5 — Error semántico: variable no declarada
```
resultado = 100;
```
**Resultado esperado:** `Error Semántico` — La variable `resultado` no ha sido declarada.

---

### ❌ Ejercicio 6 — Error semántico: tipo incompatible en asignación
```
num1 Entero;
num1 = "Hola loco";
```
**Resultado esperado:** `Error Semántico` — No se puede asignar `Texto` a `num1` de tipo `Entero`.

---

### ❌ Ejercicio 7 — Error semántico: Captura con tipo incorrecto
```
edad Entero;
edad = Captura.Texto();
```
**Resultado esperado:** `Error Semántico` — Se intenta capturar un `Texto` en la variable `edad` de tipo `Entero`.

---

### ❌ Ejercicio 8 — Error semántico: aritmética con texto
```
nombre Texto;
res Entero;
nombre = "costeño";
res = nombre + 10;
```
**Resultado esperado:** `Error Semántico` — No se permiten operaciones aritméticas con cadenas de Texto.

---

### ❌ Ejercicio 9 — Error sintáctico: orden incorrecto en declaración
```
Entero num1;
```
**Resultado esperado:** `Error Sintáctico` — Toda sentencia debe empezar con un Identificador o `Mensaje`.

---

### ❌ Ejercicio 10 — Error sintáctico: falta el punto y coma
```
num1 Entero
num1 = 5;
```
**Resultado esperado:** `Error Sintáctico` — Se esperaba `;` pero se encontró `IDENTIFICADOR ('num1')`.

---

### ❌ Ejercicio 11 — Error léxico: carácter ilegal
```
num1 Entero;
num1 @ 5;
```
**Resultado esperado:** `Error Léxico` — Carácter ilegal `@` en línea 2, columna 6.

---

## 🧬 Ejecutar Pruebas Automatizadas

El proyecto incluye **21 pruebas unitarias** organizadas en tres archivos:

```powershell
python run_tests.py
```

O con el runner estándar de Python:

```powershell
python -m unittest discover -s tests -v
```

| Archivo de test | Cobertura |
|---|---|
| `tests/test_lexer.py` | Tokenización correcta, errores léxicos, números reales |
| `tests/test_parser.py` | Declaraciones, asignaciones, capturas, mensajes, errores sintácticos |
| `tests/test_semantic.py` | Redeclaración, uso no declarado, tipos incompatibles, promoción de tipo |

---

## 📚 Documentación Adicional

- **Manual de uso de la interfaz:** [`docs/manual_de_uso.md`](docs/manual_de_uso.md)
- **Arquitectura del proyecto:** [`docs/arquitectura.md`](docs/arquitectura.md)
- **Hoja de ruta (sprints):** [`docs/sprints.md`](docs/sprints.md)

---

*Proyecto académico orientado al aprendizaje de la teoría de compiladores — Lenguaje Costeñol 🦀*
