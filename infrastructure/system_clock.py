# infrastructure/system_clock.py

from datetime import datetime, timezone
from domain.common.time import Clock

class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
