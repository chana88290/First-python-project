from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class TimeSlot:
    start_time: time
    end_time: time