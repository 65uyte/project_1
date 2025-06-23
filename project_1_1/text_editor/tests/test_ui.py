from text_editor.facade.editor_facade import EditorFacade
from text_editor.commands.command import SetTextCommand
import pytest

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