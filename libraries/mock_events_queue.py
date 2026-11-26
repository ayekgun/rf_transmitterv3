"""
mock_events_queue.py - Reusable Thread-Safe Event Queue for Mock HTTP / TCP Servers.
Enables background worker threads to record request/response/error events safely
without directly calling Robot Framework logger APIs from non-main threads.
"""
from datetime import datetime, timezone
from itertools import count
from queue import Empty, Queue
from threading import Lock

_events = Queue()
_sequence = count(1)
_sequence_lock = Lock()

def record_mock_event(event_type, **details):
    """
    Thread-safe recording of mock events (requests, responses, errors)
    from HTTP server worker threads into an in-memory queue.
    """
    with _sequence_lock:
        sequence = next(_sequence)
    event = {
        "sequence": sequence,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        **details,
    }
    _events.put(event)
    return sequence

def drain_mock_events():
    """
    Drains all accumulated events from the queue (FIFO) on the main thread.
    """
    events = []
    while True:
        try:
            events.append(_events.get_nowait())
        except Empty:
            break
    return events

def clear_mock_events():
    """
    Clears all pending events from the queue.
    """
    drain_mock_events()
