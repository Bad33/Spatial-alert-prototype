from backend import create_app, socketio   # import the *Flask-SocketIO* instance

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, port=8000)   # this helper exists on Flask-SocketIO
