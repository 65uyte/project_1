import tkinter as tk
from text_editor.facade.editor_facade import EditorFacade
from tkinter import filedialog, messagebox
from text_editor.commands.command import SetTextCommand

class EditorWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Editor")
        self.facade = EditorFacade(self.save_document)
        self.last_text = ""

        self.text = tk.Text(root, wrap="word")
        self.text.pack(expand=1, fill="both")

        self.text.bind("<KeyRelease>", self.on_text_change)

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

    def save_document(self, content):
        # Можна реалізувати автозбереження у файл
        pass

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            try:
                self.facade.open_from_file(filepath)
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", self.facade.get_content())
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            try:
                self.facade.save_to_file(filepath)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}") 