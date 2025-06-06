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
    try:
        data = request.get_json() 
        email = data.get('email')
        password = data.get('password') 

        if not email or not password:
            return jsonify({"msg": "Missing username or password"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"msg": "User already exists"}), 409

        new_user = User(email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User created successfully", "user_id": new_user.id}), 201
    
    except Exception as e:
        return jsonify({"msg": f"Something went wrong, Please try again.: {e}"}), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"msg": "Missing username or password"}), 400

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user, additional_claims={"role": user.role})
            return jsonify(access_token=access_token, user_id=user.id, user_role=user.role), 200
        else:
            return jsonify({"msg": "Bad username or password"}), 401
    except Exception as e:
        return jsonify({"msg": "Something went wrong, Please try again."}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"msg": "User not found"}), 404

        data = request.get_json()
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name) 

        db.session.commit()
        return jsonify({"msg": "Profile updated", "user": user.to_dict()}), 200
    except Exception as e:
        return jsonify({"msg": f"Something went wrong: {e}"}), 500

@bp.route('/profile/password', methods=['PUT'])
@jwt_required()
def update_password():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"msg": "User not found"}), 404

        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not new_password:
            return jsonify({"msg": "New password is required"}), 400

        if not user.check_password(old_password):
            return jsonify({"msg": "Old password is incorrect"}), 400

        user.set_password(new_password)
        db.session.commit()
        return jsonify({"msg": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"msg": f"Something went wrong: {e}, Please try again."}), 500

@bp.route('/users', methods=['GET'])
@admin_required()
def get_users():
    try:
        users = User.query.filter(User.role != 'admin').all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({"msg": f"Something went wrong: {e}"}), 500

@bp.route('/users/<user_id>', methods=['DELETE'])
@admin_required()
def deactivate_user(user_id):
    try:
        # Only admins can access this route (admin_required)
        user = User.query.get(user_id)

        if not user:
            return jsonify({"msg": "User not found"}), 404

        if user.role == 'admin':
            return jsonify({"msg": "Cannot deactivate an admin user"}), 403

        if user.status == 'inactive':
            return jsonify({"msg": "User is already deactivated"}), 400

        user.status = 'inactive'
        db.session.commit()

        return jsonify({"msg": "User deactivated successfully", "user": user.to_dict()}), 200
    except Exception as e:
        return jsonify({"msg": f"Something went wrong: {e}"}), 500

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"msg": "User not found"}), 404

        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({"msg": f"Something went wrong: {e}"}), 500
