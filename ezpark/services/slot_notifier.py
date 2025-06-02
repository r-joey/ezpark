# ezpark/services/slot_notifier.py
from ezpark.extensions import socketio

def notify_slot_status_update(slot_data):
    """
    Emits a SocketIO event to all connected clients about a slot status change.
    """
    socketio.emit('slot_status_update', slot_data)