from text_editor.document.document import Document
from text_editor.document.observer import DocumentObserver

def test_document_observer_prints(capsys):
    doc = Document()
    obs = DocumentObserver()
    doc.attach(obs)
    doc.content = "new text"
    captured = capsys.readouterr()
    assert "Document updated: new text" in captured.out 