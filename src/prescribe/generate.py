import re
from typing import Callable, TypeVar

from .core import Index, IndexEntry, Identifier

RT = TypeVar('RT')
def generate_index(
    records : list[RT],
    identifier : Callable[[RT], Identifier],
    tokenizer : Callable[[RT], str],
    scorer : Callable[[RT, str], int] = None,
) -> Index:
    compiled_tokens : dict[str, dict[Identifier, int]] = {}
    for record in records:
        tokens = tokenizer(record)
        for token in tokens:
            if token not in compiled_tokens: compiled_tokens[token] = {}
            compiled_tokens[token].update(
                { identifier(record) :
                    1 if scorer is None else scorer(record, token) },
            )

    index = Index(entries = [])
    for token, scores in compiled_tokens.items():
        index.add_entry(IndexEntry(tokens = [token], scores = scores))

    return index

def create_tokenizer(
    serializer : Callable[[RT], str] = None,
) -> Callable[[RT], list[str]]:

    def tokenizer(record : RT) -> list[str]:
        text = record if serializer is None else serializer(record)
        text = text.lower()
        words = re.sub(r'[^\w]', ' ', text).split()
        tokens = []
        for w in words:
            for i in range(1, len(w) + 1):
                token = w[:i]
                if token not in tokens: tokens.append(token)
        return tokens

    return tokenizer

def create_scorer(
    serializer : Callable[[RT], str] = None,
    factor : int = 1,
    cumulative : bool = True
) -> Callable[[RT, str], list[str]]:

    def scorer(record : RT, token : str) -> int:
        text = record if serializer is None else serializer(record)
        text = text.lower()
        words = re.sub(r'[^\w]', ' ', text).split()

        count = 0
        for w in words:
            if re.match(re.escape(token), w): count += 1

        if count <= 0: return 0
        return  count * factor if cumulative else factor

    return scorer

def combine_scorers(
    *scorers : list[Callable[[RT, str], int]],
) -> Callable[[RT, str], int]:

    def scorer(record : RT, token : str) -> int:
        return sum([ s(record, token) for s in scorers ])

    return scorer
