import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os
import ctypes

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
        
        btn_run = tk.Button(top_frame, text="▶ Analizar Código", 
                            bg=self.accent_color, fg="white", 
                            font=('Segoe UI', 10, 'bold'),
                            borderwidth=0, padx=15, pady=5,
                            command=self.analizar_codigo,
                            cursor="hand2")
        btn_run.pack(side=tk.LEFT, padx=10, pady=5)
        
        btn_close = tk.Button(top_frame, text="⏹ Cerrar", 
                              bg=self.error_color, fg="white", 
                              font=('Segoe UI', 10, 'bold'),
                              borderwidth=0, padx=15, pady=5,
                              command=self.destroy,
                              cursor="hand2")
        btn_close.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # --- PANEL CENTRAL: EDITOR ---
        editor_frame = tk.Frame(self, bg=self.bg_color)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
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
        
        # Código inicial de ejemplo
        codigo_ejemplo = "num1 Entero;\nnombre = Captura.Texto();\nMensaje.Texto(\"Hola Mundo\");"
        self.editor.insert(tk.END, codigo_ejemplo)
        self.after(100, self._on_scroll)
        self.after(150, self._highlight_syntax)
        
        # --- PANEL INFERIOR: RESULTADOS / CONSOLA ---
        bottom_frame = tk.Frame(self, bg=self.panel_bg, height=250)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        bottom_frame.pack_propagate(False) # Mantener altura fija
        
        lbl_console = tk.Label(bottom_frame, text="CONSOLA DE RESULTADOS (TOKENS)", bg=self.panel_bg, fg="#858585", font=('Consolas', 9))
        lbl_console.pack(anchor=tk.W, padx=5, pady=2)
        
        # Crear tabla para tokens
        columnas = ('linea', 'columna', 'token', 'lexema')
        self.tree = ttk.Treeview(bottom_frame, columns=columnas, show='headings', selectmode="browse")
        
        self.tree.heading('linea', text='Línea')
        self.tree.heading('columna', text='Columna')
        self.tree.heading('token', text='Tipo de Token')
        self.tree.heading('lexema', text='Lexema (Valor)')
        
        self.tree.column('linea', width=50, anchor=tk.W)
        self.tree.column('columna', width=60, anchor=tk.W)
        self.tree.column('token', width=200, anchor=tk.W)
        self.tree.column('lexema', width=300, anchor=tk.W)
        
        # Scrollbar para la tabla
        tree_scrollbar = ttk.Scrollbar(bottom_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Área de mensajes de error
        self.lbl_error = tk.Label(bottom_frame, text="", bg=self.panel_bg, fg=self.error_color, font=('Consolas', 10, 'bold'))
        self.lbl_error.pack(fill=tk.X, pady=2)

    def _configurar_tags_sintaxis(self):
        # Colores
        self.editor.tag_configure("TIPO_DATO", foreground="#569CD6") # Azul
        self.editor.tag_configure("COMANDO_IO", foreground="#DCDCAA") # Amarillo
        self.editor.tag_configure("CADENA_TEXTO", foreground="#CE9178") # Naranja
        self.editor.tag_configure("NUMERO", foreground="#B5CEA8") # Verde
        self.editor.tag_configure("OPERADOR", foreground="#D4D4D4") # Gris claro
        
        # Tag para subrayado de errores
        self.editor.tag_configure("ERROR_LINEA", underline=True, underlinefg=self.error_color)

    def _on_key_release(self, event=None):
        self._highlight_syntax()
        self.linenumbers.redraw()

    def _on_scroll(self, event=None):
        self.linenumbers.redraw()

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
                
                if t.type == "TIPO_DATO":
                    self.editor.tag_add("TIPO_DATO", start_idx, end_idx)
                elif t.type == "COMANDO_IO":
                    self.editor.tag_add("COMANDO_IO", start_idx, end_idx)
                elif t.type == "CADENA_TEXTO":
                    self.editor.tag_add("CADENA_TEXTO", start_idx, end_idx)
                elif t.type in ["NUMERO_ENTERO", "NUMERO_REAL"]:
                    self.editor.tag_add("NUMERO", start_idx, end_idx)
                elif t.type in ["OPERADOR_ASIGNACION", "OPERADOR_ARITMETICO"]:
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
        # Limpiar tabla, errores previos y subrayado
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.lbl_error.config(text="")
        self.editor.tag_remove("ERROR_LINEA", "1.0", tk.END)
        
        # Asegurar que el resaltado esté fresco
        self._highlight_syntax()
        
        # Obtener código
        codigo = self.editor.get("1.0", tk.END)
        
        if not codigo.strip():
            return
            
        try:
            # 1. Análisis Léxico
            tokens = tokenize(codigo)
            
            # Poblar tabla
            for t in tokens:
                self.tree.insert('', tk.END, values=(t.line, t.column, t.type, t.value))
                
            # 2. Análisis Sintáctico y Semántico
            parser = Parser(tokens)
            parser.parse()
            
            self._ultimo_error = None  # Resetear historial de errores en éxito
            msg = f"✅ aro, esa era — {len(tokens)} tokens validados."
            self.lbl_error.config(text=msg, fg="#89D185") # Verde VSCode
            messagebox.showinfo("monocuco 🎉", msg)
            
        except LexicalError as e:
            error_key = str(e)
            if self._ultimo_error == error_key:
                # ¡Mismo error dos veces! — "joda rosa vas a seguir?"
                self.editor.delete("1.0", tk.END)
                self.editor.insert(tk.END, "num1 Entero;\nnombre = Captura.Texto();\nMensaje.Texto(\"Hola Mundo\");")
                self._ultimo_error = None
                self.lbl_error.config(text="joda rosa vas a seguir? — Se reinició el código de ejemplo.", fg="#FFCC00")
                return
            self._ultimo_error = error_key
            self.lbl_error.config(text=str(e), fg=self.error_color)
            messagebox.showerror("Error Léxico", str(e))
        except SyntaxErrorCosteñol as e:
            error_key = str(e.message)
            if self._ultimo_error == error_key:
                self.editor.delete("1.0", tk.END)
                self.editor.insert(tk.END, "num1 Entero;\nnombre = Captura.Texto();\nMensaje.Texto(\"Hola Mundo\");")
                self._ultimo_error = None
                self.lbl_error.config(text="joda rosa vas a seguir? — Se reinició el código de ejemplo.", fg="#FFCC00")
                return
            self._ultimo_error = error_key
            if e.token:
                self._marcar_error_en_texto(e.token)
                for item in self.tree.get_children():
                    val = self.tree.item(item, 'values')
                    if int(val[0]) == e.token.line and int(val[1]) == e.token.column:
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        self.tree.see(item)
                        break
            self.lbl_error.config(text=str(e.message), fg=self.error_color)
            messagebox.showerror("Error Sintáctico", str(e.message))
        except SemanticErrorCosteñol as e:
            error_key = str(e.message)
            if self._ultimo_error == error_key:
                self.editor.delete("1.0", tk.END)
                self.editor.insert(tk.END, "num1 Entero;\nnombre = Captura.Texto();\nMensaje.Texto(\"Hola Mundo\");")
                self._ultimo_error = None
                self.lbl_error.config(text="joda rosa vas a seguir? — Se reinició el código de ejemplo.", fg="#FFCC00")
                return
            self._ultimo_error = error_key
            if getattr(e, 'token', None):
                self._marcar_error_en_texto(e.token)
                for item in self.tree.get_children():
                    val = self.tree.item(item, 'values')
                    if int(val[0]) == e.token.line and int(val[1]) == e.token.column:
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        self.tree.see(item)
                        break
            self.lbl_error.config(text=str(e.message), fg=self.error_color)
            messagebox.showerror("Error Semántico", str(e.message))
            
def start_app():
    try:
        app = CompilerGUI()
        app.mainloop()
    except KeyboardInterrupt:
        # Cierre forzado silencioso
        pass

if __name__ == "__main__":
    start_app()
