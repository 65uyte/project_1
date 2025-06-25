import tkinter as tk
from tkinter import messagebox, filedialog
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
import json
import os

# Observer Pattern
class DocumentObserver(ABC):
    @abstractmethod
    def update(self, document):
        pass

class Document:
    def __init__(self):
        self._content = ""
        self._observers: List[DocumentObserver] = []
        self._filename = None

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str):
        self._content = value
        self._notify_observers()

    def attach(self, observer: DocumentObserver):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: DocumentObserver):
        self._observers.remove(observer)

    def _notify_observers(self):
        for observer in self._observers:
            observer.update(self)

    def create_memento(self) -> 'DocumentMemento':
        return DocumentMemento(self._content)

    def restore_from_memento(self, memento: 'DocumentMemento'):
        self._content = memento.content
        self._notify_observers()

# Command Pattern
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class InsertTextCommand(Command):
    def __init__(self, document: Document, text: str, position: int):
        self.document = document
        self.text = text
        self.position = position
        self._original_content = None

    def execute(self):
        self._original_content = self.document.content
        content = self.document.content
        self.document.content = content[:self.position] + self.text + content[self.position:]

    def undo(self):
        if self._original_content is not None:
            self.document.content = self._original_content

class DeleteTextCommand(Command):
    def __init__(self, document: Document, start: int, end: int):
        self.document = document
        self.start = start
        self.end = end
        self._deleted_text = None
        self._original_content = None

    def execute(self):
        self._original_content = self.document.content
        content = self.document.content
        self._deleted_text = content[self.start:self.end]
        self.document.content = content[:self.start] + content[self.end:]

    def undo(self):
        if self._original_content is not None:
            self.document.content = self._original_content

# Memento Pattern
class DocumentMemento:
    def __init__(self, content: str):
        self.content = content

class DocumentCaretaker:
    def __init__(self):
        self._mementos: List[DocumentMemento] = []

    def save(self, document: Document):
        self._mementos.append(document.create_memento())

    def restore(self, document: Document, index: int):
        if not 0 <= index < len(self._mementos):
            raise IndexError("Invalid memento index")
        memento = self._mementos[index]
        document.restore_from_memento(memento)

# Factory Pattern
class DocumentFactory:
    @staticmethod
    def create_document(doc_type: str) -> Document:
        if doc_type == "text":
            return Document()
        raise ValueError(f"Unknown document type: {doc_type}")

# Strategy Pattern
class TextFormatter(ABC):
    @abstractmethod
    def format(self, text: str) -> str:
        pass

class PlainTextFormatter(TextFormatter):
    def format(self, text: str) -> str:
        return text

class MarkdownFormatter(TextFormatter):
    def format(self, text: str) -> str:
        # Обробка граничних випадків
        if not text:
            return ""
        if text == "**":
            return "**"
        if text == "__":
            return "__"
        if text == "****":
            return "<b></b>"
        if text == "____":
            return "<i></i>"

        # Замінюємо markdown на HTML теги
        result = text
        if "**" in result:
            result = result.replace("**", "<b>", 1)
            result = result.replace("**", "</b>", 1)
        if "__" in result:
            result = result.replace("__", "<i>", 1)
            result = result.replace("__", "</i>", 1)
        return result

class TextEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Text Editor")
        self.root.geometry("800x600")

        self.document = DocumentFactory.create_document("text")
        self.caretaker = DocumentCaretaker()
        self.command_history: List[Command] = []
        self.redo_stack: List[Command] = []
        self.current_formatter: TextFormatter = PlainTextFormatter()

        self.setup_ui()

    def setup_ui(self):
        # Menu
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menubar)

        # Text area
        self.text_area = tk.Text(self.root, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind events
        self.text_area.bind('<KeyRelease>', self.on_text_change)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())

    def execute_command(self, command: Command):
        """Execute a command and update history."""
        command.execute()
        self.command_history.append(command)
        self.redo_stack.clear()
        self.update_text_area()

    def update_text_area(self):
        """Update the text area with current document content."""
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", self.document.content)

    def get_selection_indices(self) -> Tuple[str, str]:
        try:
            start = self.text_area.index("sel.first")
            end = self.text_area.index("sel.last")
            return start, end
        except tk.TclError:
            return None, None

    def get_char_index(self, index: str) -> int:
        """Convert Tkinter index to character position."""
        return len(self.text_area.get("1.0", index))

    def cut(self):
        try:
            # Get selected text
            selected_text = self.text_area.get("sel.first", "sel.last")
            if selected_text:
                # Store the selection indices
                start, end = self.get_selection_indices()
                start_pos = self.get_char_index(start)
                end_pos = self.get_char_index(end)

                # Cut to system clipboard
                self.text_area.event_generate("<<Cut>>")
                
                # Create and execute command for undo/redo
                command = DeleteTextCommand(self.document, start_pos, end_pos)
                self.execute_command(command)
                
                self.update_status("Text cut to clipboard")
        except tk.TclError:
            self.update_status("No text selected")

    def copy(self):
        try:
            # Copy to system clipboard
            self.text_area.event_generate("<<Copy>>")
            self.update_status("Text copied to clipboard")
        except tk.TclError:
            self.update_status("No text selected")

    def paste(self):
        try:
            position = self.text_area.index(tk.INSERT)
            pos = self.get_char_index(position)
            
            # Get clipboard content
            clipboard_text = self.root.clipboard_get()
            
            # Create and execute command
            command = InsertTextCommand(self.document, clipboard_text, pos)
            self.execute_command(command)
            
            self.update_status("Text pasted from clipboard")
        except Exception as e:
            self.update_status(f"Error pasting text: {str(e)}")

    def update_status(self, message: str):
        self.status_bar.config(text=message)
        self.root.after(2000, lambda: self.status_bar.config(text="Ready"))

    def on_text_change(self, event=None):
        self.document.content = self.text_area.get("1.0", tk.END)
        self.caretaker.save(self.document)

    def new_file(self):
        self.text_area.delete("1.0", tk.END)
        self.document.content = ""
        self.command_history.clear()
        self.redo_stack.clear()
        self.update_status("New file created")

    def open_file(self):
        filename = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_area.delete("1.0", tk.END)
                    self.text_area.insert("1.0", content)
                    self.command_history.clear()
                    self.redo_stack.clear()
                    self.update_status(f"Opened {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_file(self):
        if not self.document._filename:
            self.document._filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
        if self.document._filename:
            try:
                with open(self.document._filename, 'w', encoding='utf-8') as file:
                    file.write(self.text_area.get("1.0", tk.END))
                self.update_status(f"Saved to {self.document._filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def undo(self):
        if self.command_history:
            command = self.command_history.pop()
            command.undo()
            self.redo_stack.append(command)
            self.update_text_area()
            self.update_status("Undo completed")

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.command_history.append(command)
            self.update_text_area()
            self.update_status("Redo completed")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    editor = TextEditor()
    editor.run() 