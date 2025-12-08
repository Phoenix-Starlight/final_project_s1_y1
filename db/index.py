from typing import Any, Callable, Iterable, TypeVar

from .schema import Unique

# Maintain a dynamically solved reference for easy updates
# Makes deletion harder
Index = dict[Any, Callable[[], int]]
IndexReference = dict[str, Index]


# We say that it can be any subtype of Unique
T = TypeVar("T", bound=Unique, covariant=True)


def BadIndex(k, v, obj, keyword: Callable):
    return ValueError(
        f"Bad index `{k}` attempting to {keyword.__name__} `{obj}`: value `{v}` already present`"
    )


def create_indexes(unique_keys: list[str], db: Iterable[T]) -> IndexReference:
    return {key: create_index(db, key) for key in unique_keys}


def create_index(db: Iterable[T], key: str):
    index: Index = {}
    for i, record in enumerate(db):
        if (v := record[key]) in index:
            raise BadIndex(key, v, record, create_index)
        index[v] = lambda: (i)
    return index
