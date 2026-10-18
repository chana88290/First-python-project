from datetime import time, timedelta
from pathlib import Path

from io_comp.models.working_hours import WorkingHours
from io_comp.repositories.csv_event_repository import CsvEventRepository
from io_comp.services.calendar_service import CalendarService


def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "resources" / "calendar.csv"

    repository = CsvEventRepository(str(csv_path))

    working_hours = WorkingHours(
        start_time=time(7, 0),
        end_time=time(19, 0),
    )

    calendar_service = CalendarService(
        event_repository=repository,
        working_hours=working_hours,
    )

    available_slots = calendar_service.find_available_slots(
        person_list=["Alice", "Jack"],
        event_duration=timedelta(minutes=60),
    )

    for slot in available_slots:
        if slot.start_time == slot.end_time:
            print(slot.start_time.strftime("%H:%M"))
        else:
            print(
                f"{slot.start_time.strftime('%H:%M')} - "
                f"{slot.end_time.strftime('%H:%M')}"
            )


if __name__ == "__main__":
    main()