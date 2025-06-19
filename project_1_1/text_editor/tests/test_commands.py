from text_editor.commands.undo_redo import UndoRedoManager
from text_editor.commands.command import SetTextCommand
from text_editor.document.document import Document

def test_undo_redo_with_set_text():
    doc = Document()
    manager = UndoRedoManager()
    
    # Перша зміна
    cmd1 = SetTextCommand(doc, "Hello")
    manager.execute(cmd1)
    assert doc.content == "Hello"
    
    # Друга зміна
    cmd2 = SetTextCommand(doc, "Hello World")
    manager.execute(cmd2)
    assert doc.content == "Hello World"
    
    # Undo
    manager.undo()
    assert doc.content == "Hello"
    
    # Redo
    manager.redo()
    assert doc.content == "Hello World"

def test_undo_redo_multiple_changes():
    doc = Document()
    manager = UndoRedoManager()
    
    # Серія змін
    manager.execute(SetTextCommand(doc, "A"))
    manager.execute(SetTextCommand(doc, "AB"))
    manager.execute(SetTextCommand(doc, "ABC"))
    
    assert doc.content == "ABC"
    
    # Undo всіх змін
    manager.undo()
    assert doc.content == "AB"
    manager.undo()
    assert doc.content == "A"
    manager.undo()
    assert doc.content == ""
    
    # Redo всіх змін
    manager.redo()
    assert doc.content == "A"
    manager.redo()
    assert doc.content == "AB"
    manager.redo()
    assert doc.content == "ABC"

def test_undo_redo_empty_stack():
    doc = Document()
    manager = UndoRedoManager()
    
    # Undo на порожньому стеку не має ефекту
    manager.undo()
    assert doc.content == ""
    
    # Redo на порожньому стеку не має ефекту
    manager.redo()
    assert doc.content == ""

def test_set_text_command_execute():
    doc = Document("Original")
    cmd = SetTextCommand(doc, "New content")
    cmd.execute()
    assert doc.content == "New content"

def test_set_text_command_undo():
    doc = Document("Original")
    cmd = SetTextCommand(doc, "New content")
    cmd.execute()
    cmd.undo()
    assert doc.content == "Original"

def test_set_text_command_preserves_previous():
    doc = Document("Original")
    cmd = SetTextCommand(doc, "New content")
    cmd.execute()
    assert cmd.prev_text == "Original"

def test_undo_redo_clear_redo_stack():
    doc = Document()
    manager = UndoRedoManager()
    
    manager.execute(SetTextCommand(doc, "A"))
    manager.execute(SetTextCommand(doc, "B"))
    manager.undo()
    assert doc.content == "A"
    
    # Нова команда очищає redo стек
    manager.execute(SetTextCommand(doc, "C"))
    manager.redo()  # Не має ефекту
    assert doc.content == "C"

def test_undo_redo_complex_scenario():
    doc = Document()
    manager = UndoRedoManager()
    
    # Створюємо складний сценарій
    manager.execute(SetTextCommand(doc, "Start"))
    manager.execute(SetTextCommand(doc, "Start with"))
    manager.execute(SetTextCommand(doc, "Start with some"))
    manager.execute(SetTextCommand(doc, "Start with some text"))
    
    # Undo кілька разів
    manager.undo()
    assert doc.content == "Start with some"
    manager.undo()
    assert doc.content == "Start with"
    
    # Додаємо нову команду
    manager.execute(SetTextCommand(doc, "Start with new"))
    
    # Redo не має ефекту
    manager.redo()
    assert doc.content == "Start with new"

def test_set_text_command_same_content():
    doc = Document("Test")
    cmd = SetTextCommand(doc, "Test")  # Такий самий контент
    cmd.execute()
    assert doc.content == "Test"
    cmd.undo()
    assert doc.content == "Test"  # Повертається до оригіналу 