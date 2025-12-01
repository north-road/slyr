"""
Utilities
"""

import collections
from typing import TypeVar, Dict, Tuple, Any, Iterator, Optional

_VT = TypeVar("_VT")


class CaseInsensitiveKeyDict(collections.abc.MutableMapping[str, _VT]):
    def __init__(self, data=None, **kwargs: _VT):
        self._store: Dict[Optional[str], Tuple[Optional[str], _VT]] = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key: Optional[str], value: _VT):
        if key is None:
            self._store[key] = (key, value)
        else:
            self._store[key.lower()] = (key, value)

    def __getitem__(self, key: Optional[str]) -> _VT:
        if key is None:
            return self._store[key][1]
        return self._store[key.lower()][1]

    def __delitem__(self, key: Optional[str]) -> None:
        if key is None:
            del self._store[key]
        else:
            del self._store[key.lower()]

    def __iter__(self) -> Iterator[Optional[str]]:
        return (cased_key for cased_key, mapped_value in self._store.values())

    def __len__(self) -> int:
        return len(self._store)

    def lower_items(self) -> Iterator[Tuple[Optional[str], _VT]]:
        return ((lower_key, key_val[1]) for (lower_key, key_val) in self._store.items())

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, collections.abc.Mapping):
            other = CaseInsensitiveKeyDict(other)
        else:
            return NotImplemented
        return dict(self.lower_items()) == dict(other.lower_items())

    def copy(self) -> "CaseInsensitiveKeyDict[_VT]":
        return CaseInsensitiveKeyDict(self._store.values())

    def __repr__(self) -> str:
        return "%s(%r)" % (self.__class__.__name__, dict(self.items()))
