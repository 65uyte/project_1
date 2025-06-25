# Text Editor with Design Patterns

A text editor implementation that demonstrates various design patterns and best practices in software development.

## Features

- Create, edit, and save text documents
- Undo/Redo functionality
- Multiple text formatting options
- Document state management
- Observer pattern for document changes
- Command pattern for operations
- Factory pattern for document creation
- Memento pattern for state management
- Strategy pattern for text formatting

## Design Patterns Used

1. **Observer Pattern** (Behavioral)
   - Used for notifying observers about document changes
   - Implements document state monitoring

2. **Command Pattern** (Behavioral)
   - Implements undo/redo functionality
   - Encapsulates document operations

3. **Factory Pattern** (Creational)
   - Creates different types of documents
   - Provides a flexible way to instantiate document objects

4. **Memento Pattern** (Behavioral)
   - Saves and restores document states
   - Implements history functionality

5. **Strategy Pattern** (Behavioral)
   - Implements different text formatting strategies
   - Allows for easy addition of new formatting options

## Design Principles

1. **Single Responsibility Principle**
   - Each class has a single responsibility
   - Clear separation of concerns between document management, UI, and formatting

2. **Open/Closed Principle**
   - The system is open for extension but closed for modification
   - New formatters can be added without modifying existing code

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python text_editor.py
```

## Running Tests

```bash
pytest test_text_editor.py
```

## Project Structure

- `text_editor.py` - Main application implementation
- `test_text_editor.py` - Unit tests
- `requirements.txt` - Project dependencies

## UML Diagrams

### Class Diagram
```
[Document] <|-- [TextDocument]
[DocumentObserver] <|.. [TestObserver]
[Command] <|-- [InsertTextCommand]
[TextFormatter] <|-- [PlainTextFormatter]
[TextFormatter] <|-- [MarkdownFormatter]
[DocumentFactory] --> [Document]
[DocumentCaretaker] --> [DocumentMemento]
```

### Sequence Diagram
```
User -> TextEditor: Create new document
TextEditor -> DocumentFactory: create_document()
DocumentFactory -> Document: new()
TextEditor -> Document: attach(observer)
User -> TextEditor: Edit text
TextEditor -> Command: execute()
Command -> Document: update content
Document -> Observer: notify()
```

## Code Quality

The project includes:
- Comprehensive unit tests (20+ test cases)
- Code documentation
- Type hints
- Error handling
- Clean code principles

## Future Improvements

1. Add more text formatting options
2. Implement file encryption
3. Add collaborative editing features
4. Implement plugin system
5. Add syntax highlighting 