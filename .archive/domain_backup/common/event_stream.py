from typing import Iterable
from domain.common.event_record import EventRecord


def verify_event_chain(events: Iterable[EventRecord]) -> None:
    previous_hash = None

    for event in events:
        if event.attestation.previous_hash != previous_hash:
            raise RuntimeError(
                "Event chain integrity violated"
            )
        previous_hash = event.attestation.hash
