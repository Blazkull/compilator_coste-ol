import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import sys
import os
import ctypes
import threading
import queue
import pickle

# Asegurar que podemos importar el lexer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.lexer.scanner import tokenize, LexicalError
from src.parser.parser import Parser, SyntaxErrorCosteñol
from src.semantic.symbol_table import SemanticErrorCosteñol

# Configuración de Windows para DPI
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
        if not self.textwidget: return
        try:
            i = self.textwidget.index("@0,0")
            while True :
                dline = self.textwidget.dlineinfo(i)
                if dline is None: break
                y = dline[1]
                linenum = str(i).split(".")[0]
                self.create_text(2, y, anchor="nw", text=linenum, fill="#858585", font=('Consolas', 11))
                i = self.textwidget.index("%s+1line" % i)
        except Exception: pass

class CompilerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compilador Costeñol - IDE")
        self.geometry("1000x750")
        
        # Colores estilo VSCode Dark Theme
        self.bg_color = "#1E1E1E"
        self.fg_color = "#D4D4D4"
        self.panel_bg = "#252526"
        self.highlight_bg = "#333333"
        self.accent_color = "#0E639C"
        self.error_color = "#F48771"
        self.line_num_bg = "#1E1E1E"
        
        self.configure(bg=self.bg_color)
        
        # Estado
        self.editors = {} # {tab_id: {editor, path, dirty, title, linenumbers}}
        self.input_queue = queue.Queue()
        self._ultimo_error = None
        
        self._configurar_estilos()
        self._crear_widgets()
        
        # Atajos de teclado
        self.bind("<Control-s>", lambda e: self.guardar_archivo())
        self.bind("<Control-S>", lambda e: self.guardar_archivo())

    def _configurar_estilos(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.highlight_bg, foreground=self.fg_color, padding=[10, 2])
        style.map("TNotebook.Tab", background=[("selected", self.bg_color)])
        style.configure("Treeview", background=self.panel_bg, foreground=self.fg_color, fieldbackground=self.panel_bg, borderwidth=0, rowheight=25)
        style.configure("Treeview.Heading", background=self.highlight_bg, foreground=self.fg_color, borderwidth=0, font=('Consolas', 10, 'bold'))
        style.map('Treeview', background=[('selected', self.accent_color)])

    def _crear_widgets(self):
        # --- TOPBAR ---
        top_frame = tk.Frame(self, bg=self.highlight_bg, height=40)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        top_frame.pack_propagate(False)
        
        btn_run = tk.Button(top_frame, text="🔍 Analizar", bg=self.accent_color, fg="white", font=('Segoe UI', 9, 'bold'), borderwidth=0, padx=10, command=self.analizar_codigo, cursor="hand2")
        btn_run.pack(side=tk.LEFT, padx=5, pady=5)

        btn_exec = tk.Button(top_frame, text="▶ Ejecutar", bg="#28A745", fg="white", font=('Segoe UI', 9, 'bold'), borderwidth=0, padx=10, command=self.ejecutar_codigo, cursor="hand2")
        btn_exec.pack(side=tk.LEFT, padx=5, pady=5)

        btn_save = tk.Button(top_frame, text="📦 Guardar .pqek", bg=self.highlight_bg, fg=self.fg_color, font=('Segoe UI', 9), borderwidth=0, padx=10, command=self.guardar_archivo, cursor="hand2")
        btn_save.pack(side=tk.LEFT, padx=5, pady=5)
        
        # --- MAIN CONTAINER ---
        main_container = tk.Frame(self, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- SIDEBAR (CONTROL DE LA VUELTA) ---
        self.sidebar = tk.Frame(main_container, bg=self.panel_bg, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        lbl_sidebar = tk.Label(self.sidebar, text="CONTROL DE LA VUELTA", bg=self.highlight_bg, fg=self.fg_color, font=('Segoe UI', 8, 'bold'), pady=5)
        lbl_sidebar.pack(fill=tk.X)

        self.tree_packages = ttk.Treeview(self.sidebar, show='tree', selectmode="browse")
        self.tree_packages.pack(fill=tk.BOTH, expand=True, padx=2, pady=5)
        self.tree_packages.bind("<Double-1>", self._on_sidebar_double_click)

        btn_refresh = tk.Button(self.sidebar, text="🔄 Refrescar", bg=self.highlight_bg, fg=self.fg_color, font=('Segoe UI', 8), borderwidth=0, command=self._refresh_package_list)
        btn_refresh.pack(fill=tk.X, padx=10, pady=5)

        # --- EDITOR AREA ---
        self.editor_frame = tk.Frame(main_container, bg=self.bg_color)
        self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.editor_notebook = ttk.Notebook(self.editor_frame)
        self.editor_notebook.pack(fill=tk.BOTH, expand=True)
        self.editor_notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # --- CONSOLE AREA ---
        self.bottom_frame = tk.Frame(self, bg=self.bg_color, height=220)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.lbl_error = tk.Label(self.bottom_frame, text="", bg=self.bg_color, fg=self.error_color, font=('Consolas', 10), pady=2)
        self.lbl_error.pack(fill=tk.X)

        self.notebook_console = ttk.Notebook(self.bottom_frame)
        self.notebook_console.pack(fill=tk.BOTH, expand=True)
        
        self.tab_terminal = tk.Frame(self.notebook_console, bg=self.panel_bg)
        self.notebook_console.add(self.tab_terminal, text=" 💻 TERMINAL ")
        self.terminal_output = scrolledtext.ScrolledText(self.tab_terminal, bg=self.panel_bg, fg="#CCCCCC", font=('Consolas', 11), borderwidth=0, state='disabled', padx=10, pady=5)
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        
        term_input_frame = tk.Frame(self.tab_terminal, bg=self.panel_bg)
        term_input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
        tk.Label(term_input_frame, text=" > ", bg=self.panel_bg, fg=self.accent_color, font=('Consolas', 12, 'bold')).pack(side=tk.LEFT)
        self.terminal_input = tk.Entry(term_input_frame, bg=self.panel_bg, fg="white", insertbackground="white", font=('Consolas', 12), borderwidth=0)
        self.terminal_input.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.terminal_input.bind("<Return>", self._on_terminal_enter)
        self.terminal_input.config(state='disabled')

        self.tab_tokens = tk.Frame(self.notebook_console, bg=self.panel_bg)
        self.notebook_console.add(self.tab_tokens, text=" 🔍 TOKENS ")
        self.tree_tokens = ttk.Treeview(self.tab_tokens, columns=('linea', 'token', 'lexema'), show='headings')
        self.tree_tokens.heading('linea', text='Línea'); self.tree_tokens.heading('token', text='Tipo'); self.tree_tokens.heading('lexema', text='Valor')
        self.tree_tokens.column('linea', width=50); self.tree_tokens.pack(fill=tk.BOTH, expand=True)

        self._refresh_package_list()
        self.add_new_editor_tab()

    def add_new_editor_tab(self, file_path=None, content=""):
        tab_frame = tk.Frame(self.editor_notebook, bg=self.bg_color)
        txt_container = tk.Frame(tab_frame, bg=self.bg_color)
        txt_container.pack(fill=tk.BOTH, expand=True)
        
        linenumbers = LineNumbers(txt_container, width=35, bg=self.line_num_bg, highlightthickness=0)
        linenumbers.pack(side=tk.LEFT, fill=tk.Y)
        
        editor = tk.Text(txt_container, bg=self.bg_color, fg=self.fg_color, insertbackground="white", font=('Consolas', 13), undo=True, borderwidth=0, padx=10, pady=10)
        editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        linenumbers.attach(editor)
        
        if content:
            editor.insert("1.0", content)
        elif file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                    editor.insert("1.0", data.get("codigo", ""))
            except Exception:
                # Si no es un pickle válido, intentar leer como texto
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        editor.insert("1.0", f.read())
                except: pass

        self._setup_editor_tags(editor)
        title = os.path.basename(file_path) if file_path else "sin_nombre.pqek"
        self.editor_notebook.add(tab_frame, text=title)
        
        tid = tab_frame.winfo_pathname(tab_frame.winfo_id())
        self.editors[tid] = {'editor': editor, 'path': file_path, 'dirty': False, 'title': title, 'linenumbers': linenumbers}
        self.editor_notebook.select(tab_frame)
        editor.bind("<KeyRelease>", lambda e: self._on_editor_change(tid))
        editor.bind("<MouseWheel>", lambda e: linenumbers.redraw())
        self.after(100, lambda: self._highlight_syntax(editor))
        self.after(110, lambda: linenumbers.redraw())

    def _setup_editor_tags(self, editor):
        tags = {"TIPO_DATO":"#569CD6", "COMANDO_IO":"#DCDCAA", "CONTROL":"#C586C0", "BOOLEANO":"#569CD6", "CADENA_TEXTO":"#CE9178", "NUMERO":"#B5CEA8", "OPERADOR":"#D4D4D4", "COMENTARIO":"#6A9955"}
        for t, c in tags.items(): editor.tag_configure(t, foreground=c)
        editor.tag_configure("ERROR_LINEA", underline=True, underlinefg=self.error_color)

    def get_current_editor_info(self):
        sel = self.editor_notebook.select()
        return self.editors.get(sel)

    def _on_editor_change(self, tid):
        info = self.editors.get(tid)
        if info and not info['dirty']:
            info['dirty'] = True
            self.editor_notebook.tab(tid, text=f"• {info['title']}")
        self._highlight_syntax(info['editor'])
        info['linenumbers'].redraw()

    def _on_tab_changed(self, e):
        info = self.get_current_editor_info()
        if info: info['linenumbers'].redraw(); self._highlight_syntax(info['editor'])

    def guardar_archivo(self):
        info = self.get_current_editor_info()
        if not info: return
        
        # Primero analizamos para tener el AST actualizado
        ast = self.analizar_codigo()
        
        path = info['path']
        if not path:
            pkg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))
            if not os.path.exists(pkg_dir): os.makedirs(pkg_dir)
            path = filedialog.asksaveasfilename(initialdir=pkg_dir, defaultextension=".pqek", filetypes=[("Paquete Costeñol", "*.pqek")])
            if not path: return
            info['path'] = path
            info['title'] = os.path.basename(path)

        try:
            content = info['editor'].get("1.0", tk.END).strip()
            data = {"version": "2.0", "codigo": content, "ast": ast}
            with open(path, 'wb') as f:
                pickle.dump(data, f)
            
            info['dirty'] = False
            self.editor_notebook.tab(self.editor_notebook.select(), text=info['title'])
            self._refresh_package_list()
            self.lbl_error.config(text=f"✅ Paquete guardado: {info['title']}", fg="#89D185")
        except Exception as e: messagebox.showerror("Error", str(e))

    def empaquetar_codigo(self): self.guardar_archivo()

    def _on_sidebar_double_click(self, e):
        item = self.tree_packages.selection()
        if not item: return
        path = self.tree_packages.item(item, 'values')[0]
        for tid, info in self.editors.items():
            if info['path'] == path:
                self.editor_notebook.select(tid)
                return
        self.add_new_editor_tab(path)

    def _refresh_package_list(self):
        for item in self.tree_packages.get_children(): self.tree_packages.delete(item)
        pkg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))
        if os.path.exists(pkg_dir):
            for f in os.listdir(pkg_dir):
                if f.endswith(".pqek"):
                    self.tree_packages.insert('', tk.END, text=f" 📦 {f}", values=(os.path.join(pkg_dir, f),))

    def _highlight_syntax(self, editor):
        for tag in ["TIPO_DATO", "COMANDO_IO", "CONTROL", "BOOLEANO", "CADENA_TEXTO", "NUMERO", "OPERADOR", "COMENTARIO", "ERROR_LINEA"]:
            editor.tag_remove(tag, "1.0", tk.END)
        try:
            tokens = tokenize(editor.get("1.0", tk.END))
            for t in tokens:
                s, e = f"{t.line}.{t.column-1}", f"{t.line}.{t.column-1 + len(str(t.value))}"
                if t.type == "COMENTARIO": editor.tag_add("COMENTARIO", s, e)
                elif t.type == "TIPO_DATO": editor.tag_add("TIPO_DATO", s, e)
                elif t.type == "COMANDO_IO": editor.tag_add("COMANDO_IO", s, e)
                elif t.type == "CONTROL": editor.tag_add("CONTROL", s, e)
                elif t.type == "BOOLEANO": editor.tag_add("BOOLEANO", s, e)
                elif t.type == "CADENA_TEXTO": editor.tag_add("CADENA_TEXTO", s, e)
                elif t.type in ["NUMERO_ENTERO", "NUMERO_REAL"]: editor.tag_add("NUMERO", s, e)
                elif t.type in ["OPERADOR_ASIGNACION", "OPERADOR_ARITMETICO", "COMPARADOR"]: editor.tag_add("OPERADOR", s, e)
        except: pass

    def analizar_codigo(self):
        info = self.get_current_editor_info()
        if not info: return None
        for item in self.tree_tokens.get_children(): self.tree_tokens.delete(item)
        editor = info['editor']
        codigo = editor.get("1.0", tk.END)
        if not codigo.strip(): return None
        try:
            tokens_all = tokenize(codigo)
            for t in tokens_all: self.tree_tokens.insert('', tk.END, values=(t.line, t.type, t.value))
            ast = Parser([t for t in tokens_all if t.type != 'COMENTARIO']).parse()
            self.lbl_error.config(text=f"✅ aro, esa era — {len(tokens_all)} tokens validados.", fg="#89D185")
            return ast
        except Exception as e:
            self.lbl_error.config(text=str(e), fg=self.error_color)
            if hasattr(e, 'token') and e.token:
                s, e_idx = f"{e.token.line}.{e.token.column-1}", f"{e.token.line}.{e.token.column-1 + len(str(e.token.value))}"
                editor.tag_add("ERROR_LINEA", s, e_idx); editor.see(s)
            return None

    def ejecutar_codigo(self):
        ast = self.analizar_codigo()
        if not ast: return
        from src.interpreter.interpreter import Interpreter
        self.notebook_console.select(self.tab_terminal)
        self._append_to_terminal("🚀 Iniciando ejecución...\n\n")
        def run():
            try:
                Interpreter(output_callback=lambda m: self.after(0, self._append_to_terminal, m + "\n"), input_callback=self._request_input).execute(ast)
                self.after(0, self._append_to_terminal, "\n✅ Ejecución finalizada con éxito.\n", "#89D185")
            except Exception as ex: self.after(0, self._append_to_terminal, f"\n❌ ERROR: {str(ex)}\n", self.error_color)
        threading.Thread(target=run, daemon=True).start()

    def ejecutar_paquete(self, path):
        from src.interpreter.interpreter import Interpreter
        try:
            with open(path, 'rb') as f: data = pickle.load(f)
            self.notebook_console.select(self.tab_terminal)
            self._append_to_terminal(f"🚀 Ejecutando: {os.path.basename(path)}\n")
            threading.Thread(target=lambda: Interpreter(output_callback=lambda m: self.after(0, self._append_to_terminal, m + "\n"), input_callback=self._request_input).execute(data['ast']), daemon=True).start()
        except Exception as e: messagebox.showerror("Error", str(e))

    def _on_terminal_enter(self, e):
        v = self.terminal_input.get(); self._append_to_terminal(v + "\n", "white"); self.terminal_input.delete(0, tk.END); self.terminal_input.config(state='disabled'); self.input_queue.put(v)

    def _append_to_terminal(self, t, c="#CCCCCC"):
        self.terminal_output.config(state='normal')
        tag = f"c_{c.replace('#','')}"
        self.terminal_output.tag_configure(tag, foreground=c)
        self.terminal_output.insert(tk.END, t, tag); self.terminal_output.see(tk.END); self.terminal_output.config(state='disabled')

    def _request_input(self, n, vt):
        self.after(0, lambda: (self.notebook_console.select(self.tab_terminal), self._append_to_terminal(f"📥 {n} ({vt}): ", "#569CD6"), self.terminal_input.config(state='normal'), self.terminal_input.focus_set()))
        return self.input_queue.get()

def start_app(): CompilerGUI().mainloop()
if __name__ == "__main__": start_app()
