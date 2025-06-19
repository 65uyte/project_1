from .document import Document
 
class DocumentFactory:
    def create_document(self, content: str = "") -> Document:
        return Document(content) 