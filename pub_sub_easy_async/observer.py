# -*- coding: utf-8 -*-

import asyncio
from weakref import WeakKeyDictionary
from collections import defaultdict
from typing import Dict, Set

from .interface import IObservable, ObserverCallback, IObserver


class Observer(IObserver):
    """
    Класс "наблюдатель" для релаизации паттерна Observer (Pub/Sub).
    """
    _subscriptions: Dict[IObservable, Dict[str, Set[ObserverCallback]]]

    def __init__(self):
        super().__init__()
        self._subscriptions = WeakKeyDictionary()

    def listen_to(self, observable: IObservable, event_name: str, callback: ObserverCallback) -> None:
        """
        Подписывает инстанс на событие event_name у observable.

        :param observable: Объект, на событие которого подписываемся.
        :param event_name: Название события.
        :param callback: Callback для вызова.
        """

        if observable not in self._subscriptions:
            self._subscriptions[observable] = defaultdict(set)

        self._subscriptions[observable][event_name].add(callback)
        observable.on(event_name, callback)

    async def stop_listening(self, observable: IObservable = None, event_name: str = None,
                             callback: ObserverCallback = None) -> None:
        """
        Отписываемся от событий, на которые подписывались с помощью listen_to.

        :param observable: Объект, на событие которого подписывались, None, отпишемся ото всех.
        :param event_name: Название события, на которое были подписаны, None - отпишемся от всех событий observable.
        :param callback: Callback, который был подписан, если None - отпишем все Callback для event_name observable.
        """
        subs = {}
        if observable is None:
            subs = self._subscriptions
        elif event_name is None:
            subs = WeakKeyDictionary({
                observable: self._subscriptions.get(observable, {})
            })
        elif callback is None:
            subs = WeakKeyDictionary({
                observable: {
                    event_name: self._subscriptions.get(observable, {}).get(event_name, set())
                }
            })
        else:
            event_subs = self._subscriptions.get(observable, {}).get(event_name, set())
            if callback in event_subs:
                subs = WeakKeyDictionary({
                    observable: {
                        event_name: {callback}
                    }
                })

        off_tasks = []
        for observable, subscriptions in subs.items():
            for event_name, callbacks in subscriptions.items():
                for callback in callbacks.copy():
                    off_tasks.append(asyncio.create_task(observable.off(event_name, callback)))
                    self._subscriptions[observable][event_name].remove(callback)

        if off_tasks:
            await asyncio.gather(*off_tasks)
