import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os

# Asegurar que podemos importar el lexer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.lexer.scanner import tokenize, LexicalError
from src.parser.parser import Parser, SyntaxErrorCosteñol
from src.semantic.symbol_table import SemanticErrorCosteñol

class CompilerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compilador Costeñol - IDE")
        self.geometry("900x650")
        
        # Colores estilo VSCode Dark Theme
        self.bg_color = "#1E1E1E"
        self.fg_color = "#D4D4D4"
        self.panel_bg = "#252526"
        self.highlight_bg = "#333333"
        self.accent_color = "#0E639C" # Azul de VSCode
        self.error_color = "#F48771"
        
        self.configure(bg=self.bg_color)
        
        self._configurar_estilos()
        self._crear_widgets()
        
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
        
        # Área de texto con scroll
        self.editor = scrolledtext.ScrolledText(editor_frame, 
                                                bg=self.bg_color, 
                                                fg=self.fg_color,
                                                insertbackground=self.fg_color, # Color del cursor
                                                font=('Consolas', 12),
                                                borderwidth=0,
                                                undo=True, # Permite Ctrl+Z
                                                padx=10, pady=10)
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Código inicial de ejemplo
        codigo_ejemplo = "num1 Entero;\nnombre = Captura.Texto();\nMensaje.Texto(\"Hola Mundo\");"
        self.editor.insert(tk.END, codigo_ejemplo)
        
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
        scrollbar = ttk.Scrollbar(bottom_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Área de mensajes de error
        self.lbl_error = tk.Label(bottom_frame, text="", bg=self.panel_bg, fg=self.error_color, font=('Consolas', 10, 'bold'))
        self.lbl_error.pack(fill=tk.X, pady=2)

    def analizar_codigo(self):
        # Limpiar tabla y errores previos
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.lbl_error.config(text="")
        
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
                
            # 2. Análisis Sintáctico
            parser = Parser(tokens)
            parser.parse()
            
            msg = f"✅ Análisis Léxico y Sintáctico exitoso. {len(tokens)} tokens validados."
            self.lbl_error.config(text=msg, fg="#89D185") # Verde VSCode
            messagebox.showinfo("Éxito", msg)
            
        except LexicalError as e:
            self.lbl_error.config(text=str(e), fg=self.error_color)
            messagebox.showerror("Error Léxico", str(e))
        except SyntaxErrorCosteñol as e:
            # Seleccionar en la tabla el token que causó el error si es posible
            if e.token:
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
            # Seleccionar en la tabla el token que causó el error si es posible
            if getattr(e, 'token', None):
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
