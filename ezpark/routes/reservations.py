from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ezpark.extensions import db, socketio
from ezpark.models import Reservation, Slot, User
from .auth import admin_required # Import admin_required decorator
import datetime

bp = Blueprint('reservations', __name__, url_prefix='/reservations')

@bp.route('/', methods=['POST'])
@jwt_required()
def create_reservation():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        slot_id = data.get('slot_id')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        
        start_time = None
        end_time = None
        if start_time_str and end_time_str:
            try:
                start_time = datetime.datetime.fromisoformat(start_time_str)
                end_time = datetime.datetime.fromisoformat(end_time_str)
            except ValueError:
                return jsonify({"msg": "Invalid end_time format. Use ISO 8601."}), 400

        if not slot_id:
            return jsonify({"msg": "Missing slot_id"}), 400

        slot = Slot.query.get(slot_id)
        if not slot:
            return jsonify({"msg": "Slot not found"}), 404
        if not slot.is_available:
            return jsonify({"msg": "Slot is not available"}), 409

        existing_reservation = Reservation.query.filter_by(
            user_id=current_user_id,
            slot_id=slot_id,
            status='active'
        ).first()
        if existing_reservation:
            return jsonify({"msg": "You already have an active reservation for this slot."}), 409

        new_reservation = Reservation(
            slot_id=slot_id,
            user_id=current_user_id,
            start_time=start_time,
            end_time=end_time,
            status='active'
        )
        db.session.add(new_reservation)

        slot.is_available = False
        db.session.commit()

        socketio.emit('slot_status_update', slot.to_dict())

        return jsonify({"msg": "Reservation created successfully", "reservation": new_reservation.to_dict()}), 201
    except Exception as e:
        return jsonify({"msg": "Something went wrong, Please try again."}), 500
    
@bp.route('/', methods=['GET'])
@jwt_required()
def get_reservations():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if current_user.role == 'admin':
            reservations = Reservation.query.all()
        else:
            reservations = Reservation.query.filter_by(user_id=current_user_id).all()

        return jsonify([res.to_dict() for res in reservations]), 200
    except Exception as e:
        return jsonify({"msg": "Something went wrong, Please try again."}), 500
    
@bp.route('/<int:reservation_id>', methods=['DELETE'])
@jwt_required()
def cancel_reservation(reservation_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({"msg": "Reservation not found"}), 404

        if current_user.role == 'admin' or reservation.user_id == current_user_id:
            if reservation.status == 'cancelled':
                return jsonify({"msg": "Reservation is already cancelled"}), 400

            reservation.status = 'cancelled'
            db.session.commit()

            slot = Slot.query.get(reservation.slot_id)
            if slot and not slot.is_available:
                slot.is_available = True
                db.session.commit()
                socketio.emit('slot_status_update', slot.to_dict())

            return jsonify({"msg": "Reservation cancelled successfully", "reservation": reservation.to_dict()}), 200
        else:
            return jsonify({"msg": "Unauthorized to cancel this reservation"}), 403
    except Exception as e:
        return jsonify({"msg": "Something went wrong, Please try again."}), 500

@bp.route('/complete/<int:reservation_id>', methods=['PUT'])
@jwt_required()
def complete_reservation(reservation_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({"msg": "Reservation not found"}), 404

        if current_user.role == 'admin' or reservation.user_id == current_user_id:
            if reservation.status == 'completed':
                return jsonify({"msg": "Reservation is already completed"}), 400

            reservation.status = 'completed'
            db.session.commit()

            slot = Slot.query.get(reservation.slot_id)
            if slot and not slot.is_available:
                slot.is_available = True
                db.session.commit()
                socketio.emit('slot_status_update', slot.to_dict())

            return jsonify({"msg": "Reservation completed successfully", "reservation": reservation.to_dict()}), 200
        else:
            return jsonify({"msg": "Unauthorized to complete this reservation"}), 403
    except Exception as e:
        return jsonify({"msg": "Something went wrong, Please try again."}), 500
