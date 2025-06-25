# UML README

У цьому файлі наведено архітектурну та поведінкову діаграми (UML) для проєкту текстового редактора.

## Архітектурна діаграма

Ця діаграма ілюструє основні компоненти системи та їх взаємозв'язки:

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

- **EditorFacade** — фасад для взаємодії з основними компонентами редактора.
- **Document** — модель документа, над яким виконуються операції.
- **Command** — патерн команд для виконання дій (редагування, скасування тощо).
- **Clipboard** — буфер обміну для копіювання/вставки.
- **Observer** — спостерігачі для відстеження змін у документі.

## Поведінкова діаграма

Ця діаграма демонструє послідовність дій при виконанні користувацьких операцій:

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant EditorFacade
    participant Document
    participant Command
    User->>UI: Edit/Save/Undo
    UI->>EditorFacade: handle_action()
    EditorFacade->>Command: execute()
    Command->>Document: change_state()
    Document-->>UI: notify_observers()
```

- **User** ініціює дію (редагування, збереження, скасування).
- **UI** передає дію фасаду редактора.
- **EditorFacade** делегує виконання відповідній команді.
- **Command** змінює стан документа.
- **Document** повідомляє UI про зміни через спостерігачів. 