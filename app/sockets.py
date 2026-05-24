# Sockets for real-time updates using Flask-SocketIO
# This file defines the SocketIO event handlers for real-time communication between the server and clients.

from . import socketio
from flask_login import current_user
from flask_socketio import emit, join_room

# WebSocket event handlers
@socketio.on('connect')
def on_connect():
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        emit('connected', {'message': 'Connected to live updates'})

# This handler is called when a client disconnects. We can perform any cleanup here if necessary.
@socketio.on('disconnect')
def on_disconnect():
    pass
