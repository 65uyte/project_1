from text_editor.facade.editor_facade import EditorFacade
from text_editor.commands.command import SetTextCommand
import tempfile
import os

def test_facade_new_document():
    facade = EditorFacade()
    facade.new_document("start")
    assert facade.get_content() == "start"

def test_facade_set_get_content():
    facade = EditorFacade()
    facade.set_content("test content")
    assert facade.get_content() == "test content"

def test_facade_undo_redo():
    facade = EditorFacade()
    
    # Реєструємо команди вручну для тестування
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

def test_facade_save_to_file():
    facade = EditorFacade()
    facade.set_content("Test content for saving")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        temp_file = f.name
    
    try:
        facade.save_to_file(temp_file)
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == "Test content for saving"
    finally:
        os.unlink(temp_file)

def test_facade_open_from_file():
    facade = EditorFacade()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Content from file")
        temp_file = f.name
    
    try:
        facade.open_from_file(temp_file)
        assert facade.get_content() == "Content from file"
    finally:
        os.unlink(temp_file)

def test_facade_empty_document():
    facade = EditorFacade()
    assert facade.get_content() == ""

def test_facade_multiple_new_documents():
    facade = EditorFacade()
    facade.new_document("First")
    facade.new_document("Second")
    facade.new_document("Third")
    assert facade.get_content() == "Third"

def test_facade_save_callback():
    saved_content = None
    def save_callback(content):
        nonlocal saved_content
        saved_content = content
    
    facade = EditorFacade(save_callback)
    facade.set_content("Callback test")
    assert saved_content == "Callback test"

def test_facade_no_save_callback():
    facade = EditorFacade()  # Без callback
    facade.set_content("Test")
    # Не має викликати помилку
    assert facade.get_content() == "Test" 