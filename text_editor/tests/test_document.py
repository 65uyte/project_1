import pytest
from text_editor.document.document import Document
from text_editor.document.decorators import AutoSaveDecorator

class DummyObserver:
    def __init__(self):
        self.updated = False
        self.last_content = None
        self.update_count = 0
    def update(self, content):
        self.updated = True
        self.last_content = content
        self.update_count += 1

def test_document_content():
    doc = Document()
    doc.content = "Hello"
    assert doc.content == "Hello"

def test_document_empty_content():
    doc = Document()
    assert doc.content == ""

def test_document_initial_content():
    doc = Document("Initial text")
    assert doc.content == "Initial text"

def test_observer_notified():
    doc = Document()
    obs = DummyObserver()
    doc.attach(obs)
    doc.content = "Test"
    assert obs.updated
    assert obs.last_content == "Test"

def test_observer_not_notified_before_attach():
    doc = Document()
    obs = DummyObserver()
    doc.content = "Test"
    doc.attach(obs)
    assert not obs.updated

def test_multiple_observers():
    doc = Document()
    obs1 = DummyObserver()
    obs2 = DummyObserver()
    doc.attach(obs1)
    doc.attach(obs2)
    doc.content = "Test"
    assert obs1.updated and obs2.updated
    assert obs1.last_content == "Test" and obs2.last_content == "Test"

def test_observer_detach():
    doc = Document()
    obs = DummyObserver()
    doc.attach(obs)
    doc.detach(obs)
    doc.content = "Test"
    assert not obs.updated

def test_observer_update_count():
    doc = Document()
    obs = DummyObserver()
    doc.attach(obs)
    doc.content = "First"
    doc.content = "Second"
    doc.content = "Third"
    assert obs.update_count == 3

def test_decorator_autosave():
    saved = {}
    def save_callback(content):
        saved['content'] = content
    doc = Document()
    deco = AutoSaveDecorator(doc, save_callback)
    deco.content = "SaveMe"
    assert saved['content'] == "SaveMe"

def test_decorator_preserves_content():
    doc = Document("Original")
    deco = AutoSaveDecorator(doc, lambda x: None)
    assert deco.content == "Original"

def test_decorator_multiple_saves():
    saved_contents = []
    def save_callback(content):
        saved_contents.append(content)
    doc = Document()
    deco = AutoSaveDecorator(doc, save_callback)
    deco.content = "First"
    deco.content = "Second"
    deco.content = "Third"
    assert saved_contents == ["First", "Second", "Third"] 