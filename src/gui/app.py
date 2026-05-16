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
except Exception: pass

class LineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget): self.textwidget = text_widget

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
        self.geometry("1100x800")
        
        self.bg_color = "#1E1E1E"; self.fg_color = "#D4D4D4"; self.panel_bg = "#252526"
        self.highlight_bg = "#333333"; self.accent_color = "#0E639C"; self.error_color = "#F48771"
        self.line_num_bg = "#1E1E1E"
        self.configure(bg=self.bg_color)
        
        try:
            from PIL import Image, ImageTk
            img_path = os.path.join(os.path.dirname(__file__), '..', '..', 'brain', '7e2aeddb-747d-4fcd-8cd8-0d546412259f', 'close_tab_icon_1778899555954.png')
            if not os.path.exists(img_path): img_path = os.path.join(os.path.dirname(__file__), 'close_tab_icon.png')
            img = Image.open(img_path).resize((12, 12), Image.LANCZOS)
            self.close_img = ImageTk.PhotoImage(img)
        except Exception: self.close_img = None

        self.editors = {}; self.input_queue = queue.Queue()
        self._configurar_estilos(); self._crear_widgets()
        self.bind("<Control-s>", lambda e: self.guardar_archivo())

    def _configurar_estilos(self):
        style = ttk.Style(self); style.theme_use('clam')
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.highlight_bg, foreground=self.fg_color, padding=[10, 2])
        style.map("TNotebook.Tab", background=[("selected", self.bg_color)])
        style.configure("Treeview", background=self.panel_bg, foreground=self.fg_color, fieldbackground=self.panel_bg, borderwidth=0, rowheight=25)
        style.configure("Treeview.Heading", background=self.highlight_bg, foreground=self.fg_color, borderwidth=0, font=('Consolas', 10, 'bold'))
        style.map('Treeview', background=[('selected', self.accent_color)])

    def _crear_widgets(self):
        top_frame = tk.Frame(self, bg=self.highlight_bg, height=40); top_frame.pack(fill=tk.X, side=tk.TOP); top_frame.pack_propagate(False)
        tk.Button(top_frame, text="❓", bg=self.highlight_bg, fg=self.fg_color, font=('Segoe UI', 11, 'bold'), borderwidth=0, padx=10, command=self.mostrar_ayuda, cursor="hand2").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(top_frame, text="🔍 Analizar", bg=self.accent_color, fg="white", font=('Segoe UI', 9, 'bold'), borderwidth=0, padx=10, command=self.analizar_codigo, cursor="hand2").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(top_frame, text="▶ Ejecutar", bg="#28A745", fg="white", font=('Segoe UI', 9, 'bold'), borderwidth=0, padx=10, command=self.ejecutar_codigo, cursor="hand2").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(top_frame, text="📦 Guardar .pqek", bg=self.highlight_bg, fg=self.fg_color, font=('Segoe UI', 9), borderwidth=0, padx=10, command=self.guardar_archivo, cursor="hand2").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(top_frame, text="❌ Cerrar Pestaña", bg=self.highlight_bg, fg=self.error_color, font=('Segoe UI', 9), borderwidth=0, padx=10, command=self.cerrar_pestana_actual, cursor="hand2").pack(side=tk.RIGHT, padx=5, pady=5)
        
        main = tk.Frame(self, bg=self.bg_color); main.pack(fill=tk.BOTH, expand=True)
        self.sidebar = tk.Frame(main, bg=self.panel_bg, width=220); self.sidebar.pack(side=tk.LEFT, fill=tk.Y); self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="CONTROL DE LA VUELTA", bg=self.highlight_bg, fg=self.fg_color, font=('Segoe UI', 8, 'bold'), pady=5).pack(fill=tk.X)
        self.tree_packages = ttk.Treeview(self.sidebar, show='tree', selectmode="browse"); self.tree_packages.pack(fill=tk.BOTH, expand=True, padx=2, pady=5); self.tree_packages.bind("<Double-1>", self._on_sidebar_double_click)
        tk.Button(self.sidebar, text="🔄 Refrescar", bg=self.highlight_bg, fg=self.fg_color, font=('Segoe UI', 8), borderwidth=0, command=self._refresh_package_list).pack(fill=tk.X, padx=10, pady=5)

        self.editor_frame = tk.Frame(main, bg=self.bg_color); self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        self.editor_notebook = ttk.Notebook(self.editor_frame); self.editor_notebook.pack(fill=tk.BOTH, expand=True); self.editor_notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        bottom = tk.Frame(self, bg=self.bg_color, height=220); bottom.pack(fill=tk.X, side=tk.BOTTOM)
        self.lbl_error = tk.Label(bottom, text="", bg=self.bg_color, fg=self.error_color, font=('Consolas', 10), pady=2); self.lbl_error.pack(fill=tk.X)
        self.notebook_console = ttk.Notebook(bottom); self.notebook_console.pack(fill=tk.BOTH, expand=True)
        self.tab_terminal = tk.Frame(self.notebook_console, bg=self.panel_bg); self.notebook_console.add(self.tab_terminal, text=" 💻 TERMINAL ")
        self.terminal_output = scrolledtext.ScrolledText(self.tab_terminal, bg=self.panel_bg, fg="#CCCCCC", font=('Consolas', 11), borderwidth=0, state='disabled', padx=10, pady=5); self.terminal_output.pack(fill=tk.BOTH, expand=True)
        t_input_f = tk.Frame(self.tab_terminal, bg=self.panel_bg); t_input_f.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
        tk.Label(t_input_f, text=" > ", bg=self.panel_bg, fg=self.accent_color, font=('Consolas', 12, 'bold')).pack(side=tk.LEFT)
        self.terminal_input = tk.Entry(t_input_f, bg=self.panel_bg, fg="white", insertbackground="white", font=('Consolas', 12), borderwidth=0); self.terminal_input.pack(fill=tk.X, side=tk.LEFT, expand=True); self.terminal_input.bind("<Return>", self._on_terminal_enter)
        
        self.tab_tokens = tk.Frame(self.notebook_console, bg=self.panel_bg); self.notebook_console.add(self.tab_tokens, text=" 🔍 TOKENS ")
        self.tree_tokens = ttk.Treeview(self.tab_tokens, columns=('linea', 'token', 'lexema'), show='headings'); self.tree_tokens.heading('linea', text='Línea'); self.tree_tokens.heading('token', text='Tipo'); self.tree_tokens.heading('lexema', text='Valor'); self.tree_tokens.column('linea', width=50); self.tree_tokens.pack(fill=tk.BOTH, expand=True)

        self._refresh_package_list(); self.add_new_editor_tab()

    def add_new_editor_tab(self, file_path=None, content=""):
        tab = tk.Frame(self.editor_notebook, bg=self.bg_color)
        c = tk.Frame(tab, bg=self.bg_color); c.pack(fill=tk.BOTH, expand=True)
        ln = LineNumbers(c, width=35, bg=self.line_num_bg, highlightthickness=0); ln.pack(side=tk.LEFT, fill=tk.Y)
        e = tk.Text(c, bg=self.bg_color, fg=self.fg_color, insertbackground="white", font=('Consolas', 13), undo=True, borderwidth=0, padx=10, pady=10); e.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); ln.attach(e)
        
        txt = content
        if not txt and file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    raw = f.read()
                    try: 
                        data = pickle.loads(raw)
                        txt = data.get("codigo", "") if isinstance(data, dict) else ""
                    except: txt = raw.decode('utf-8', errors='ignore')
            except: pass
        if txt: e.insert("1.0", txt)
        self._setup_editor_tags(e)
        t = os.path.basename(file_path) if file_path else "sin_nombre.pqek"
        self.editor_notebook.add(tab, text=t, image=self.close_img, compound=tk.RIGHT if self.close_img else None)
        tid = tab.winfo_pathname(tab.winfo_id())
        self.editors[tid] = {'editor': e, 'path': file_path, 'dirty': False, 'title': t, 'linenumbers': ln}
        self.editor_notebook.select(tab)
        e.bind("<KeyRelease>", lambda ev: self._on_editor_change(tid))
        self.after(100, lambda: self._highlight_syntax(e))

    def cerrar_pestana_actual(self):
        sel = self.editor_notebook.select()
        if not sel: return
        i = self.editors.get(sel)
        if i and i['dirty'] and not messagebox.askyesno("Cerrar", "¿Cerrar sin guardar la vuelta?"): return
        self.editor_notebook.forget(sel); del self.editors[sel]
        if not self.editors: self.add_new_editor_tab()

    def _setup_editor_tags(self, e):
        tags = {"TIPO_DATO":"#569CD6", "COMANDO_IO":"#DCDCAA", "CONTROL":"#C586C0", "BOOLEANO":"#569CD6", "CADENA_TEXTO":"#CE9178", "NUMERO":"#B5CEA8", "OPERADOR":"#D4D4D4", "COMENTARIO":"#6A9955"}
        for t, c in tags.items(): e.tag_configure(t, foreground=c)
        e.tag_configure("ERROR_LINEA", underline=True, underlinefg=self.error_color)

    def get_current_editor_info(self): return self.editors.get(self.editor_notebook.select())

    def _on_editor_change(self, tid):
        i = self.editors.get(tid)
        if i and not i['dirty']: i['dirty'] = True; self.editor_notebook.tab(tid, text=f"• {i['title']}")
        self._highlight_syntax(i['editor']); i['linenumbers'].redraw()

    def _on_tab_changed(self, e):
        i = self.get_current_editor_info()
        if i: i['linenumbers'].redraw(); self._highlight_syntax(i['editor'])

    def guardar_archivo(self):
        i = self.get_current_editor_info()
        if not i: return
        ast = self.analizar_codigo()
        p = i['path']
        if not p:
            pkg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))
            if not os.path.exists(pkg_dir): os.makedirs(pkg_dir)
            p = filedialog.asksaveasfilename(initialdir=pkg_dir, defaultextension=".pqek", filetypes=[("Paquete Costeñol", "*.pqek")])
            if not p: return
            i['path'] = p; i['title'] = os.path.basename(p)
        try:
            with open(p, 'wb') as f: pickle.dump({"version": "3.0", "codigo": i['editor'].get("1.0", "end-1c"), "ast": ast}, f)
            i['dirty'] = False; self.editor_notebook.tab(self.editor_notebook.select(), text=i['title'])
            self._refresh_package_list(); self.lbl_error.config(text=f"✅ Guardado: {i['title']}", fg="#89D185")
        except Exception as ex: messagebox.showerror("Error", str(ex))

    def _on_sidebar_double_click(self, e):
        it = self.tree_packages.selection()
        if not it: return
        p = self.tree_packages.item(it, 'values')[0]
        for tid, info in self.editors.items():
            if info['path'] == p: self.editor_notebook.select(tid); return
        self.add_new_editor_tab(p)

    def _refresh_package_list(self):
        for it in self.tree_packages.get_children(): self.tree_packages.delete(it)
        pkg_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))
        if os.path.exists(pkg_dir):
            for f in os.listdir(pkg_dir):
                if f.endswith(".pqek"): self.tree_packages.insert('', tk.END, text=f" 📦 {f}", values=(os.path.join(pkg_dir, f),))

    def _highlight_syntax(self, e):
        for tag in ["TIPO_DATO", "COMANDO_IO", "CONTROL", "BOOLEANO", "CADENA_TEXTO", "NUMERO", "OPERADOR", "COMENTARIO", "ERROR_LINEA"]: e.tag_remove(tag, "1.0", tk.END)
        try:
            tokens = tokenize(e.get("1.0", tk.END))
            for t in tokens:
                s, end = f"{t.line}.{t.column-1}", f"{t.line}.{t.column-1 + len(str(t.value))}"
                if t.type in ["NUMERO_ENTERO", "NUMERO_REAL"]: e.tag_add("NUMERO", s, end)
                elif t.type in ["OPERADOR_ASIGNACION", "OPERADOR_ARITMETICO", "COMPARADOR"]: e.tag_add("OPERADOR", s, end)
                else: e.tag_add(t.type, s, end)
        except: pass

    def analizar_codigo(self):
        i = self.get_current_editor_info()
        if not i: return None
        for it in self.tree_tokens.get_children(): self.tree_tokens.delete(it)
        ed = i['editor']; cod = ed.get("1.0", tk.END)
        if not cod.strip(): return None
        try:
            toks = tokenize(cod)
            for t in toks: self.tree_tokens.insert('', tk.END, values=(t.line, t.type, t.value))
            ast = Parser([t for t in toks if t.type != 'COMENTARIO']).parse()
            self.lbl_error.config(text="✅ Todo nítido.", fg="#89D185"); return ast
        except Exception as ex:
            self.lbl_error.config(text=str(ex), fg=self.error_color)
            if hasattr(ex, 'token') and ex.token:
                s, end = f"{ex.token.line}.{ex.token.column-1}", f"{ex.token.line}.{ex.token.column-1 + len(str(ex.token.value))}"
                ed.tag_add("ERROR_LINEA", s, end); ed.see(s)
            return None

    def ejecutar_codigo(self):
        ast = self.analizar_codigo()
        if not ast: return
        from src.interpreter.interpreter import Interpreter
        self.notebook_console.select(self.tab_terminal); self._append_to_terminal("🚀 Iniciando...\n\n")
        threading.Thread(target=lambda: Interpreter(lambda m: self.after(0, self._append_to_terminal, m + "\n"), self._request_input).execute(ast), daemon=True).start()

    def mostrar_ayuda(self):
        win = tk.Toplevel(self); win.title("Ejemplo"); win.geometry("500x550"); win.configure(bg=self.bg_color)
        txt = scrolledtext.ScrolledText(win, bg=self.panel_bg, fg=self.fg_color, font=('Consolas', 11))
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        txt.insert(tk.END, "// Ejemplo:\nnombre Texto;\nMensaje.Texto(\"Tu nombre:\");\nnombre = Captura.Texto();\nMensaje.Texto(\"Hola\", nombre);")
        txt.config(state='disabled')

    def _on_terminal_enter(self, e):
        v = self.terminal_input.get(); self._append_to_terminal(v + "\n", "white"); self.terminal_input.delete(0, tk.END); self.input_queue.put(v)

    def _append_to_terminal(self, t, c="#CCCCCC"):
        self.terminal_output.config(state='normal'); tag = f"c_{c.replace('#','')}"; self.terminal_output.tag_configure(tag, foreground=c); self.terminal_output.insert(tk.END, t, tag); self.terminal_output.see(tk.END); self.terminal_output.config(state='disabled')

    def _request_input(self, n, vt):
        self.after(0, lambda: (self.notebook_console.select(self.tab_terminal), self._append_to_terminal(f"📥 {n}: ", "#569CD6"), self.terminal_input.focus_set())); return self.input_queue.get()

def start_app(): CompilerGUI().mainloop()
if __name__ == "__main__": start_app()
