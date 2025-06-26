from text_editor.document.document import Document
from text_editor.document.observer import DocumentObserver, PrintObserver, FileLogObserver

def test_document_observer_prints(capsys):
    doc = Document()
    obs = PrintObserver()
    doc.attach(obs)
    doc.content = "new text"
    captured = capsys.readouterr()
    assert "Document updated: new text" in captured.out 

def test_print_observer(capsys):
    doc = Document()
    obs = PrintObserver()
    doc.attach(obs)
    doc.content = "new text"
    captured = capsys.readouterr()
    assert "Document updated: new text" in captured.out

def test_file_log_observer(tmp_path):
    doc = Document()
    log_file = tmp_path / "log.txt"
    obs = FileLogObserver(str(log_file))
    doc.attach(obs)
    doc.content = "log this"
    with open(log_file, encoding="utf-8") as f:
        lines = f.readlines()
    assert any("log this" in line for line in lines) 