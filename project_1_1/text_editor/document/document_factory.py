from .document import Document

class TxtDocument(Document):
    pass

class MdDocument(Document):
    pass

class RtfDocument(Document):
    pass

class HtmlDocument(Document):
    pass

class DocumentFactory:
    _doc_types = {
        ".txt": TxtDocument,
        ".md": MdDocument,
        ".rtf": RtfDocument,
        ".html": HtmlDocument,
    }

    def create_document(self, content: str = "", filetype: str = ".txt") -> Document:
        doc_class = self._doc_types.get(filetype)
        if not doc_class:
            raise ValueError(f"Unsupported file type: {filetype}")
        return doc_class(content) 