from .document import Document

class DocumentDecorator(Document):
    def __init__(self, document: Document):
        self._document = document

    @property
    def content(self) -> str:
        return self._document.content

    @content.setter
    def content(self, value: str):
        self._document.content = value

class AutoSaveDecorator(DocumentDecorator):
    def __init__(self, document: Document, save_callback):
        super().__init__(document)
        self.save_callback = save_callback

    @property
    def content(self) -> str:
        return self._document.content

    @content.setter
    def content(self, value: str):
        self._document.content = value
        self.save_callback(self._document.content) 