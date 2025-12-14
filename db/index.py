from typing import Any, Callable, Iterable, TypeVar

from .errors import BadIndex as _BadIndex
from .schema import Unique

# Maintain a pointer for easy updates
# Means deletions need to set the value to None
Index = dict[Any, int]
IndexReference = dict[str, Index]


# We say that it can be any subtype of Unique
T = TypeVar("T", bound=Unique, covariant=True)

def BadIndex(k, v, obj, keyword: Callable):
    return _BadIndex(
        f"Bad index `{k}` attempting to {keyword.__name__} `{obj}`: value `{v}` already present`"
    )


def create_indexes(unique_keys: list[str], db: Iterable[T]) -> IndexReference:
    return {key: create_index(db, key) for key in unique_keys}


def create_index(db: Iterable[T], key: str):
    index: Index = {}
    for i, record in enumerate(db):
        if (v := record[key]) in index:
            err = BadIndex(key, v, record, create_index)
            err.add_note(f"Column {key} has value `{v}` in {record} at line {i+1}")
            raise err
        index[v] = i
    return index
