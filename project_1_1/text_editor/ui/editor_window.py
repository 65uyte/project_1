import tkinter as tk
from text_editor.facade.editor_facade import EditorFacade
from tkinter import filedialog, messagebox
from text_editor.commands.command import SetTextCommand
import os
from text_editor.document.decorators import AutoSaveDecorator

class EditorWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Editor")
        self.current_file_path = None
        self.last_text = ""
        self.facade = EditorFacade(self.auto_save_callback)

        self.text = tk.Text(root, wrap="word")
        self.text.pack(expand=1, fill="both")

        self.text.bind("<KeyRelease>", self.on_text_change)
        self.text.bind("<Control-c>", lambda e: (self.copy(), "break"))
        self.text.bind("<Control-v>", lambda e: (self.paste(), "break"))

        menu = tk.Menu(root)
        root.config(menu=menu)
        edit_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="New", command=self.new_file)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_text_change(self, event=None):
        content = self.text.get("1.0", tk.END)[:-1]
        if content != self.last_text:
            cmd = SetTextCommand(self.facade.document, content)
            self.facade.undo_redo.execute(cmd)
            self.last_text = content

    def copy(self):
        try:
            selected = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except tk.TclError:
            pass  # Нічого не виділено

    def paste(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.text.insert(tk.INSERT, clipboard_text)
            self.on_text_change()
        except tk.TclError:
            pass  # Буфер порожній

    def undo(self):
        self.facade.undo()
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", self.facade.get_content())
        self.last_text = self.facade.get_content()

    def redo(self):
        self.facade.redo()
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", self.facade.get_content())
        self.last_text = self.facade.get_content()

    def auto_save_callback(self, content):
        if self.current_file_path:
            try:
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not auto-save file: {e}")

    def open_file(self):
        # Власний інтерфейс відкривання
        open_win = tk.Toplevel(self.root)
        open_win.title("Open File")
        tk.Label(open_win, text="Directory:").pack(padx=10, pady=(10, 0))
        dir_var = tk.StringVar(value="D:\\Documents")
        dir_frame = tk.Frame(open_win)
        dir_frame.pack(padx=10, pady=2, fill='x')
        dir_entry = tk.Entry(dir_frame, textvariable=dir_var, width=30)
        dir_entry.pack(side='left', fill='x', expand=True)
        def browse_dir():
            d = tk.filedialog.askdirectory(initialdir=dir_var.get())
            if d:
                dir_var.set(d)
                update_file_list()
        tk.Button(dir_frame, text="Browse...", command=browse_dir).pack(side='left', padx=5)
        tk.Label(open_win, text="File type:").pack(padx=10, pady=(10, 0))
        filetype_var = tk.StringVar(value="all")
        types = [
            ('all', 'All Types'),
            ('.txt', 'Text File'),
            ('.md', 'Markdown'),
            ('.rtf', 'Rich Text'),
            ('.html', 'HTML')
        ]
        for ext, label in types:
            tk.Radiobutton(open_win, text=label, variable=filetype_var, value=ext).pack(anchor='w', padx=20)
        tk.Label(open_win, text="Files:").pack(padx=10, pady=(10, 0))
        file_listbox = tk.Listbox(open_win, width=40, height=8)
        def update_file_list(*_):
            file_listbox.delete(0, tk.END)
            ext = filetype_var.get()
            directory = dir_var.get()
            if not os.path.isdir(directory):
                return
            for f in os.listdir(directory):
                if ext == 'all' or f.endswith(ext):
                    file_listbox.insert(tk.END, f)
        filetype_var.trace_add('write', update_file_list)
        dir_var.trace_add('write', update_file_list)
        update_file_list()
        file_listbox.pack(padx=10, pady=5)
        filename_var = tk.StringVar()
        def on_select(event):
            sel = file_listbox.curselection()
            if sel:
                filename_var.set(file_listbox.get(sel[0]))
        file_listbox.bind('<<ListboxSelect>>', on_select)
        tk.Label(open_win, text="File name:").pack(padx=10, pady=(10, 0))
        entry = tk.Entry(open_win, textvariable=filename_var, width=30)
        entry.pack(padx=10, pady=5)
        def openf():
            name = filename_var.get().strip()
            ext = filetype_var.get()
            directory = dir_var.get()
            if not name:
                messagebox.showerror("Error", "Please select or enter file name.")
                return
            if not os.path.isdir(directory):
                messagebox.showerror("Error", "Invalid directory.")
                return
            fname = os.path.join(directory, name)
            # Визначаємо тип по розширенню, якщо вибрано all
            if ext == 'all':
                ext = os.path.splitext(fname)[1].lower()
                if ext not in ['.txt', '.md', '.rtf', '.html']:
                    ext = '.txt'
            if not fname.endswith(ext):
                fname += ext
            try:
                self.current_file_path = fname
                self.facade.document = AutoSaveDecorator(self.facade.factory.create_document("", filetype=ext), self.auto_save_callback)
                self.facade.open_from_file(fname)
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", self.facade.get_content())
                open_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
        tk.Button(open_win, text="Open", command=openf).pack(pady=10)

    def save_file(self):
        # Власний інтерфейс збереження з вибором шляху
        save_win = tk.Toplevel(self.root)
        save_win.title("Save File")
        tk.Label(save_win, text="Directory:").pack(padx=10, pady=(10, 0))
        dir_var = tk.StringVar(value="D:\\Documents")
        dir_frame = tk.Frame(save_win)
        dir_frame.pack(padx=10, pady=2, fill='x')
        dir_entry = tk.Entry(dir_frame, textvariable=dir_var, width=30)
        dir_entry.pack(side='left', fill='x', expand=True)
        def browse_dir():
            d = tk.filedialog.askdirectory(initialdir=dir_var.get())
            if d:
                dir_var.set(d)
                update_file_list()
        tk.Button(dir_frame, text="Browse...", command=browse_dir).pack(side='left', padx=5)
        tk.Label(save_win, text="File name:").pack(padx=10, pady=(10, 0))
        filename_var = tk.StringVar()
        entry = tk.Entry(save_win, textvariable=filename_var, width=30)
        entry.pack(padx=10, pady=5)
        tk.Label(save_win, text="File type:").pack(padx=10, pady=(10, 0))
        filetype_var = tk.StringVar(value=".txt")
        types = [('.txt', 'Text File'), ('.md', 'Markdown'), ('.rtf', 'Rich Text'), ('.html', 'HTML')]
        for ext, label in types:
            tk.Radiobutton(save_win, text=label, variable=filetype_var, value=ext).pack(anchor='w', padx=20)
        file_listbox = tk.Listbox(save_win, width=40, height=8)
        def update_file_list(*_):
            file_listbox.delete(0, tk.END)
            ext = filetype_var.get()
            directory = dir_var.get()
            if not os.path.isdir(directory):
                return
            for f in os.listdir(directory):
                if f.endswith(ext):
                    file_listbox.insert(tk.END, f)
        filetype_var.trace_add('write', update_file_list)
        dir_var.trace_add('write', update_file_list)
        update_file_list()
        file_listbox.pack(padx=10, pady=5)
        def on_select(event):
            sel = file_listbox.curselection()
            if sel:
                filename_var.set(file_listbox.get(sel[0]).rsplit('.', 1)[0])
        file_listbox.bind('<<ListboxSelect>>', on_select)
        def save():
            name = filename_var.get().strip()
            ext = filetype_var.get()
            directory = dir_var.get()
            if not name:
                messagebox.showerror("Error", "Please enter file name.")
                return
            if not os.path.isdir(directory):
                messagebox.showerror("Error", "Invalid directory.")
                return
            fname = os.path.join(directory, f"{name}{ext}")
            try:
                self.current_file_path = fname
                self.facade.document = AutoSaveDecorator(self.facade.factory.create_document(self.text.get("1.0", tk.END)[:-1], filetype=ext), self.auto_save_callback)
                self.facade.save_to_file(fname)
                save_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        tk.Button(save_win, text="Save", command=save).pack(pady=10)

    def new_file(self):
        # Діалог вибору імені та шляху нового файлу (аналогічно save_file)
        new_win = tk.Toplevel(self.root)
        new_win.title("New File")
        tk.Label(new_win, text="Directory:").pack(padx=10, pady=(10, 0))
        dir_var = tk.StringVar(value="D:\\Documents")
        dir_frame = tk.Frame(new_win)
        dir_frame.pack(padx=10, pady=2, fill='x')
        dir_entry = tk.Entry(dir_frame, textvariable=dir_var, width=30)
        dir_entry.pack(side='left', fill='x', expand=True)
        def browse_dir():
            d = tk.filedialog.askdirectory(initialdir=dir_var.get())
            if d:
                dir_var.set(d)
        tk.Button(dir_frame, text="Browse...", command=browse_dir).pack(side='left', padx=5)
        tk.Label(new_win, text="File name:").pack(padx=10, pady=(10, 0))
        filename_var = tk.StringVar()
        entry = tk.Entry(new_win, textvariable=filename_var, width=30)
        entry.pack(padx=10, pady=5)
        tk.Label(new_win, text="File type:").pack(padx=10, pady=(10, 0))
        filetype_var = tk.StringVar(value=".txt")
        types = [('.txt', 'Text File'), ('.md', 'Markdown'), ('.rtf', 'Rich Text'), ('.html', 'HTML')]
        for ext, label in types:
            tk.Radiobutton(new_win, text=label, variable=filetype_var, value=ext).pack(anchor='w', padx=20)
        def create():
            name = filename_var.get().strip()
            ext = filetype_var.get()
            directory = dir_var.get()
            if not name:
                messagebox.showerror("Error", "Please enter file name.")
                return
            if not os.path.isdir(directory):
                messagebox.showerror("Error", "Invalid directory.")
                return
            fname = os.path.join(directory, f"{name}{ext}")
            try:
                # Створюємо порожній файл
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write("")
                self.current_file_path = fname
                self.facade.document = AutoSaveDecorator(self.facade.factory.create_document("", filetype=ext), self.auto_save_callback)
                self.text.delete("1.0", tk.END)
                self.last_text = ""
                new_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file: {e}")
        tk.Button(new_win, text="Create", command=create).pack(pady=10)

    def on_close(self):
        self.root.destroy() 