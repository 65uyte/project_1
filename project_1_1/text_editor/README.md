# Простий текстовий редактор

## Опис
Це простий текстовий редактор з підтримкою створення, редагування, збереження документів, буфера обміну, Undo/Redo та демонстрацією 5 патернів проектування (Factory Method, Decorator, Facade, Command, Observer). Дотримано SRP та OCP. Покрито модульними тестами, додано UML-діаграми, підготовлено до інтеграції з Sonar.

## Архітектура проекту

┌─────────────────────────────────────┐
│           UI Layer (Tkinter)        │  ← Презентаційний шар
├─────────────────────────────────────┤
│         Facade Layer                │  ← Шар бізнес-логіки
├─────────────────────────────────────┤
│      Document Layer                 │  ← Шар доменної логіки
├─────────────────────────────────────┤
│      Commands Layer                 │  ← Шар операцій
└─────────────────────────────────────┘

- **UI (Tkinter)**: Відповідає за взаємодію з користувачем, відображення тексту, меню, роботу з системним буфером обміну. Всі зміни тексту делегуються через Facade.
- **Facade**: Клас `EditorFacade` надає простий інтерфейс для роботи з документом, undo/redo, збереженням та відкриванням файлів. Інкапсулює складну логіку взаємодії між підсистемами.
- **Document**: Клас для зберігання тексту, підтримує патерн Observer для оновлення підписників при зміні тексту. Декоратори дозволяють розширювати функціонал (наприклад, автозбереження).
- **Commands**: Всі зміни тексту (набір, вставка, видалення) реєструються як команди (`SetTextCommand`) для підтримки undo/redo через UndoRedoManager (патерн Command).
- **Тестування**: Покрито всі основні компоненти, включаючи UI, Facade, Document, Undo/Redo.

## Використані патерни проектування

### 1. Factory Method (Генеративний патерн)

**Призначення**: Створення об'єктів без вказівки їх конкретних класів.

**Реалізація в проекті**:
```python
# document/document_factory.py
class DocumentFactory:
    def create_document(self, content: str = "") -> Document:
        return Document(content)

# Використання
factory = DocumentFactory()
document = factory.create_document("Hello World")
```

**Переваги**:
- Інкапсуляція логіки створення об'єктів
- Легко додавати нові типи документів
- Централізоване управління створенням

**Можливі розширення**:
```python
class RichDocumentFactory(DocumentFactory):
    def create_document(self, content: str = "") -> RichDocument:
        return RichDocument(content, formatting=True)
```

### 2. Decorator (Структурний патерн)

**Призначення**: Додавання нової функціональності до об'єкта без зміни його структури.

**Реалізація в проекті**:
```python
# document/decorators.py
class DocumentDecorator(Document):
    def __init__(self, document: Document):
        self._document = document

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
        self.save_callback(self._document.content)  # Автозбереження

# Використання
doc = Document()
autosave_doc = AutoSaveDecorator(doc, lambda content: save_to_file(content))
```

**Переваги**:
- Розширення функціоналу без зміни основного класу
- Композиція функціональності
- Дотримання Open/Closed Principle

**Можливі розширення**:
```python
class EncryptionDecorator(DocumentDecorator):
    def __init__(self, document: Document, key: str):
        super().__init__(document)
        self.key = key

    @property
    def content(self) -> str:
        return decrypt(self._document.content, self.key)

    @content.setter
    def content(self, value: str):
        self._document.content = encrypt(value, self.key)
```

### 3. Facade (Структурний патерн)

**Призначення**: Надання єдиного інтерфейсу до набору інтерфейсів підсистеми.

**Реалізація в проекті**:
```python
# facade/editor_facade.py
class EditorFacade:
    def __init__(self, save_callback=None):
        self.factory = DocumentFactory()
        self.undo_redo = UndoRedoManager()
        self.save_callback = save_callback or (lambda content: None)
        self.document = AutoSaveDecorator(self.factory.create_document(), self.save_callback)

    def set_content(self, content: str):
        self.document.content = content

    def get_content(self) -> str:
        return self.document.content

    def undo(self):
        self.undo_redo.undo()

    def redo(self):
        self.undo_redo.redo()

    def save_to_file(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.get_content())

# Використання
facade = EditorFacade()
facade.set_content("Hello")
facade.save_to_file("document.txt")
facade.undo()
```

**Переваги**:
- Спрощений інтерфейс для складних підсистем
- Зменшення залежностей між компонентами
- Легше тестування та підтримка

### 4. Command (Поведінковий патерн)

**Призначення**: Інкапсуляція запиту як об'єкта, що дозволяє параметризувати клієнтів з різними запитами.

**Реалізація в проекті**:
```python
# commands/command.py
class Command(Protocol):
    def execute(self):
        ...
    def undo(self):
        ...

class SetTextCommand:
    def __init__(self, document, new_text):
        self.document = document
        self.new_text = new_text
        self.prev_text = document.content

    def execute(self):
        self.document.content = self.new_text

    def undo(self):
        self.document.content = self.prev_text

# commands/undo_redo.py
class UndoRedoManager:
    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def execute(self, command: Command):
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self):
        if self._undo_stack:
            command = self._undo_stack.pop()
            command.undo()
            self._redo_stack.append(command)

    def redo(self):
        if self._redo_stack:
            command = self._redo_stack.pop()
            command.execute()
            self._undo_stack.append(command)

# Використання
manager = UndoRedoManager()
cmd = SetTextCommand(document, "New text")
manager.execute(cmd)
manager.undo()  # Повертає попередній стан
```

**Переваги**:
- Інкапсуляція операцій
- Підтримка Undo/Redo
- Легке додавання нових команд
- Відокремлення відправника від отримувача

**Можливі розширення**:
```python
class DeleteTextCommand(Command):
    def __init__(self, document, start, end):
        self.document = document
        self.start = start
        self.end = end
        self.deleted_text = document.content[start:end]

    def execute(self):
        # Видалення тексту
        pass

    def undo(self):
        # Відновлення видаленого тексту
        pass
```

### 5. Observer (Поведінковий патерн)

**Призначення**: Визначення залежності "один-до-багатьох" між об'єктами так, що при зміні стану одного об'єкта всі залежні від нього об'єкти автоматично повідомляються.

**Реалізація в проекті**:
```python
# document/document.py
class Observer(Protocol):
    def update(self, content: str):
        ...

class Document:
    def __init__(self, content: str = ""):
        self._content = content
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self._content)

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str):
        self._content = value
        self.notify()  # Автоматично повідомляє всіх observers

# document/observer.py
class DocumentObserver:
    def update(self, content: str):
        print(f"Document updated: {content}")

# Використання
doc = Document()
observer = DocumentObserver()
doc.attach(observer)
doc.content = "New content"  # Автоматично викликає observer.update()
```

**Переваги**:
- Слабка зв'язність між об'єктами
- Автоматичне оновлення залежних компонентів
- Легке додавання нових observers

**Можливі розширення**:
```python
class UIObserver(Observer):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def update(self, content: str):
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", content)

class FileObserver(Observer):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def update(self, content: str):
        with open(self.filepath, 'w') as f:
            f.write(content)
```

## Дизайн-принципи
- **Single Responsibility Principle (SRP)**: Кожен клас відповідає лише за одну задачу (UI, документ, undo/redo, facade).
- **Open/Closed Principle (OCP)**: Легко додавати нові типи документів, декоратори, команди без зміни існуючого коду.

## Проблеми коду та рефакторинг

### 1. Буфер обміну: власний vs системний

**Проблема:** Спочатку копіювання/вставлення реалізовувались через власний буфер, що не дозволяло взаємодіяти з системним clipboard Windows.

**До рефакторингу:**
```python
# commands/clipboard.py
class Clipboard:
    def __init__(self):
        self._buffer = ""
    
    def copy(self, text: str):
        self._buffer = text
    
    def paste(self) -> str:
        return self._buffer

class CopyCommand(Command):
    def __init__(self, clipboard: Clipboard, text: str):
        self.clipboard = clipboard
        self.text = text
    
    def execute(self):
        self.clipboard.copy(self.text)
    
    def undo(self):
        self.clipboard.clear()

# ui/editor_window.py
def copy(self):
    selected = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
    self.facade.copy(selected)  # Використовує власний буфер
```

**Після рефакторингу:**
```python
# ui/editor_window.py
def copy(self):
    try:
        selected = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
        self.root.clipboard_clear()
        self.root.clipboard_append(selected)  # Системний clipboard
    except tk.TclError:
        pass  # Нічого не виділено

def paste(self):
    try:
        clipboard_text = self.root.clipboard_get()  # Системний clipboard
        self.text.insert(tk.INSERT, clipboard_text)
        self.on_text_change()
    except tk.TclError:
        pass  # Буфер порожній
```

### 2. Undo/Redo для змін тексту

**Проблема:** Після переходу на системний clipboard undo/redo перестали працювати, оскільки зміни тексту не реєструвались як команди.

**До рефакторингу:**
```python
# ui/editor_window.py
def on_text_change(self, event=None):
    content = self.text.get("1.0", tk.END)[:-1]
    self.facade.set_content(content)  # Пряма зміна без команди

# facade/editor_facade.py
def undo(self):
    self.undo_redo.undo()  # Нічого не робить, бо немає команд
```

**Після рефакторингу:**
```python
# commands/command.py
class SetTextCommand:
    def __init__(self, document, new_text):
        self.document = document
        self.new_text = new_text
        self.prev_text = document.content
    
    def execute(self):
        self.document.content = self.new_text
    
    def undo(self):
        self.document.content = self.prev_text

# ui/editor_window.py
def on_text_change(self, event=None):
    content = self.text.get("1.0", tk.END)[:-1]
    if content != self.last_text:
        cmd = SetTextCommand(self.facade.document, content)
        self.facade.undo_redo.execute(cmd)  # Реєструє команду
        self.last_text = content
```

### 3. Імпорт та видалення модулів

**Проблема:** Після видалення clipboard.py залишились некоректні імпорти.

**До рефакторингу:**
```python
# facade/editor_facade.py
from text_editor.commands.clipboard import Clipboard, CopyCommand, PasteCommand  # Помилка!

class EditorFacade:
    def __init__(self, save_callback=None):
        self.clipboard = Clipboard()  # Не існує
```

**Після рефакторингу:**
```python
# facade/editor_facade.py
from text_editor.document.document_factory import DocumentFactory
from text_editor.document.decorators import AutoSaveDecorator
from text_editor.commands.undo_redo import UndoRedoManager  # Тільки потрібні імпорти

class EditorFacade:
    def __init__(self, save_callback=None):
        self.factory = DocumentFactory()
        self.undo_redo = UndoRedoManager()
        # clipboard видалено
```

### 4. Тестування UI

**Проблема:** Складність тестування Tkinter компонентів.

**Рішення:**
```python
# tests/test_ui.py
class DummyRoot:
    def __init__(self):
        self.clipboard_content = ""
    
    def clipboard_clear(self):
        self.clipboard_content = ""
    
    def clipboard_append(self, text):
        self.clipboard_content = text
    
    def clipboard_get(self):
        return self.clipboard_content

def test_copy_to_clipboard(dummy_window):
    dummy_window.text.content = "abcde"
    dummy_window.text.selection = (1, 4)
    dummy_window.copy()
    assert dummy_window.root.clipboard_content == "bcd"
```

## Структура проекту
- document: логіка документів та патерни Factory, Decorator, Observer
- commands: патерн Command для Undo/Redo
- facade: Facade для спрощення роботи з редактором
- ui: інтерфейс користувача (Tkinter)
- tests: модульні тести
- uml: діаграми

## Запуск
```
python -m text_editor.main
```

## Тестування
```
pytest --cov=text_editor tests/
```

## Якість коду
```
flake8 text_editor/
```

## Sonar
Інструкції у README після реалізації основної логіки. 