import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os
import ctypes
import threading
import queue

# Asegurar que podemos importar el lexer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.lexer.scanner import tokenize, LexicalError
from src.parser.parser import Parser, SyntaxErrorCosteñol
from src.semantic.symbol_table import SemanticErrorCosteñol

# Le decimos a Windows que esta es una app independiente, antes de cualquier ventana
try:
    myappid = 'compilador.costenol.ide.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

class LineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        self.delete("all")
        i = self.textwidget.index("@0,0")
        while True :
            dline = self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, fill="#858585", font=('Consolas', 11))
            i = self.textwidget.index("%s+1line" % i)

class CompilerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compilador Costeñol - IDE")
        self.geometry("900x650")
        
        # Guardamos el último error para detectar si el usuario repite el mismo error dos veces
        self._ultimo_error = None
        
        # Colores estilo VSCode Dark Theme
        self.bg_color = "#1E1E1E"
        self.fg_color = "#D4D4D4"
        self.panel_bg = "#252526"
        self.highlight_bg = "#333333"
        self.accent_color = "#0E639C" # Azul de VSCode
        self.error_color = "#F48771"
        self.line_num_bg = "#1E1E1E"
        
        self.configure(bg=self.bg_color)
        
        # Cargar y establecer el icono
        try:
            ico_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logo', 'Logo_costenol.ico'))
            png_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logo', 'Logo_costenol.png'))
            
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
            elif os.path.exists(png_path):
                img_icon = tk.PhotoImage(file=png_path)
                self.iconphoto(True, img_icon)
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")
        
        self._configurar_estilos()
        self._crear_widgets()
        self._configurar_tags_sintaxis()
        
    def _configurar_estilos(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Configurar Treeview (Tabla)
        style.configure("Treeview", 
                        background=self.panel_bg, 
                        foreground=self.fg_color, 
                        fieldbackground=self.panel_bg,
                        borderwidth=0,
                        rowheight=25)
        style.configure("Treeview.Heading", 
                        background=self.highlight_bg, 
                        foreground=self.fg_color, 
                        borderwidth=0,
                        font=('Consolas', 10, 'bold'))
        style.map('Treeview', background=[('selected', self.accent_color)])
        
        # Configurar Scrollbar
        style.configure("Vertical.TScrollbar", 
                        background=self.highlight_bg, 
                        troughcolor=self.bg_color,
                        bordercolor=self.bg_color,
                        arrowcolor=self.fg_color)
                        
    def _crear_widgets(self):
        # --- PANEL SUPERIOR: BOTONES ---
        top_frame = tk.Frame(self, bg=self.highlight_bg, height=40)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        top_frame.pack_propagate(False)
        
        btn_run = tk.Button(top_frame, text="🔍 Analizar", 
                            bg=self.accent_color, fg="white", 
                            font=('Segoe UI', 10, 'bold'),
                            borderwidth=0, padx=15, pady=5,
                            command=self.analizar_codigo,
                            cursor="hand2")
        btn_run.pack(side=tk.LEFT, padx=10, pady=5)

        btn_exec = tk.Button(top_frame, text="▶ Ejecutar", 
                            bg="#28A745", fg="white", 
                            font=('Segoe UI', 10, 'bold'),
                            borderwidth=0, padx=15, pady=5,
                            command=self.ejecutar_codigo,
                            cursor="hand2")
        btn_exec.pack(side=tk.LEFT, padx=5, pady=5)

        btn_tokens = tk.Button(top_frame, text="🔍 Ver Tokens", 
                               bg=self.highlight_bg, fg=self.fg_color, 
                               font=('Segoe UI', 10),
                               borderwidth=0, padx=10, pady=5,
                               command=lambda: self.notebook.select(self.tab_tokens),
                               cursor="hand2")
        btn_tokens.pack(side=tk.RIGHT, padx=20, pady=5)
        
        btn_close = tk.Button(top_frame, text="⏹ Cerrar", 
                              bg=self.error_color, fg="white", 
                              font=('Segoe UI', 10, 'bold'),
                              borderwidth=0, padx=15, pady=5,
                              command=self.destroy,
                              cursor="hand2")
        btn_close.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # --- CONTENEDOR PRINCIPAL: SIDEBAR + EDITOR ---
        main_container = tk.Frame(self, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- BARRA LATERAL (CONTROL DE LA VUELTA) ---
        self.sidebar = tk.Frame(main_container, bg=self.panel_bg, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        lbl_sidebar = tk.Label(self.sidebar, text="CONTROL DE LA VUELTA", 
                               bg=self.highlight_bg, fg=self.fg_color, 
                               font=('Segoe UI', 9, 'bold'), pady=10)
        lbl_sidebar.pack(fill=tk.X)

        # Botones de acción en la barra lateral
        sidebar_btns = tk.Frame(self.sidebar, bg=self.panel_bg)
        sidebar_btns.pack(fill=tk.X, pady=5)

        self.btn_pack = tk.Button(sidebar_btns, text="📦 Empaquetar", 
                                  bg=self.accent_color, fg="white",
                                  font=('Segoe UI', 9), borderwidth=0,
                                  command=self.empaquetar_codigo, cursor="hand2")
        self.btn_pack.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Lista de archivos empaquetados
        self.tree_packages = ttk.Treeview(self.sidebar, show='tree', selectmode="browse")
        self.tree_packages.pack(fill=tk.BOTH, expand=True, padx=2, pady=5)
        self.tree_packages.bind("<Double-1>", self._on_package_double_click)

        # --- PANEL CENTRAL: EDITOR ---
        editor_frame = tk.Frame(main_container, bg=self.bg_color)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        lbl_editor = tk.Label(editor_frame, text="EDITOR COSTEÑOL", bg=self.bg_color, fg="#858585", font=('Consolas', 9))
        lbl_editor.pack(anchor=tk.W)
        
        # Contenedor para línea de números y texto
        text_container = tk.Frame(editor_frame, bg=self.bg_color)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        self.linenumbers = LineNumbers(text_container, width=30, bg=self.line_num_bg, highlightthickness=0)
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Área de texto con scroll
        self.editor = tk.Text(text_container, 
                              bg=self.bg_color, 
                              fg=self.fg_color,
                              insertbackground=self.fg_color, # Color del cursor
                              font=('Consolas', 12),
                              borderwidth=0,
                              undo=True, # Permite Ctrl+Z
                              padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self.editor.yview)
        self.editor.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.linenumbers.attach(self.editor)
        
        # Bindings para sincronizar números de línea y resaltado
        self.editor.bind("<KeyRelease>", self._on_key_release)
        self.editor.bind("<MouseWheel>", self._on_scroll)
        self.editor.bind("<Button-1>", self._on_scroll)
        self.editor.bind("<Return>", self._on_scroll)
        self.editor.bind("<Configure>", self._on_scroll)
        self.editor.bind("<Key>", self._on_scroll)
        self.editor.bind("<<Modified>>", self._on_scroll)
        
        # Código inicial de ejemplo
        codigo_ejemplo = """// Ejemplo Costeñol: Contador
contador Entero;
limite Entero;

contador = 0;
Mensaje.Texto("Hasta cuanto quieres contar, mi llave?");
limite = Captura.Entero();

Mientras (contador < limite) {
    contador = contador + 1;
    Mensaje.Texto("Contando:", contador);
}

Si (limite > 10) {
    Mensaje.Texto("Joda, contaste bastante!");
} Sino {
    Mensaje.Texto("Breve, eso fue rápido.");
}"""
        self.editor.insert(tk.END, codigo_ejemplo)
        self.after(100, self._on_scroll)
        self.after(150, self._highlight_syntax)
        
        # --- PANEL INFERIOR: RESULTADOS / CONSOLA (Notebook) ---
        # Área de mensajes de error (encima del notebook)
        self.lbl_error = tk.Label(self, text="", bg=self.bg_color, fg=self.error_color, font=('Consolas', 10, 'bold'))
        self.lbl_error.pack(fill=tk.X, side=tk.TOP, pady=2)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)
        
        # PESTAÑA 1: TERMINAL
        self.tab_terminal = tk.Frame(self.notebook, bg=self.panel_bg)
        self.notebook.add(self.tab_terminal, text=" 💻 TERMINAL ")
        
        # Frame para entrada del usuario (empaquetar primero al fondo)
        input_frame = tk.Frame(self.tab_terminal, bg=self.panel_bg)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        tk.Label(input_frame, text=" > ", bg=self.panel_bg, fg=self.accent_color, font=('Consolas', 12, 'bold')).pack(side=tk.LEFT)
        
        self.terminal_input = tk.Entry(input_frame, 
                                     bg=self.panel_bg, 
                                     fg="white", 
                                     insertbackground="white",
                                     font=('Consolas', 12),
                                     borderwidth=0)
        self.terminal_input.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.terminal_input.bind("<Return>", self._on_terminal_enter)
        self.terminal_input.config(state='disabled')
        
        # Consola de salida (ocupa el resto del espacio)
        self.terminal_output = scrolledtext.ScrolledText(self.tab_terminal, 
                                                       bg=self.panel_bg, 
                                                       fg="#CCCCCC",
                                                       font=('Consolas', 11),
                                                       borderwidth=0,
                                                       state='disabled',
                                                       padx=10, pady=5)
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        
        # PESTAÑA 2: TOKENS
        self.tab_tokens = tk.Frame(self.notebook, bg=self.panel_bg)
        self.notebook.add(self.tab_tokens, text=" 🔍 TABLA DE TOKENS ")
        
        # Crear tabla para tokens
        columnas = ('linea', 'token', 'lexema')
        self.tree = ttk.Treeview(self.tab_tokens, columns=columnas, show='headings', selectmode="browse")
        
        self.tree.heading('linea', text='Línea')
        self.tree.heading('token', text='Tipo de Token')
        self.tree.heading('lexema', text='Lexema (Valor)')
        
        self.tree.column('linea', width=70, anchor=tk.W)
        self.tree.column('token', width=200, anchor=tk.W)
        self.tree.column('lexema', width=400, anchor=tk.W)
        
        tree_scrollbar = ttk.Scrollbar(self.tab_tokens, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Variables para manejo de ejecución e hilos
        import queue
        self.input_queue = queue.Queue()
        self.executing = False
        self._ultimo_error = None
        
        # Cargar paquetes existentes
        self._refresh_package_list()

    def _on_terminal_enter(self, event):
        """Maneja cuando el usuario presiona Enter en la terminal."""
        if self.terminal_input['state'] == 'disabled':
            return
            
        val = self.terminal_input.get()
        self._append_to_terminal(val + "\n", color="white")
        self.terminal_input.delete(0, tk.END)
        self.terminal_input.config(state='disabled', bg=self.panel_bg)
        self.input_queue.put(val)

    def _append_to_terminal(self, text, color="#CCCCCC"):
        """Agrega texto a la consola de la terminal."""
        self.terminal_output.config(state='normal')
        
        # Crear un tag único para el color si no existe
        tag_name = f"color_{color.replace('#', '')}"
        self.terminal_output.tag_configure(tag_name, foreground=color)
        
        self.terminal_output.insert(tk.END, text, tag_name)
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state='disabled')

    def _request_input(self, name, var_type):
        """Callback para el intérprete cuando necesita una Captura."""
        def activate_ui():
            self.notebook.select(self.tab_terminal)
            self._append_to_terminal(f"📥 Ingrese valor para '{name}' ({var_type}): ", color="#569CD6")
            self.terminal_input.config(state='normal', bg="#3C3C3C") # Fondo más claro para indicar actividad
            self.terminal_input.focus_set()
            
        self.after(0, activate_ui)
        # Bloquea hasta que haya algo en la cola (esto está bien en el hilo secundario)
        return self.input_queue.get()

    def _configurar_tags_sintaxis(self):
        # Colores
        self.editor.tag_configure("TIPO_DATO", foreground="#569CD6") # Azul
        self.editor.tag_configure("COMANDO_IO", foreground="#DCDCAA") # Amarillo
        self.editor.tag_configure("CONTROL", foreground="#C586C0") # Púrpura
        self.editor.tag_configure("BOOLEANO", foreground="#569CD6") # Azul
        self.editor.tag_configure("CADENA_TEXTO", foreground="#CE9178") # Naranja
        self.editor.tag_configure("NUMERO", foreground="#B5CEA8") # Verde
        self.editor.tag_configure("OPERADOR", foreground="#D4D4D4") # Gris claro
        self.editor.tag_configure("COMENTARIO", foreground="#6A9955") # Verde oscuro (estilo VSCode)
        
        # Tag para subrayado de errores
        self.editor.tag_configure("ERROR_LINEA", underline=True, underlinefg=self.error_color)

    def _on_key_release(self, event=None):
        self._highlight_syntax()
        self.linenumbers.redraw()

    def _on_scroll(self, event=None):
        self.linenumbers.redraw()
        if event and event.type == "<<Modified>>":
            self.editor.edit_modified(False)

    def _highlight_syntax(self):
        # Limpiar tags actuales
        for tag in ["TIPO_DATO", "COMANDO_IO", "CADENA_TEXTO", "NUMERO", "OPERADOR", "ERROR_LINEA"]:
            self.editor.tag_remove(tag, "1.0", tk.END)
            
        codigo = self.editor.get("1.0", tk.END)
        try:
            tokens = tokenize(codigo)
            for t in tokens:
                # tk.Text usa índices de línea base 1, pero columnas base 0.
                # Nuestro lexer devuelve columnas base 1, así que restamos 1.
                tk_col = t.column - 1 
                start_idx = f"{t.line}.{tk_col}"
                end_idx = f"{t.line}.{tk_col + len(str(t.value))}"
                
                if t.type == "COMENTARIO":
                    self.editor.tag_add("COMENTARIO", start_idx, end_idx)
                elif t.type == "TIPO_DATO":
                    self.editor.tag_add("TIPO_DATO", start_idx, end_idx)
                elif t.type == "COMANDO_IO":
                    self.editor.tag_add("COMANDO_IO", start_idx, end_idx)
                elif t.type == "CONTROL":
                    self.editor.tag_add("CONTROL", start_idx, end_idx)
                elif t.type == "BOOLEANO":
                    self.editor.tag_add("BOOLEANO", start_idx, end_idx)
                elif t.type == "CADENA_TEXTO":
                    self.editor.tag_add("CADENA_TEXTO", start_idx, end_idx)
                elif t.type in ["NUMERO_ENTERO", "NUMERO_REAL"]:
                    self.editor.tag_add("NUMERO", start_idx, end_idx)
                elif t.type in ["OPERADOR_ASIGNACION", "OPERADOR_ARITMETICO", "COMPARADOR"]:
                    self.editor.tag_add("OPERADOR", start_idx, end_idx)
        except LexicalError:
            # Si hay error léxico mientras escribe, colorear lo que se pueda
            pass

    def _marcar_error_en_texto(self, token):
        if not token: return
        tk_col = token.column - 1
        start_idx = f"{token.line}.{tk_col}"
        end_idx = f"{token.line}.{tk_col + len(str(token.value))}"
        self.editor.tag_add("ERROR_LINEA", start_idx, end_idx)
        # Hacer scroll para ver el error
        self.editor.see(start_idx)

    def analizar_codigo(self):
        # Limpiar tabla, terminal, errores previos y subrayado
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.terminal_output.config(state='normal')
        self.terminal_output.delete("1.0", tk.END)
        self.terminal_output.config(state='disabled')
        self.lbl_error.config(text="")
        self.editor.tag_remove("ERROR_LINEA", "1.0", tk.END)
        
        # Asegurar que el resaltado esté fresco
        self._highlight_syntax()
        
        # Obtener código
        codigo = self.editor.get("1.0", tk.END)
        
        if not codigo.strip():
            return None
            
        try:
            # 1. Análisis Léxico
            tokens_all = tokenize(codigo)
            
            # Poblar tabla y filtrar para el parser
            tokens_for_parser = []
            for t in tokens_all:
                self.tree.insert('', tk.END, values=(t.line, t.type, t.value))
                if t.type != 'COMENTARIO':
                    tokens_for_parser.append(t)
                
            # 2. Análisis Sintáctico y Semántico
            parser = Parser(tokens_for_parser)
            ast = parser.parse()
            
            self._ultimo_error = None
            msg = f"✅ aro, esa era — {len(tokens_all)} tokens validados."
            self.lbl_error.config(text=msg, fg="#89D185")
            return ast
            
        except LexicalError as e:
            self._manejar_error(e, "Hey loco que pasa vale mia 😤")
        except SyntaxErrorCosteñol as e:
            self._manejar_error(e, "mi llave barros schelotto 🚨")
        except SemanticErrorCosteñol as e:
            self._manejar_error(e, "Joda loco estas barrilete 💀")
        return None

    def _manejar_error(self, e, titulo):
        self._ultimo_error = str(e)
        
        if hasattr(e, 'token') and e.token:
            self._marcar_error_en_texto(e.token)
            for item in self.tree.get_children():
                val = self.tree.item(item, 'values')
                if int(val[0]) == e.token.line and str(val[2]) == str(e.token.value):
                    self.tree.selection_set(item)
                    self.tree.focus(item)
                    self.tree.see(item)
                    break
                    
        self.lbl_error.config(text=str(e), fg=self.error_color)
        messagebox.showerror(titulo, str(e))

    def ejecutar_codigo(self):
        """Analiza y luego ejecuta el código en un hilo separado."""
        ast = self.analizar_codigo()
        if not ast:
            return

        from src.interpreter.interpreter import Interpreter

        self.notebook.select(self.tab_terminal)
        self._append_to_terminal("🚀 Iniciando ejecución...\n\n")
        
        def run_interpreter():
            try:
                interpreter = Interpreter(
                    output_callback=lambda m: self.after(0, self._append_to_terminal, m + "\n"),
                    input_callback=self._request_input
                )
                interpreter.execute(ast)
            except Exception as e:
                self.after(0, self._append_to_terminal, f"\n❌ ERROR EN EJECUCIÓN: {str(e)}\n", "#F48771")

        threading.Thread(target=run_interpreter, daemon=True).start()

    def empaquetar_codigo(self):
        """Genera un archivo .pqek con el AST serializado."""
        ast = self.analizar_codigo()
        if not ast:
            return

        import pickle
        from tkinter import filedialog
        
        # Crear carpeta de paquetes si no existe
        pkg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))
        if not os.path.exists(pkg_dir):
            os.makedirs(pkg_dir)

        # Pedir nombre de archivo
        file_path = filedialog.asksaveasfilename(
            initialdir=pkg_dir,
            title="Empaquetar la vuelta",
            defaultextension=".pqek",
            filetypes=(("Paquete Costeñol", "*.pqek"), ("Todos los archivos", "*.*"))
        )

        if file_path:
            try:
                datos = {
                    "version": "1.0",
                    "autor": "Blazkull",
                    "ast": ast
                }
                with open(file_path, 'wb') as f:
                    pickle.dump(datos, f)
                
                messagebox.showinfo("Control de la Vuelta", f"¡Todo firme! Archivo empaquetado en:\n{os.path.basename(file_path)}")
                self._refresh_package_list()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo empaquetar: {e}")

    def _refresh_package_list(self):
        """Actualiza la lista de archivos .pqek en la barra lateral."""
        for item in self.tree_packages.get_children():
            self.tree_packages.delete(item)
            
        pkg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))
        if os.path.exists(pkg_dir):
            for file in os.listdir(pkg_dir):
                if file.endswith(".pqek"):
                    self.tree_packages.insert('', tk.END, text=f" 📦 {file}", values=(os.path.join(pkg_dir, file),))

    def _on_package_double_click(self, event):
        """Al hacer doble clic, ejecutar el paquete .pqek."""
        item = self.tree_packages.selection()
        if not item: return
        
        file_path = self.tree_packages.item(item, 'values')[0]
        self.ejecutar_paquete(file_path)

    def ejecutar_paquete(self, file_path):
        """Carga un AST de un archivo .pqek y lo ejecuta."""
        import pickle
        from src.interpreter.interpreter import Interpreter

        try:
            with open(file_path, 'rb') as f:
                datos = pickle.load(f)
            
            ast = datos.get("ast")
            if not ast:
                raise Exception("Archivo corrupto o sin AST.")

            self.notebook.select(self.tab_terminal)
            self._append_to_terminal(f"🚀 Ejecutando paquete: {os.path.basename(file_path)}...\n")
            
            def run_interpreter():
                try:
                    interpreter = Interpreter(
                        output_callback=lambda m: self.after(0, self._append_to_terminal, m + "\n"),
                        input_callback=self._request_input
                    )
                    interpreter.execute(ast)
                except Exception as e:
                    self.after(0, self._append_to_terminal, f"\n❌ ERROR EN PAQUETE: {str(e)}\n", "#F48771")

            threading.Thread(target=run_interpreter, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error de Paquete", f"No se pudo abrir la vuelta: {e}")
            
def start_app():
    try:
        app = CompilerGUI()
        app.mainloop()
    except KeyboardInterrupt:
        # Cierre forzado silencioso
        pass

if __name__ == "__main__":
    start_app()
