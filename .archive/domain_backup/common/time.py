from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """
    Domain clock abstraction.
    Time must be injected into the domain, never pulled from the system.
    """

    @abstractmethod
    def now(self) -> datetime:
        """
        Returns the current time as a timezone-aware datetime.
        """
        raise NotImplementedError
