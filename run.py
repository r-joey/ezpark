from ezpark import create_app
from ezpark.extensions import socketio, db

app = create_app()

if __name__ == '__main__': 
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)