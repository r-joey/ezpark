from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ezpark.extensions import db
from ezpark.models import Location
from .auth import admin_required # Import admin_required decorator

bp = Blueprint('locations', __name__, url_prefix='/locations')

@bp.route('/', methods=['POST'])
@admin_required()
def add_location():
    try:
        data = request.get_json()
        name = data.get('name')
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        address = data.get('address')

        if not name or not address or not longitude or not latitude:
            return jsonify({"msg": "Missing field(s)"}), 400

        if Location.query.filter_by(name=name).first():
            return jsonify({"msg": "Location with this name already exists"}), 409

        new_location = Location(name=name, address=address, latitude=latitude, longitude=longitude)
        db.session.add(new_location)
        db.session.commit()
        return jsonify({"msg": "Location added successfully", "location": new_location.to_dict()}), 201
    except Exception as e:
        return jsonify({"msg": "Something went wrong, Please try again."}), 500
    
@bp.route('/', methods=['GET'])
@jwt_required()
def get_all_locations():
    try:
        locations = Location.query.all()
        return jsonify([loc.to_dict() for loc in locations]), 200
    except Exception as e:
        return jsonify({"msg": "Something went wrong, Please try again."}), 500
    
@bp.route('/<int:location_id>', methods=['GET'])
@jwt_required()
def get_location(location_id):
    try:
        location = Location.query.get(location_id)
        if not location:
            return jsonify({"msg": "Location not found"}), 404
        return jsonify(location.to_dict()), 200
    except Exception as e:
        return jsonify({"msg": "Something went wrong, Please try again."}), 500

@bp.route('/<int:location_id>', methods=['DELETE'])
@admin_required()
def delete_location(location_id):
    try:
        location = Location.query.get(location_id)
        if not location:
            return jsonify({"msg": "Location not found"}), 404
        db.session.delete(location)
        db.session.commit()
        return jsonify({"msg": "Location deleted successfully"}), 200
    except Exception as e:
        return jsonify({"msg": "Something went wrong, Please try again."}), 500
    
@bp.route('/<int:location_id>', methods=['PUT'])
@admin_required()
def update_location(location_id):
    try:
        location = Location.query.get(location_id)
        if not location:
            return jsonify({"msg": "Location not found"}), 404

        data = request.get_json()
        name = data.get('name')
        address = data.get('address')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if name:
            existing = Location.query.filter_by(name=name).first()
            if existing and existing.id != location.id:
                return jsonify({"msg": "Location with this name already exists"}), 409
            location.name = name

        if address:
            location.address = address
        if latitude is not None:
            location.latitude = latitude
        if longitude is not None:
            location.longitude = longitude

        db.session.commit()
        return jsonify({"msg": "Location updated successfully", "location": location.to_dict()}), 200

    except Exception as e:
        return jsonify({"msg": "Something went wrong, Please try again."}), 500
