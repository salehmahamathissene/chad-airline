import hashlib
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Attestation:
    """
    Cryptographic proof that an event is untampered.
    """
    hash: str
    previous_hash: Optional[str]

    @staticmethod
    def compute(payload: bytes, previous_hash: Optional[str]) -> "Attestation":
        h = hashlib.sha256()
        if previous_hash:
            h.update(previous_hash.encode())
        h.update(payload)
        return Attestation(hash=h.hexdigest(), previous_hash=previous_hash)
