from datetime import datetime, timedelta
from typing import List

from io_comp.models.event import Event
from io_comp.models.time_range import TimeRange
from io_comp.models.time_slot import TimeSlot
from io_comp.models.working_hours import WorkingHours
from io_comp.repositories.event_repository import EventRepository


class CalendarService:

    def __init__(
        self,
        event_repository: EventRepository,
        working_hours: WorkingHours,
    ):
        self._event_repository = event_repository
        self._working_hours = working_hours

    def find_available_slots(
        self,
        person_list: List[str],
        event_duration: timedelta,
    ) -> List[TimeSlot]:
        if event_duration <= timedelta(0):
            raise ValueError("Event duration must be greater than zero.")
        events = self._event_repository.get_events()

        relevant_events = [
            event
            for event in events
            if event.person_name in person_list
        ]

        busy_ranges = self._merge_overlapping_events(relevant_events)
        free_slots = self._find_gaps(busy_ranges)

        return self._calculate_available_start_ranges(
            free_slots,
            event_duration,
        )

    @staticmethod
    def _merge_overlapping_events(
        events: List[Event],
    ) -> List[TimeRange]:
        if not events:
            return []

        sorted_events = sorted(
            events,
            key=lambda event: event.start_time,
        )

        merged_ranges = [
            TimeRange(
                start_time=sorted_events[0].start_time,
                end_time=sorted_events[0].end_time,
            )
        ]

        for event in sorted_events[1:]:
            last_range = merged_ranges[-1]

            if event.start_time <= last_range.end_time:
                merged_ranges[-1] = TimeRange(
                    start_time=last_range.start_time,
                    end_time=max(
                        last_range.end_time,
                        event.end_time,
                    ),
                )
            else:
                merged_ranges.append(
                    TimeRange(
                        start_time=event.start_time,
                        end_time=event.end_time,
                    )
                )

        return merged_ranges

    def _find_gaps(
        self,
        busy_ranges: List[TimeRange],
    ) -> List[TimeSlot]:
        free_slots = []
        current_time = self._working_hours.start_time

        for busy_range in busy_ranges:
            if current_time < busy_range.start_time:
                free_slots.append(
                    TimeSlot(
                        start_time=current_time,
                        end_time=busy_range.start_time,
                    )
                )

            current_time = max(
                current_time,
                busy_range.end_time,
            )

        if current_time < self._working_hours.end_time:
            free_slots.append(
                TimeSlot(
                    start_time=current_time,
                    end_time=self._working_hours.end_time,
                )
            )

        return free_slots

    @staticmethod
    def _calculate_available_start_ranges(
        free_slots: List[TimeSlot],
        event_duration: timedelta,
    ) -> List[TimeSlot]:
        available_ranges = []

        for slot in free_slots:
            slot_start = datetime.combine(
                datetime.today(),
                slot.start_time,
            )
            slot_end = datetime.combine(
                datetime.today(),
                slot.end_time,
            )

            latest_start = slot_end - event_duration

            if slot_start <= latest_start:
                available_ranges.append(
                    TimeSlot(
                        start_time=slot.start_time,
                        end_time=latest_start.time(),
                    )
                )

        return available_ranges