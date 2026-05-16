# Compilador "COSTEÑOL" 🦀

Un IDE y compilador educativo desarrollado en **Python** con **Tkinter**, diseñado para analizar léxica, sintáctica y semánticamente el lenguaje **"Costeñol"**. Ahora incluye un motor de ejecución interactivo y sistema de empaquetado.

---

## 🗂️ Estructura del Proyecto

```text
compilator_costeñol/
├── packages/               # Archivos .pqek (Código + AST serializado)
├── src/
│   ├── gui/                # IDE con Terminal y "Control de la Vuelta"
│   ├── lexer/              # Lexer con soporte para comentarios y comparadores
│   ├── parser/             # Parser con soporte para Si/Mientras
│   ├── interpreter/        # Motor de ejecución (Visita el AST)
│   └── main.py             # Punto de entrada
├── tests/                  # Pruebas unitarias
└── README.md
```

---

## 🚀 Nuevas Funcionalidades (V4.2 - Final Sprint)

### 💻 Terminal de Alto Rendimiento
- **Entrada Continua:** El campo de texto de la terminal está siempre activo para una mejor experiencia de usuario.
- **Auto-Limpieza:** Cada vez que ejecutas un código, la terminal se limpia automáticamente para evitar confusiones con resultados anteriores.
- **Scroll Inteligente:** La salida siempre te muestra la última línea ejecutada.

### 📦 Control de la Vuelta (.pqek)
- **Empaquetado Total:** Los archivos `.pqek` ahora guardan el código fuente original. Al abrirlos desde el sidebar, recuperas tu trabajo instantáneamente.
- **Gestión de Pestañas:** Abre múltiples archivos simultáneamente y ciérralos con el nuevo botón de cierre.

### ❓ Ayuda y Ejemplos
- **Botón de Ayuda:** Acceso instantáneo a la sintaxis del lenguaje con un ejemplo funcional de contador interactivo.

### 🧠 Gramática y Lógica
- **Concatenación con Comas:** Soporte extendido para unir textos usando comas `,` en cualquier parte del código, incluyendo dentro de paréntesis.
- **Tipado Fuerte:** Validación semántica para asegurar que las operaciones se realicen entre tipos compatibles.
- **Comentarios:** Ahora puedes comentar tu código usando `//` (resaltados en verde).
- **Concatenación:** El operador de unión es la coma `,` (ej. `Respuesta = "Hola ", nombre;`). El signo `+` queda reservado solo para números.

---

## ⚙️ Instalación y Ejecución

1. **Instalar dependencias:** `pip install -r requirements.txt`
2. **Iniciar el IDE:** `python src/main.py`

---

## 🔬 Flujo del Compilador Moderno

```
Código fuente → [LÉXICO] → [SINTÁCTICO] → [AST] → [INTÉRPRETE] → EJECUCIÓN
                                         ↓
                                  [EMPAQUETADO .PQEK]
```

---

## 📚 Gramática y Reglas Semánticas

### Control de Flujo
```text
Mientras (a < 10) {
    a = a + 1;
}

Si (edad >= 18) {
    Mensaje.Texto("Pasa, mi llave");
} Sino {
    Mensaje.Texto("Pa la casa");
}
```

### Reglas Semánticas Actualizadas
- **Concatenación:** Se usa la coma `,` para unir valores en variables de tipo `Texto`. El operador `+` solo es válido para números (`Entero` y `Real`).
- **Condicionales:** Las condiciones en `Si` y `Mientras` deben evaluar a un valor `Logico`.

---

## 🧪 Ejemplo Completo: Contador
```text
// Ejemplo Costeñol: Contador con límites
limite Entero;
i Entero;

Mensaje.Texto("Hasta cuanto quieres contar, mi llave?");
limite = Captura.Entero();

i = 1;
Mientras (i <= limite) {
    Mensaje.Texto("Contando:", i);
    i = i + 1;
}

Mensaje.Texto("Breve, eso fue rápido.");
```

---

*Proyecto académico orientado al aprendizaje de la teoría de compiladores — Lenguaje Costeñol 🦀*
