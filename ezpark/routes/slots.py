from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ezpark.extensions import db, socketio
from ezpark.models import Slot, Location
from .auth import admin_required 
from ezpark.extensions import db

bp = Blueprint('slots', __name__, url_prefix='/slots')

@bp.route('/', methods=['POST'])
@admin_required()
def add_slot():
    data = request.get_json()
    location_id = data.get('location_id')
    name = data.get('name')

    if not location_id or not name:
        return jsonify({"msg": "Missing location_id or name"}), 400

    location = Location.query.get(location_id)
    if not location:
        return jsonify({"msg": "Location not found"}), 404

    if Slot.query.filter_by(location_id=location_id, name=name).first():
        return jsonify({"msg": f"Slot '{name}' already exists at this location"}), 409

    new_slot = Slot(location_id=location_id, name=name, is_available=True)
    db.session.add(new_slot)
    db.session.commit()
    return jsonify({"msg": "Slot added successfully", "slot": new_slot.to_dict()}), 201

@bp.route('/', methods=['GET'])
@jwt_required()
def get_all_slots():
    location_id = request.args.get('location_id', type=int)
    slots_query = Slot.query

    if location_id:
        slots_query = slots_query.filter_by(location_id=location_id)

    slots = slots_query.all()
    return jsonify([slot.to_dict() for slot in slots]), 200

@bp.route('/<int:slot_id>', methods=['GET'])
@jwt_required()
def get_slot(slot_id):
    slot = Slot.query.get(slot_id)
    if not slot:
        return jsonify({"msg": "Slot not found"}), 404
    return jsonify(slot.to_dict()), 200

@bp.route('/<int:slot_id>/availability', methods=['PUT'])
@admin_required()
def update_slot_availability(slot_id):
    slot = Slot.query.get(slot_id)
    if not slot:
        return jsonify({"msg": "Slot not found"}), 404

    data = request.get_json()
    new_availability = data.get('is_available')

    if new_availability is None or not isinstance(new_availability, bool):
        return jsonify({"msg": "Missing or invalid 'is_available' boolean"}), 400

    if slot.is_available != new_availability:
        slot.is_available = new_availability
        db.session.commit()
        socketio.emit('slot_status_update', slot.to_dict())
        return jsonify({"msg": "Slot availability updated", "slot": slot.to_dict()}), 200
    else:
        return jsonify({"msg": "Slot availability already at requested state", "slot": slot.to_dict()}), 200