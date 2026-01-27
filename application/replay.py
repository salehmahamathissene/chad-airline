def replay(recorded_events, until=None):
    for recorded in recorded_events:
        if until and recorded.recorded_at > until:
            break
        yield recorded
