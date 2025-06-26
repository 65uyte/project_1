from .document import Document
import json
import os
from datetime import datetime
import re

class DocumentDecorator(Document):
    def __init__(self, document: Document):
        self._document = document

    @property
    def content(self) -> str:
        return self._document.content

    @content.setter
    def content(self, value: str):
        self._document.content = value

    def get_metadata(self) -> dict:
        """Повертає метадані декоратора"""
        return {"type": self.__class__.__name__}

class AutoSaveDecorator(DocumentDecorator):
    def __init__(self, document: Document, save_callback):
        super().__init__(document)
        self.save_callback = save_callback

    @property
    def content(self) -> str:
        return self._document.content

    @content.setter
    def content(self, value: str):
        self._document.content = value
        self.save_callback(self._document.content)

    def get_metadata(self) -> dict:
        return {"type": "AutoSave", "enabled": True}

class ValidationDecorator(DocumentDecorator):
    def __init__(self, document: Document, max_length: int = 10000):
        super().__init__(document)
        self.max_length = max_length

    @property
    def content(self) -> str:
        return self._document.content

    @content.setter
    def content(self, value: str):
        if self._validate_content(value):
            self._document.content = value
        else:
            raise ValueError("Content validation failed")

    def _validate_content(self, content: str) -> bool:
        # Перевірка довжини
        return len(content) <= self.max_length

    def get_metadata(self) -> dict:
        return {
            "type": "Validation", 
            "enabled": True, 
            "max_length": self.max_length
        }

class EncryptionDecorator(DocumentDecorator):
    MAGIC = "MAGIC:"
    def __init__(self, document: Document, key: str = "default_key"):
        super().__init__(document)
        self.key = key

    @property
    def content(self) -> str:
        encrypted_content = self._document.content
        decrypted = self._decrypt(encrypted_content)
        if not decrypted.startswith(self.MAGIC):
            raise ValueError("Неправильний пароль для розшифрування")
        return decrypted[len(self.MAGIC):]

    @content.setter
    def content(self, value: str):
        value_with_magic = self.MAGIC + value
        encrypted_value = self._encrypt(value_with_magic)
        self._document.content = encrypted_value

    def _encrypt(self, text: str) -> str:
        # Простий XOR шифр
        encrypted = ""
        for i, char in enumerate(text):
            key_char = self.key[i % len(self.key)]
            encrypted += chr(ord(char) ^ ord(key_char))
        return encrypted

    def _decrypt(self, text: str) -> str:
        return self._encrypt(text)

    def get_metadata(self) -> dict:
        return {"type": "Encryption", "enabled": True, "key": self.key}

class StatisticsDecorator(DocumentDecorator):
    def __init__(self, document: Document):
        super().__init__(document)
        self.stats = {
            'char_count': 0,
            'word_count': 0,
            'line_count': 0,
            'last_modified': None
        }

    @property
    def content(self) -> str:
        return self._document.content

    @content.setter
    def content(self, value: str):
        self._document.content = value
        self._update_stats(value)

    def _update_stats(self, content: str):
        self.stats['char_count'] = len(content)
        self.stats['word_count'] = len(content.split()) if content.strip() else 0
        self.stats['line_count'] = len(content.splitlines()) if content else 0
        self.stats['last_modified'] = datetime.now().isoformat()

    def get_statistics(self) -> dict:
        return self.stats.copy()

    def get_metadata(self) -> dict:
        return {"type": "Statistics", "enabled": True}

def save_decorators_metadata(file_path: str, decorators_metadata: list):
    """Зберігає метадані декораторів у JSON файл в D:\Documents\Data"""
    metadata_dir = "D:\\Documents\\Data"
    os.makedirs(metadata_dir, exist_ok=True)
    
    import hashlib
    file_hash = hashlib.md5(file_path.encode()).hexdigest()
    metadata_file = os.path.join(metadata_dir, f"{file_hash}.meta")
    
    metadata = {
        "file_path": file_path,
        "decorators": decorators_metadata
    }
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

def load_decorators_metadata(file_path: str) -> list:
    """Завантажує метадані декораторів з JSON файлу в D:\Documents\Data"""
    metadata_dir = "D:\\Documents\\Data"
    import hashlib
    file_hash = hashlib.md5(file_path.encode()).hexdigest()
    metadata_file = os.path.join(metadata_dir, f"{file_hash}.meta")
    
    if os.path.exists(metadata_file):
        # Перевіряємо, чи існує основний файл
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            stored_file_path = metadata.get("file_path", "")
            
            if not os.path.exists(stored_file_path):
                os.remove(metadata_file)
                return []
            
            return metadata.get("decorators", [])
    return []

def cleanup_orphaned_metadata():
    """Видаляє метадані для файлів, які більше не існують"""
    metadata_dir = "D:\\Documents\\Data"
    if not os.path.exists(metadata_dir):
        return
    
    for filename in os.listdir(metadata_dir):
        if filename.endswith('.meta'):
            metadata_file = os.path.join(metadata_dir, filename)
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    stored_file_path = metadata.get("file_path", "")
                    
                    if not os.path.exists(stored_file_path):
                        os.remove(metadata_file)
                        print(f"Removed orphaned metadata: {filename}")
            except Exception as e:
                print(f"Error processing metadata file {filename}: {e}")

def create_decorator_chain(document: Document, decorators_metadata: list, save_callback=None, encryption_key=None):
    """Створює ланцюжок декораторів на основі метадані"""
    decorated_doc = document
    
    for decorator_info in decorators_metadata:
        if not decorator_info.get("enabled", False):
            continue
            
        decorator_type = decorator_info["type"]
        
        if decorator_type == "AutoSave" and save_callback:
            decorated_doc = AutoSaveDecorator(decorated_doc, save_callback)
        elif decorator_type == "Validation":
            max_length = decorator_info.get("max_length", 10000)
            decorated_doc = ValidationDecorator(decorated_doc, max_length)
        elif decorator_type == "Encryption":
            key = encryption_key or decorator_info.get("key", "default_key")
            decorated_doc = EncryptionDecorator(decorated_doc, key)
        elif decorator_type == "Statistics":
            decorated_doc = StatisticsDecorator(decorated_doc)
    
    return decorated_doc

def collect_decorators_metadata(document) -> list:
    """Збирає метадані з ланцюжка декораторів"""
    metadata = []
    current_doc = document
    
    while hasattr(current_doc, '_document'):
        if hasattr(current_doc, 'get_metadata'):
            metadata.append(current_doc.get_metadata())
        current_doc = current_doc._document
    
    return metadata[::-1]