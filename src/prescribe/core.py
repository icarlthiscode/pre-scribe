from __future__ import annotations
from typing import Union

Identifier = Union[str, int]
IndexJson = list[dict[list[str], dict[Identifier, int]]]

class IndexEntry:

    def get_score(self, identifier : Identifier) -> int:
        return self.scores.get(identifier, 0)

    def set_score(self, identifier : Identifier, score : int):
        self.scores[identifier] = score

    def add_token(self, token : str):
        self.tokens.append(token)

    def __eq__(self, other):
        return set(self.scores.items()) == set(other.scores.items())

    def __iadd__(self, other):
        if self != other:
            raise ValueError('Cannot combine entries with unequal scores')
        self.tokens += other.tokens

    def __init__(self, tokens : list[str], scores : dict[Identifier, int]):
        self.tokens = tokens
        self.scores = scores

class Index:

    @classmethod
    def new(cls,  index : IndexJson) -> Index:
        return cls(entries = [
            IndexEntry(tokens = i['tokens'], scores = i['scores'])
                for i in index
        ])

    def add_entry(self, entry : IndexEntry):
        for e in self.entries:
            if e == entry:
                e += entry
                return
        self.entries.append(entry)

    def json(self) -> IndexJson:
        return [
            { 'tokens' : i.tokens, 'scores' : i.scores }
                for i in self.entries
        ]

    def __init__(self, entries : list[IndexEntry]):
        self.entries = entries
