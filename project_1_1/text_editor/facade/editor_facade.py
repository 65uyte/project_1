from text_editor.document.document_factory import DocumentFactory
from text_editor.document.decorators import AutoSaveDecorator
from text_editor.commands.undo_redo import UndoRedoManager

class EditorFacade:
    def __init__(self, save_callback=None):
        self.factory = DocumentFactory()
        self.undo_redo = UndoRedoManager()
        self.save_callback = save_callback or (lambda content: None)
        self.document = AutoSaveDecorator(self.factory.create_document(), self.save_callback)

    def new_document(self, content=""):
        self.document = AutoSaveDecorator(self.factory.create_document(content), self.save_callback)

    def set_content(self, content: str):
        self.document.content = content

    def get_content(self) -> str:
        return self.document.content

    def copy(self, text: str):
        # Тепер ця функція не потрібна, бо копіювання через системний clipboard
        pass

    def paste(self):
        # Тепер ця функція не потрібна, бо вставка через системний clipboard
        pass

    def undo(self):
        self.undo_redo.undo()

    def redo(self):
        self.undo_redo.redo()

    def save_to_file(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.get_content())

    def open_from_file(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        self.set_content(content) 