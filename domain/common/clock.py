from datetime import datetime, timezone


class Clock:
    @staticmethod
    def business_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def system_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def infrastructure_now() -> datetime:
        return datetime.now(timezone.utc)
