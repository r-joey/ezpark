from flask import Flask, request 
from .config import config_by_name
from .extensions import db, jwt, socketio, cors, migrate 
from .models import User
from .routes import auth, locations, slots, reservations 
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    environment = os.environ.get('ENVIRONMENT', 'development')
    app.config.from_object(config_by_name[environment])


    # Initialize extensions
    socketio.init_app(app, cors_allowed_origins="*")
    cors.init_app(app, resources={r"/*": {"origins": "*"}}) # Apply CORS to all routes
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints for routes
    app.register_blueprint(auth.bp)
    app.register_blueprint(locations.bp)
    app.register_blueprint(slots.bp)
    app.register_blueprint(reservations.bp)

    # JWT Callbacks  
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """
        Specifies what data to store in the JWT token (e.g., user ID).
        This function now receives the User object directly.
        """
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        Specifies how to load a user from the identity stored in the JWT token.
        The identity is now a UUID string.
        """
        identity = jwt_data["sub"]
        return User.query.get(identity)

    @socketio.on('connect')
    def handle_connect():
        print('Client connected:', request.sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected:', request.sid)


    return app