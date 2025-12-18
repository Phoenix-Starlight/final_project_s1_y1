from typing import Any, Callable, Iterable, TypeVar

from .errors import UniqueError as _UniqueError
from .schema import Unique

# Maintain a pointer for easy updates
# Means deletions need to set the value to None
Index = dict[Any, int]
IndexReference = dict[str, Index]


# We say that it can be any subtype of Unique
T = TypeVar("T", bound=Unique, covariant=True)

def UniqueError(k, v, obj, keyword: Callable):
    return _UniqueError(
        f"`Attempting to {keyword.__name__} `{obj}` in index `{k}`: value `{v}` already present`"
    )


def create_indexes(unique_keys: list[str], db: Iterable[T]) -> IndexReference:
    return {key: create_index(db, key) for key in unique_keys}


def create_index(db: Iterable[T], key: str):
    index: Index = {}
    for i, record in enumerate(db):
        if (v := record[key]) in index:
            err = UniqueError(key, v, record, create_index)
            err.add_note(f"Column {key} has value `{v}` in {record} at line {i+1}")
            raise err
        index[v] = i
    return index
