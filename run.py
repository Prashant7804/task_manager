from app import create_app, socketio

app = create_app() # Create Flask app instance

if __name__ == '__main__':
    socketio.run(app, debug=True)