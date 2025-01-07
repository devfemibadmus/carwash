from flask import request, jsonify
from .helper import db, cartype_bp
from .admin import admin_only

# CarType Model
class CarType:
    def __init__(self, name, standard, premium):
        self.name = name
        self.standard = standard
        self.premium = premium

    def to_dict(self):
        return {
            "name": self.name,
            "standard": self.standard,
            "premium": self.premium
        }

# CRUD for CarType
@cartype_bp.route('/cartype', methods=['POST'])
@admin_only
def create_cartype():
    data = request.get_json()
    if db.collection('car_types').where('name', '==', data['name']).get():
        return jsonify({"error": "Name must be unique"}), 400
    car_type = CarType(data['name'], data['standard'], data['premium'])
    doc_ref = db.collection('car_types').add(car_type.to_dict())
    return jsonify(doc_ref[1].get().to_dict()), 201

@cartype_bp.route('/cartype', methods=['GET'])
def get_all_cartypes():
    cartypes = db.collection('car_types').stream()
    cartype_list = [cartype.to_dict() for cartype in cartypes]
    return jsonify(cartype_list), 200

@cartype_bp.route('/cartype/<cartype_name>', methods=['PUT'])
@admin_only
def update_cartype(cartype_name):
    data = request.get_json()
    doc_ref = db.collection('car_types').where('name', '==', cartype_name).get()
    if not doc_ref:
        return jsonify({"error": "CarType not found"}), 404
    doc_ref = doc_ref[0].reference
    doc_ref.update({
        "name": data['name'],
        "standard": data['standard'],
        "premium": data['premium']
    })
    return jsonify({"message": "CarType updated"}), 200

@cartype_bp.route('/cartype/<cartype_name>', methods=['DELETE'])
@admin_only
def delete_cartype(cartype_name):
    doc_ref = db.collection('car_types').where('name', '==', cartype_name).get()
    if not doc_ref:
        return jsonify({"error": "CarType not found"}), 404
    doc_ref[0].reference.delete()
    return jsonify({"message": "CarType deleted"}), 200
