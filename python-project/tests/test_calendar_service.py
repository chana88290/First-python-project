from datetime import time, timedelta
from typing import List

from io_comp.models.event import Event
from io_comp.models.time_slot import TimeSlot
from io_comp.models.working_hours import WorkingHours
from io_comp.repositories.event_repository import EventRepository
from io_comp.services.calendar_service import CalendarService


class InMemoryEventRepository(EventRepository):

    def __init__(self, events: List[Event]):
        self._events = events

    def get_events(self) -> List[Event]:
        return self._events


def test_finds_available_ranges_for_alice_and_jack():
    events = [
        Event("Alice", "Morning meeting", time(8, 0), time(9, 30)),
        Event("Alice", "Lunch", time(13, 0), time(14, 0)),
        Event("Alice", "Yoga", time(16, 0), time(17, 0)),
        Event("Jack", "Morning meeting", time(8, 0), time(8, 50)),
        Event("Jack", "Sales call", time(9, 0), time(9, 40)),
        Event("Jack", "Lunch", time(13, 0), time(14, 0)),
        Event("Jack", "Yoga", time(16, 0), time(17, 0)),
    ]

    repository = InMemoryEventRepository(events)

    service = CalendarService(
        event_repository=repository,
        working_hours=WorkingHours(
            start_time=time(7, 0),
            end_time=time(19, 0),
        ),
    )

    result = service.find_available_slots(
        person_list=["Alice", "Jack"],
        event_duration=timedelta(minutes=60),
    )

    expected = [
        TimeSlot(time(7, 0), time(7, 0)),
        TimeSlot(time(9, 40), time(12, 0)),
        TimeSlot(time(14, 0), time(15, 0)),
        TimeSlot(time(17, 0), time(18, 0)),
    ]

    assert result == expected


def test_merges_overlapping_events():
    events = [
        Event("Alice", "First meeting", time(8, 0), time(9, 30)),
        Event("Jack", "Second meeting", time(9, 0), time(9, 40)),
    ]

    repository = InMemoryEventRepository(events)

    service = CalendarService(
        event_repository=repository,
        working_hours=WorkingHours(
            start_time=time(7, 0),
            end_time=time(19, 0),
        ),
    )

    result = service.find_available_slots(
        person_list=["Alice", "Jack"],
        event_duration=timedelta(minutes=60),
    )

    assert TimeSlot(time(7, 0), time(7, 0)) in result
    assert TimeSlot(time(9, 40), time(18, 0)) in result


def test_ignores_events_of_people_not_requested():
    events = [
        Event("Alice", "Meeting", time(8, 0), time(9, 0)),
        Event("Bob", "Long meeting", time(10, 0), time(18, 0)),
    ]

    repository = InMemoryEventRepository(events)

    service = CalendarService(
        event_repository=repository,
        working_hours=WorkingHours(
            start_time=time(7, 0),
            end_time=time(19, 0),
        ),
    )

    result = service.find_available_slots(
        person_list=["Alice"],
        event_duration=timedelta(minutes=60),
    )

    expected = [
        TimeSlot(time(7, 0), time(7, 0)),
        TimeSlot(time(9, 0), time(18, 0)),
    ]

    assert result == expected