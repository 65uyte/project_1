from abc import ABC, abstractmethod

class DocumentObserver(ABC):
    @abstractmethod
    def update(self, content: str):
        pass

class PrintObserver(DocumentObserver):
    def update(self, content: str):
        print(f"Document updated: {content}")

class FileLogObserver(DocumentObserver):
    def __init__(self, filepath):
        self.filepath = filepath

    def update(self, content: str):
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(f"Document updated: {content}\n") 