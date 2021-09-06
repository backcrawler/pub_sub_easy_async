# -*- coding: utf-8 -*-

import asyncio
from collections import defaultdict
from typing import Dict, Set, Awaitable, Callable
from weakref import WeakMethod

from .interface import IObservable, ObserverCallback


class Observable(IObservable):
    """
    Класс "наблюдаемый" для релаизации паттерна Observer (Pub/Sub).
    """

    _subscribes: Dict[str, Set[Callable[..., Awaitable]]]
    _weak_subscribes: Dict[str, Set[WeakMethod]]
    _emit_lock: asyncio.Lock

    def __init__(self):
        super().__init__()
        self._subscribes = defaultdict(set)
        self._weak_subscribes = defaultdict(set)
        self._emit_lock = asyncio.Lock()

    def on(self, event_name: str, callback: ObserverCallback) -> None:
        """
        "Подписывает" cb на событие event_name.

        :param event_name: Название события.
        :param callback: Callback для вызова по событию.
        """
        if isinstance(callback, WeakMethod):
            self._clean_dead_ref_callbacks(event_name)
            self._weak_subscribes[event_name].add(callback)
        else:
            self._subscribes[event_name].add(callback)

    async def off(self, event_name: str = None, callback: ObserverCallback = None) -> None:
        """
        "Отписка" от событий.

        :param event_name: Название события, если None - отписывает от всех.
        :param callback: Callback, который был подписан. Если None - отписывает все события для event_name.
        """
        async with self._emit_lock:
            if event_name is None:
                self._subscribes.clear()
            elif callback is None:
                self._subscribes[event_name].clear()
            elif callback in self._subscribes[event_name]:
                self._subscribes[event_name].remove(callback)
            elif callback in self._weak_subscribes[event_name]:
                self._weak_subscribes[event_name].remove(callback)

    async def emit(self, event_name: str, *args, **kwargs) -> None:
        """
        Выполняем все callback'и соответсвующие event_name.

        :param str event_name: Название события.
        :param args: Аргументы для передачи в callback
        :param kwargs: Ключевые аргументы для передачи в callback
        :return:
        """
        async with self._emit_lock:
            self._clean_dead_ref_callbacks(event_name)
            callbacks = self._subscribes[event_name] or {weak() for weak in self._weak_subscribes[event_name]}
            if callbacks:
                await asyncio.gather(*[cb(*args, **kwargs) for cb in callbacks])

    def _clean_dead_ref_callbacks(self, event_name: str) -> None:
        self._weak_subscribes[event_name] = {weak for weak in self._weak_subscribes[event_name] if weak() is not None}
