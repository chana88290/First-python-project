from abc import ABC, abstractmethod
from typing import List

from io_comp.models.event import Event


class EventRepository(ABC):

    @abstractmethod
    def get_events(self) -> List[Event]:
        pass