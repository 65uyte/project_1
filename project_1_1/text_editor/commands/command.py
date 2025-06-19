from typing import Protocol

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