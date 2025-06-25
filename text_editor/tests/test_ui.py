from text_editor.facade.editor_facade import EditorFacade
from text_editor.commands.command import SetTextCommand
import pytest
import sys
import types
from unittest.mock import patch, MagicMock
import tempfile
import os
from text_editor.document.decorators import AutoSaveDecorator

def test_facade_basic_operations():
    facade = EditorFacade()
    facade.set_content("test content")
    assert facade.get_content() == "test content"

def test_facade_new_document():
    facade = EditorFacade()
    facade.new_document("new content")
    assert facade.get_content() == "new content"

def test_facade_undo_redo():
    facade = EditorFacade()
    
    facade.undo_redo.execute(SetTextCommand(facade.document, "one"))
    facade.undo_redo.execute(SetTextCommand(facade.document, "two"))
    facade.undo_redo.execute(SetTextCommand(facade.document, "three"))
    
    assert facade.get_content() == "three"
    facade.undo()
    assert facade.get_content() == "two"
    facade.undo()
    assert facade.get_content() == "one"
    facade.redo()
    assert facade.get_content() == "two"

def test_main_entrypoint():
    main_mod = sys.modules.get('text_editor.main')
    if main_mod:
        del sys.modules['text_editor.main']
    with patch('tkinter.Tk') as mock_tk, \
         patch('text_editor.ui.editor_window.EditorWindow') as mock_editor_window, \
         patch('tkinter.Tk.mainloop') as mock_mainloop:
        import importlib
        main_module = importlib.import_module('text_editor.main')
        main_module.main()
        mock_tk.assert_called_once()
        mock_editor_window.assert_called_once()

def test_editor_window_init():
    with patch('tkinter.Tk') as mock_tk:
        root = mock_tk()
        from text_editor.ui.editor_window import EditorWindow
        win = EditorWindow(root)
        assert hasattr(win, 'facade')
        assert hasattr(win, 'text')

def test_new_file_creates_file_and_autosaves(monkeypatch):
    from text_editor.ui.editor_window import EditorWindow
    class DummyRoot:
        def __init__(self):
            self.protocol = lambda *a, **k: None
            self.title = lambda *a, **k: None
            self.destroy = lambda: None
            self.config = lambda *a, **k: None

    with patch("text_editor.ui.editor_window.tk.Text", MagicMock()):
        root = DummyRoot()
        win = EditorWindow(root)
        with tempfile.TemporaryDirectory() as tmpdir:
            fname = os.path.join(tmpdir, "testfile.txt")
            win.current_file_path = fname
            win.facade.document = AutoSaveDecorator(win.facade.factory.create_document("", filetype=".txt"), win.auto_save_callback)
            win.facade.document.content = "Hello autosave!"
            with open(fname, 'r', encoding='utf-8') as f:
                assert f.read() == "Hello autosave!" 