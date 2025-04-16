# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2025 vionya
import time
from collections.abc import MutableMapping
from typing import NamedTuple


class ExpiringEntry[T](NamedTuple):
    value: T
    """the actual value of this entry"""

    created_at: float
    """when this entry was created, as a result of time.monotonic()"""


class TimedCache[KT, VT](MutableMapping):
    __slots__ = ("__underlying_store", "__size", "timeout")

    timeout: int
    __underlying_store: dict[KT, ExpiringEntry[VT]]
    __size: int

    def __init__(
        self,
        timeout: int = 60,
    ):
        self.timeout = timeout
        self.__underlying_store = {}
        self.__size = 0

    # abstract methods

    def clear(self):
        self.__size = 0
        self.__underlying_store.clear()

    def __setitem__(self, key: KT, value: VT):
        if key in self:
            del self.__underlying_store[key]

        self.__size += 1
        self.__underlying_store[key] = ExpiringEntry(value, time.monotonic())

    def __getitem__(self, key: KT):
        # check if the entry is stale, evict and raise an error if it is
        if self._is_stale(key):
            del self[key]
            raise KeyError(f"'{key}' is a stale entry")

        # handles standard KeyErrors automatically
        return self.__underlying_store[key].value

    def __delitem__(self, key: KT):
        self.__size -= 1
        del self.__underlying_store[key]

    def __iter__(self):
        """
        Iterate over the keys of this TimedCache

        NOTE: this method skips over stale entries, but does NOT evict them
        """
        for key in self.__underlying_store:
            if not self._is_stale(key):
                yield key

    def __len__(self):
        return self.__size

    # public API

    def evict_all(self):
        """
        Force-evicts all stale entries from the cache
        """
        for key in list(self.__underlying_store.keys()):
            if self._is_stale(key):
                del self[key]

    # private API

    def _is_stale(self, key: KT) -> bool:
        return (
            time.monotonic() - self.__underlying_store[key].created_at
        ) >= self.timeout
