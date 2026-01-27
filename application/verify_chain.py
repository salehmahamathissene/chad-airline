def verify_chain(recorded_events):
    previous = None
    for event in recorded_events:
        expected_payload = (
            repr(event.event)
            + event.actor_id
            + event.actor_role
            + event.authority
            + event.system_version
            + (previous or "")
        ).encode()

        expected = hashlib.sha256(expected_payload).hexdigest()

        if event.chain_checksum != expected:
            raise Exception(f"CHAIN BROKEN at {event.envelope_id}")

        previous = event.chain_checksum
