from typing import List, Protocol
from .observer import DocumentObserver

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
        self.notify() 