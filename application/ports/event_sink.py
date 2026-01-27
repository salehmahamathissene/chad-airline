from abc import ABC, abstractmethod
from domain.common.events import DomainEvent
from domain.common.failures import DomainFailure


class EventSink(ABC):
    """
    Contract for persisting or publishing domain facts.
    """

    @abstractmethod
    def record_event(self, event: DomainEvent) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_failure(self, failure: DomainFailure) -> None:
        raise NotImplementedError
