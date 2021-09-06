# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from .observable import IObservable, ObserverCallback

__all__ = ['IObserver']


class IObserver(metaclass=ABCMeta):
    @abstractmethod
    def listen_to(self, observable: IObservable, event_name: str, callback: ObserverCallback) -> None:
        ...

    @abstractmethod
    def stop_listening(self, observable: IObservable = None, event_name: str = None, callback: ObserverCallback = None) -> None:
        ...
