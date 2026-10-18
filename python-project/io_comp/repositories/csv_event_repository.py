import csv
from datetime import datetime, time
from typing import List

from io_comp.models.event import Event
from io_comp.repositories.event_repository import EventRepository


class CsvEventRepository(EventRepository):

    def __init__(self, file_path: str):
        self._file_path = file_path

    def get_events(self) -> List[Event]:
        events = []

        with open(
            self._file_path,
            mode="r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.reader(file)

            for row in reader:
                event = Event(
                    person_name=row[0],
                    subject=row[1],
                    start_time=self._parse_time(row[2]),
                    end_time=self._parse_time(row[3]),
                )
                events.append(event)

        return events

    @staticmethod
    def _parse_time(value: str) -> time:
        return datetime.strptime(
            value.strip(),
            "%H:%M",
        ).time()