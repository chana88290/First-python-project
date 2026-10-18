from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class WorkingHours:
    start_time: time
    end_time: time