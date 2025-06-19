# Архітектурна діаграма (UML)

```mermaid
classDiagram
    class EditorFacade
    class Document
    class Command
    class Clipboard
    class Observer
    EditorFacade --> Document
    EditorFacade --> Command
    Document o-- Observer
    EditorFacade --> Clipboard
```

> Діаграма буде деталізована після реалізації основних класів. 