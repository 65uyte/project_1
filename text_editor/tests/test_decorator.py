from text_editor.document.document import Document
from text_editor.document.decorators import AutoSaveDecorator, DocumentDecorator, ValidationDecorator, EncryptionDecorator, StatisticsDecorator, save_decorators_metadata, load_decorators_metadata, create_decorator_chain, collect_decorators_metadata
from text_editor.document.document_factory import TxtDocument, MdDocument, RtfDocument, HtmlDocument
import tempfile
import os
import pytest
import json

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

def test_validation_decorator_accepts_valid_content():
    doc = Document()
    deco = ValidationDecorator(doc, max_length=100, forbidden_words=["bad"])
    deco.content = "good content"
    assert doc.content == "good content"

def test_validation_decorator_rejects_too_long_content():
    doc = Document()
    deco = ValidationDecorator(doc, max_length=5)
    with pytest.raises(ValueError, match="Content validation failed"):
        deco.content = "too long content"

def test_validation_decorator_rejects_forbidden_words():
    doc = Document()
    deco = ValidationDecorator(doc, forbidden_words=["bad"])
    with pytest.raises(ValueError, match="Content validation failed"):
        deco.content = "this is bad content"

def test_encryption_decorator_encrypts_and_decrypts():
    doc = Document()
    deco = EncryptionDecorator(doc, key="secret")
    original_text = "hello world"
    deco.content = original_text
    
    # Перевіряємо, що в документі зберігається зашифрований текст
    assert doc.content != original_text
    
    # Перевіряємо, що декоратор повертає розшифрований текст
    assert deco.content == original_text

def test_statistics_decorator_tracks_stats():
    doc = Document()
    deco = StatisticsDecorator(doc)
    deco.content = "hello world\nsecond line"

    stats = deco.get_statistics()
    assert stats['char_count'] == 23  # Виправлено: 23 символи включаючи \n
    assert stats['word_count'] == 4
    assert stats['line_count'] == 2

def test_decorator_chain():
    doc = Document()
    # Створюємо ланцюжок декораторів
    deco = StatisticsDecorator(
        ValidationDecorator(
            AutoSaveDecorator(doc, lambda x: None)
        )
    )
    
    deco.content = "test"
    assert doc.content == "test"
    
    stats = deco.get_statistics()
    assert stats['char_count'] == 4

def test_save_and_load_decorators_metadata():
    """Тест збереження та завантаження метадані декораторів"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        file_path = f.name
    
    try:
        # Створюємо тестові метадані
        test_metadata = [
            {"type": "AutoSave", "enabled": True},
            {"type": "Validation", "enabled": True, "max_length": 5000, "forbidden_words": ["test"]},
            {"type": "Encryption", "enabled": True, "key": "test_key"},
            {"type": "Statistics", "enabled": True}
        ]
        
        # Зберігаємо метадані
        save_decorators_metadata(file_path, test_metadata)
        
        # Перевіряємо, що файл метадані створено
        metadata_file = file_path + ".meta"
        assert os.path.exists(metadata_file)
        
        # Завантажуємо метадані
        loaded_metadata = load_decorators_metadata(file_path)
        
        # Перевіряємо, що метадані завантажено правильно
        assert len(loaded_metadata) == len(test_metadata)
        for i, metadata in enumerate(loaded_metadata):
            assert metadata["type"] == test_metadata[i]["type"]
            assert metadata["enabled"] == test_metadata[i]["enabled"]
    
    finally:
        # Очищаємо тестові файли
        if os.path.exists(file_path):
            os.unlink(file_path)
        metadata_file = file_path + ".meta"
        if os.path.exists(metadata_file):
            os.unlink(metadata_file)

def test_load_decorators_metadata_nonexistent_file():
    """Тест завантаження метадані з неіснуючого файлу"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        file_path = f.name
    
    try:
        # Видаляємо файл метадані, якщо він існує
        metadata_file = file_path + ".meta"
        if os.path.exists(metadata_file):
            os.unlink(metadata_file)
        
        # Завантажуємо метадані з неіснуючого файлу
        loaded_metadata = load_decorators_metadata(file_path)
        
        # Перевіряємо, що повернуто порожній список
        assert loaded_metadata == []
    
    finally:
        if os.path.exists(file_path):
            os.unlink(file_path)

def test_create_decorator_chain():
    """Тест створення ланцюжка декораторів з метадані"""
    doc = TxtDocument("test content")
    
    # Тестові метадані
    metadata = [
        {"type": "Validation", "enabled": True, "max_length": 100, "forbidden_words": []},
        {"type": "Statistics", "enabled": True}
    ]
    
    # Створюємо ланцюжок декораторів
    decorated_doc = create_decorator_chain(doc, metadata)
    
    # Перевіряємо, що декоратори створено правильно
    assert isinstance(decorated_doc, StatisticsDecorator)
    assert isinstance(decorated_doc._document, ValidationDecorator)
    assert isinstance(decorated_doc._document._document, TxtDocument)

def test_create_decorator_chain_with_disabled_decorators():
    """Тест створення ланцюжка з вимкненими декораторами"""
    doc = TxtDocument("test content")
    
    # Тестові метадані з вимкненими декораторами
    metadata = [
        {"type": "Validation", "enabled": True, "max_length": 100, "forbidden_words": []},
        {"type": "Statistics", "enabled": False}
    ]
    
    # Створюємо ланцюжок декораторів
    decorated_doc = create_decorator_chain(doc, metadata)
    
    # Перевіряємо, що тільки увімкнені декоратори створено
    assert isinstance(decorated_doc, ValidationDecorator)
    assert isinstance(decorated_doc._document, TxtDocument)

def test_create_decorator_chain_with_encryption():
    """Тест створення ланцюжка з шифруванням"""
    doc = TxtDocument("test content")
    
    # Тестові метадані з шифруванням
    metadata = [
        {"type": "Encryption", "enabled": True, "key": "test_key"},
        {"type": "Statistics", "enabled": True}
    ]
    
    # Створюємо ланцюжок декораторів з ключем шифрування
    decorated_doc = create_decorator_chain(doc, metadata, encryption_key="custom_key")
    
    # Перевіряємо, що декоратори створено правильно
    assert isinstance(decorated_doc, StatisticsDecorator)
    assert isinstance(decorated_doc._document, EncryptionDecorator)
    assert decorated_doc._document.key == "custom_key"

def test_collect_decorators_metadata():
    """Тест збору метадані з ланцюжка декораторів"""
    # Створюємо ланцюжок декораторів
    doc = TxtDocument("test content")
    decorated_doc = StatisticsDecorator(
        ValidationDecorator(
            doc,
            100, []
        )
    )
    
    # Збираємо метадані
    metadata = collect_decorators_metadata(decorated_doc)
    
    # Перевіряємо, що метадані зібрано правильно
    assert len(metadata) == 2
    assert metadata[0]["type"] == "Validation"
    assert metadata[1]["type"] == "Statistics"

def test_collect_decorators_metadata_no_decorators():
    """Тест збору метадані з документа без декораторів"""
    doc = TxtDocument("test content")
    
    # Збираємо метадані
    metadata = collect_decorators_metadata(doc)
    
    # Перевіряємо, що повернуто порожній список
    assert metadata == []

def test_decorator_metadata_content():
    """Тест вмісту метадані різних декораторів"""
    doc = TxtDocument("test content")
    
    # Створюємо різні декоратори
    validation_decorator = ValidationDecorator(doc, 5000, ["bad_word"])
    encryption_decorator = EncryptionDecorator(doc, "secret_key")
    statistics_decorator = StatisticsDecorator(doc)
    
    # Перевіряємо метадані
    validation_meta = validation_decorator.get_metadata()
    assert validation_meta["type"] == "Validation"
    assert validation_meta["max_length"] == 5000
    assert validation_meta["forbidden_words"] == ["bad_word"]
    
    encryption_meta = encryption_decorator.get_metadata()
    assert encryption_meta["type"] == "Encryption"
    assert encryption_meta["key"] == "secret_key"
    
    statistics_meta = statistics_decorator.get_metadata()
    assert statistics_meta["type"] == "Statistics" 