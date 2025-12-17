from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Iterable, Dict, Any, Optional

from .models import FlashcardSet, Flashcard

@dataclass(frozen=True)
class CardDTO:
    question: str
    answer: str

class FlashcardSetCreator(ABC):
    @abstractmethod
    def create_set(selfself) -> FlashcardSet:
        raise NotImplementedError

class UserFlashcardSetCreator(FlashcardSetCreator):
    def __init__(self, name: str, cards: Iterable[CardDTO]):
        self.name = (name or "").strip()
        self.cards = list(cards)

    def create_set(self) -> FlashcardSet:
        flashcard_set = FlashcardSet.objects.create(name=self.name)

        objs: List[Flashcard] = []
        for c in self.cards:
            q = (c.question or "").strip()
            a = (c.answer or "").strip()
            if q and a:
                objs.append(Flashcard(set=flashcard_set, question=q, answer=a))

        if objs:
            Flashcard.objects.bulk_create(objs)

        return flashcard_set

# class PredefinedFlashcardSetCreator(FlashcardSetCreator):
#     def __init__(self, predefined_set: Dict[str, Any], set_key: str):
#         self.predefined_set = predefined_set
#         self.set_key = set_key
#
#     def create_set(self) -> FlashcardSet:
#         data = self.predefined_set[self.set_key]
#         title = (data.get("title") or "").strip()
#
#         flashcard_set = FlashcardSet.objects.create(name=title)
#
#         objs: List[Flashcard] = []
#         for c in data.get("cards", []):
#             q = (c.question or "").strip()
#             a = (c.answer or "").strip()
#             if q and a:
#                 objs.append(Flashcard(set=flashcard_set, question=q, answer=a))
#
#         if objs:
#             Flashcard.objects.bulk_create(objs)
#
#         return flashcard_set