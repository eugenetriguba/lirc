from abc import ABC, abstractmethod
from typing import Union


class AbstractConnection(ABC):
    """
    Presents the interface for what we want
    a connection to look like and any base
    methods it should have.
    """

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def readline(self) -> str:
        pass

    @abstractmethod
    def send(self, data: str):
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @property
    @abstractmethod
    def address(self) -> Union[str, tuple]:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()
