# Manual de Uso: Compilador "COSTEÑOL"

Bienvenido al manual de uso del compilador visual para el lenguaje Costeñol. Esta guía te explicará cómo utilizar la interfaz gráfica para analizar tu código.

## 1. Conociendo la Interfaz (Estilo VSCode)

Al iniciar la aplicación (`python src/main.py`), se abrirá una ventana con un tema oscuro similar a Visual Studio Code. La pantalla se divide en tres áreas principales:

1. **Área de Edición (Editor):** Un gran bloque de texto en la parte superior donde podrás escribir múltiples líneas de código en Costeñol. Contará con numeración de líneas a la izquierda.
2. **Panel de Controles:** Un área en el centro/arriba que contiene los botones de acción, principalmente el botón **"Analizar Código"**.
3. **Consola de Resultados (Output / Terminal):** Un panel en la parte inferior (o lateral) que mostrará una tabla detallada con los resultados del análisis léxico y sintáctico, o los mensajes de error correspondientes.

## 2. Escribiendo Código en Costeñol

El lenguaje tiene una sintaxis estricta que debes respetar para evitar errores de compilación. Aquí tienes las reglas básicas que el compilador entiende:

### A. Declaración de Variables
Debes indicar el nombre de la variable, seguido del tipo de dato, y finalizar obligatoriamente con punto y coma `;`.
- Tipos soportados: `Texto`, `Entero`, `Real`, `Logico`
- Ejemplo: `num1 Entero; nombre Texto; n1 Real; asis Logico;`

### B. Asignación de Datos
Puedes asignar valores matemáticos o de texto a variables existentes.
- Ejemplo: `A = b;`
- Ejemplo Matemático: `suma = num1 + (num2 * num3);`
- Ejemplo de Texto: `nombre = "Alejandra";`
- Ejemplo de Real: `pi = 3,1416;` *(Nota: Usa coma para decimales)*

### C. Lectura de Datos (Input)
Para simular que se pide un dato al usuario, se usa el comando `Captura`.
- Formato: `Captura.<TipoDato>();`
- Ejemplo: `nombre = Captura.Texto();`
- Ejemplo: `num1 = Captura.Real();`

### D. Escritura de Datos (Output)
Para imprimir texto en pantalla, se usa el comando `Mensaje`.
- Formato: `Mensaje.Texto("<tu texto>");`
- Ejemplo: `Mensaje.Texto("Esto es una prueba");`

### E. Ejemplos de Uso Incorrecto (Errores Comunes)
Para diferenciar claramente el buen uso del mal uso, aquí tienes ejemplos de lo que **NO debes hacer**, ya que generará errores léxicos o sintácticos:

1. **Olvidar el punto y coma (;) al final:**
   - ❌ Incorrecto: `num1 Entero` (Falta el `;`)
   - ✅ Correcto: `num1 Entero;`
2. **Usar tipos de datos que no existen:**
   - ❌ Incorrecto: `nombre String;` (String no es válido en Costeñol).
   - ✅ Correcto: `nombre Texto;`
3. **Declarar variables con símbolos extraños:**
   - ❌ Incorrecto: `num@1 Entero;` (El símbolo `@` no está permitido).
   - ✅ Correcto: `num1 Entero;`
4. **Mala escritura de Comandos Reservados:**
   - ❌ Incorrecto: `captura.Entero();` (La `C` debe ser mayúscula).
   - ✅ Correcto: `Captura.Entero();`
5. **Usar punto en lugar de coma para decimales:**
   - ❌ Incorrecto: `pi = 3.1416;` (En Costeñol el decimal lleva coma).
   - ✅ Correcto: `pi = 3,1416;`

## 3. Realizando el Análisis

1. Escribe tu código (o pega uno de los ejemplos anteriores) en el **Área de Edición**.
2. Haz clic en el botón **"Analizar Código"** (o "Análisis Léxico").
3. Observa la **Consola de Resultados** en la parte inferior.
   - Si el código no tiene caracteres extraños, verás una tabla indicando línea por línea cómo el compilador ha clasificado cada palabra (ej. `num1 -> IDENTIFICADOR`, `Entero -> TIPO_DATO`).
   - Si introduces un símbolo que no pertenece al lenguaje (como un `@` o un `&`), la consola arrojará un **Error Léxico** indicando en qué línea y columna te equivocaste.

## 4. Solución de Problemas Frecuentes
- **No se detectan los decimales:** Recuerda que en Costeñol, los decimales (Reales) se escriben con coma `,` (ej. `3,14`), no con punto. El punto se reserva para los métodos como `Captura.Texto()`.
- **Falta el punto y coma:** Si olvidas un `;` al final de una instrucción, el analizador sintáctico (Fase 2) te lo indicará como un error grave.
