# -*- coding: utf-8 -*-

from typing import Awaitable, Callable, Union
from weakref import WeakMethod
from abc import ABC, abstractmethod

__all__ = ['IObservable', 'ObserverCallback']

ObserverCallback = Union[Callable[..., Awaitable], WeakMethod]


class IObservable(ABC):
    @abstractmethod
    def on(self, event_name: str, callback: ObserverCallback) -> None:
        ...

    @abstractmethod
    async def off(self, event_name: str = None, callback: ObserverCallback = None) -> None:
        ...

    @abstractmethod
    async def emit(self, event_name: str, *args, **kwargs) -> None:
        ...
