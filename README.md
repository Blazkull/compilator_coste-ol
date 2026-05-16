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

## 🚀 Nuevas Funcionalidades (V3.0 - Full .pqek)

### 💻 Terminal Interactiva
El IDE cuenta con una terminal integrada que permite entrada/salida en tiempo real y ejecución multihilo.

### 📦 Control de la Vuelta (.pqek)
El formato **.pqek** es ahora el estándar universal del lenguaje:
- **Todo en uno:** Un archivo `.pqek` guarda tanto tu código fuente como el árbol (AST) listo para ejecutar.
- **Sidebar:** Gestiona tus archivos directamente desde el panel izquierdo. Al hacer doble clic, el IDE "desempaqueta" el código para editarlo.
- **Persistencia:** Guarda tus progresos con `Ctrl+S` directamente en formato de paquete.

### 🧠 Gramática Extendida
- **Control de Flujo:** Soporte para bloques `Si`, `Sino` y bucles `Mientras`.
- **Lógica:** Evaluación de comparadores (`==`, `!=`, `<`, `>`, `<=`, `>=`) y booleanos (`Verdad`, `Mentira`).
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
