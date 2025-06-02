from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ezpark.extensions import db, jwt # You still need jwt for jwt_required decorator
from ezpark.models import User
import functools

bp = Blueprint('auth', __name__, url_prefix='/')

# Helper function for role-based access control - Keep this here!
def admin_required():
    """
    Decorator to restrict access to admin users only.
    """
    def wrapper(fn):
        @functools.wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            if current_user and current_user.role == 'admin':
                return fn(*args, **kwargs)
            else:
                return jsonify({"msg": "Admin access required"}), 403
        return decorator
    return wrapper

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    if User.query.filter_by(name=name).first():
        return jsonify({"msg": "User already exists"}), 409

    new_user = User(name=name, role=role)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created successfully", "user_id": new_user.id}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    if not name or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(name=name).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user)
        return jsonify(access_token=access_token, user_id=user.id, user_role=user.role), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@bp.route('/users', methods=['GET'])
@admin_required() # Use the decorator defined in this file
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if current_user.role == 'admin' or current_user.id == user_id:
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({"msg": "Unauthorized access to user profile"}), 403