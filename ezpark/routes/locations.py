from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ezpark.extensions import db
from ezpark.models import Location
from .auth import admin_required # Import admin_required decorator

bp = Blueprint('locations', __name__, url_prefix='/locations')

@bp.route('/', methods=['POST'])
@admin_required()
def add_location():
    data = request.get_json()
    name = data.get('name')
    address = data.get('address')

    if not name or not address:
        return jsonify({"msg": "Missing name or address"}), 400

    if Location.query.filter_by(name=name).first():
        return jsonify({"msg": "Location with this name already exists"}), 409

    new_location = Location(name=name, address=address)
    db.session.add(new_location)
    db.session.commit()
    return jsonify({"msg": "Location added successfully", "location": new_location.to_dict()}), 201

@bp.route('/', methods=['GET'])
@jwt_required()
def get_all_locations():
    locations = Location.query.all()
    return jsonify([loc.to_dict() for loc in locations]), 200

@bp.route('/<int:location_id>', methods=['GET'])
@jwt_required()
def get_location(location_id):
    location = Location.query.get(location_id)
    if not location:
        return jsonify({"msg": "Location not found"}), 404
    return jsonify(location.to_dict()), 200