import pytest
from text_editor import (
    Document,
    DocumentObserver,
    InsertTextCommand,
    DeleteTextCommand,
    DocumentFactory,
    PlainTextFormatter,
    MarkdownFormatter,
    DocumentMemento,
    DocumentCaretaker
)

# Fixture for test success messages
@pytest.fixture(autouse=True)
def test_success_message(request):
    yield
    print(f"\n✅ Test passed: {request.node.name}")

# Test Observer Pattern
class TestObserver(DocumentObserver):
    def __init__(self):
        self.updated = False
        self.last_content = None

    def update(self, document):
        self.updated = True
        self.last_content = document.content

def test_observer_pattern():
    doc = Document()
    observer = TestObserver()
    doc.attach(observer)
    doc.content = "test"
    assert observer.updated
    assert observer.last_content == "test"

# Test Command Pattern
def test_insert_text_command():
    doc = Document()
    doc.content = "Hello"
    command = InsertTextCommand(doc, " World", 5)
    command.execute()
    assert doc.content == "Hello World"
    command.undo()
    assert doc.content == "Hello"

# Test Delete Command
def test_delete_text_command():
    doc = Document()
    doc.content = "Hello World"
    command = DeleteTextCommand(doc, 0, 5)
    command.execute()
    assert doc.content == " World"
    command.undo()
    assert doc.content == "Hello World"

# Test Factory Pattern
def test_document_factory():
    doc = DocumentFactory.create_document("text")
    assert isinstance(doc, Document)
    with pytest.raises(ValueError):
        DocumentFactory.create_document("invalid")

# Test Strategy Pattern
def test_text_formatters():
    plain_formatter = PlainTextFormatter()
    markdown_formatter = MarkdownFormatter()
    
    text = "**bold** and __italic__"
    assert plain_formatter.format(text) == text
    assert markdown_formatter.format(text) == "<b>bold</b> and <i>italic</i>"

# Test Memento Pattern
def test_document_memento():
    doc = Document()
    caretaker = DocumentCaretaker()
    
    doc.content = "First state"
    caretaker.save(doc)
    
    doc.content = "Second state"
    caretaker.save(doc)
    
    caretaker.restore(doc, 0)
    assert doc.content == "First state"
    
    caretaker.restore(doc, 1)
    assert doc.content == "Second state"

# Test Document Properties
def test_document_properties():
    doc = Document()
    doc.content = "Test content"
    assert doc.content == "Test content"

# Test Document Observer Management
def test_observer_management():
    doc = Document()
    observer1 = TestObserver()
    observer2 = TestObserver()
    
    doc.attach(observer1)
    doc.attach(observer2)
    doc.content = "test"
    
    assert observer1.updated
    assert observer2.updated
    
    doc.detach(observer1)
    observer1.updated = False
    observer2.updated = False
    
    doc.content = "new test"
    assert not observer1.updated
    assert observer2.updated

# Test Command History
def test_command_history():
    doc = Document()
    doc.content = "Initial"
    
    command1 = InsertTextCommand(doc, " text", 7)
    command2 = InsertTextCommand(doc, " more", 12)
    
    command1.execute()
    command2.execute()
    
    assert doc.content == "Initial text more"
    
    command2.undo()
    assert doc.content == "Initial text"
    
    command1.undo()
    assert doc.content == "Initial"

# Test Text Formatting
def test_text_formatting_combinations():
    formatter = MarkdownFormatter()
    
    test_cases = [
        ("**bold**", "<b>bold</b>"),
        ("__italic__", "<i>italic</i>"),
        ("**bold** and __italic__", "<b>bold</b> and <i>italic</i>"),
        ("No formatting", "No formatting")
    ]
    
    for input_text, expected in test_cases:
        assert formatter.format(input_text) == expected

# Test Document State Management
def test_document_state_management():
    doc = Document()
    caretaker = DocumentCaretaker()
    
    states = ["State 1", "State 2", "State 3"]
    
    for state in states:
        doc.content = state
        caretaker.save(doc)
    
    for i, state in enumerate(states):
        caretaker.restore(doc, i)
        assert doc.content == state

# Test Error Handling
def test_error_handling():
    doc = Document()
    caretaker = DocumentCaretaker()
    
    with pytest.raises(IndexError):
        caretaker.restore(doc, -1)
    
    with pytest.raises(IndexError):
        caretaker.restore(doc, 100)

# Test Multiple Observers
def test_multiple_observers():
    doc = Document()
    observers = [TestObserver() for _ in range(5)]
    
    for observer in observers:
        doc.attach(observer)
    
    doc.content = "test"
    
    for observer in observers:
        assert observer.updated
        assert observer.last_content == "test"

# Test Command Pattern with Multiple Operations
def test_multiple_commands():
    doc = Document()
    doc.content = "Start"
    
    commands = [
        InsertTextCommand(doc, " one", 5),
        InsertTextCommand(doc, " two", 10),
        InsertTextCommand(doc, " three", 15)
    ]
    
    for cmd in commands:
        cmd.execute()
    
    assert doc.content == "Start one two three"
    
    for cmd in reversed(commands):
        cmd.undo()
    
    assert doc.content == "Start"

# Test Document Factory with Different Types
def test_document_factory_types():
    with pytest.raises(ValueError):
        DocumentFactory.create_document("invalid")
    
    doc = DocumentFactory.create_document("text")
    assert isinstance(doc, Document)

# Test Text Formatter Edge Cases
def test_text_formatter_edge_cases():
    formatter = MarkdownFormatter()
    
    test_cases = [
        ("", ""),
        ("**", "**"),
        ("__", "__"),
        ("****", "<b></b>"),
        ("____", "<i></i>")
    ]
    
    for input_text, expected in test_cases:
        assert formatter.format(input_text) == expected

# Test Document Content Updates
def test_document_content_updates():
    doc = Document()
    observer = TestObserver()
    doc.attach(observer)
    
    test_content = [
        "First line",
        "Second line",
        "Third line"
    ]
    
    for content in test_content:
        doc.content = content
        assert observer.last_content == content

# Test Command Pattern with Empty Content
def test_command_empty_content():
    doc = Document()
    doc.content = ""
    
    command = InsertTextCommand(doc, "test", 0)
    command.execute()
    assert doc.content == "test"
    
    command.undo()
    assert doc.content == ""

# Test Memento Pattern with Empty States
def test_memento_empty_states():
    doc = Document()
    caretaker = DocumentCaretaker()
    
    doc.content = ""
    caretaker.save(doc)
    
    doc.content = "test"
    caretaker.save(doc)
    
    caretaker.restore(doc, 0)
    assert doc.content == ""
    
    caretaker.restore(doc, 1)
    assert doc.content == "test"

# Test Delete Command with Empty Content
def test_delete_empty_content():
    doc = Document()
    doc.content = ""
    
    command = DeleteTextCommand(doc, 0, 0)
    command.execute()
    assert doc.content == ""
    command.undo()
    assert doc.content == ""

# Test Delete Command with Special Characters
def test_delete_special_characters():
    doc = Document()
    special_text = "Hello\nWorld\t123!@#"
    doc.content = special_text
    
    command = DeleteTextCommand(doc, 0, len(special_text))
    command.execute()
    assert doc.content == ""
    command.undo()
    assert doc.content == special_text 