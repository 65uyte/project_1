from text_editor.document.document import Document
from text_editor.document.decorators import AutoSaveDecorator

def test_autosave_decorator_callback():
    saved = {}
    def save_callback(content):
        saved['content'] = content
    doc = Document()
    deco = AutoSaveDecorator(doc, save_callback)
    deco.content = "test123"
    assert saved['content'] == "test123" 