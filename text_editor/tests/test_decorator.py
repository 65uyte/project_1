from text_editor.document.document import Document
from text_editor.document.decorators import AutoSaveDecorator, DocumentDecorator

def test_autosave_decorator_callback():
    saved = {}
    def save_callback(content):
        saved['content'] = content
    doc = Document()
    deco = AutoSaveDecorator(doc, save_callback)
    deco.content = "test123"
    assert saved['content'] == "test123"

def test_document_decorator_content():
    class DummyDoc:
        def __init__(self):
            self.content = "abc"
    doc = DummyDoc()
    deco = DocumentDecorator(doc)
    assert deco.content == "abc"
    deco.content = "xyz"
    assert doc.content == "xyz" 