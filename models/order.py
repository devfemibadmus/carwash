import stripe
from datetime import datetime
from .helper import db, stripe_api_key, validate_recaptcha, jsonify, route

stripe.api_key = stripe_api_key

def checkout(amount, order_name, quantity, redirect_url):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{'price_data': {'currency': 'usd', 'product_data': {'name': f'{order_name} Car Wash', }, 'unit_amount': int(amount * 100), }, 'quantity': quantity}],
        mode='payment',
        success_url=f'{redirect_url}?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{redirect_url}?session_id={{CHECKOUT_SESSION_ID}}',
    )
    return session.url, session.id

def refund_payment(session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        payment_intent_id = session.payment_intent
        refund = stripe.Refund.create(payment_intent=payment_intent_id)
        return refund
    except stripe.error.StripeError as e:
        return f"Refund failed: {e.user_message}"

def expire_checkout_session(session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.status not in ['complete', 'expired']:
            expired_session = stripe.checkout.Session.expire(session_id)
            return "Session expire successfull"
        else:
            return "Session cannot be expired as it is already completed or expired."
    except stripe.error.StripeError as e:
        return f"Expiration failed: {e.user_message}"


# Order Model
class Order:
    def __init__(self, address, car_type_name, wash_type, quantity, payment_url=None, payment_id=None, payment_status=None):
        self.address = address
        self.car_type_name = car_type_name
        self.wash_type = wash_type
        self.quantity = quantity
        self.payment_url = payment_url
        self.payment_id = payment_id
        self.order_date = datetime.utcnow()
        self.payment_status = payment_status or 'pending'

    def amount(self, car_type):
        if self.wash_type == 'standard':
            return car_type['standard']
        elif self.wash_type == 'premium':
            return car_type['premium']
        return 0

    def to_dict(self, car_type):
        return {
            "address": self.address,
            "car_type_name": self.car_type_name,
            "wash_type": self.wash_type,
            "quantity": self.quantity,
            "order_date": self.order_date,
            "amount": self.amount(car_type),
            "total_amount": self.amount(car_type)*self.quantity,
            "payment_status": self.payment_status,
            "payment_url": self.payment_url,
            "payment_id": self.payment_id
        }

@route('/order', methods=['POST'])
@validate_recaptcha(action_name='ORDER')
def create_order(request):
    data = request.get_json()
    if not all(key in data for key in ['address', 'car_type_name', 'wash_type', 'quantity', 'redirect_url']):
        return jsonify({"error": "Missing required fields"}), 400
    car_type_ref = db.collection('car_types').where('name', '==', data['car_type_name']).limit(1).get()
    if not car_type_ref:
        return jsonify({"error": "Invalid car_type_name"}), 400
    car_type = car_type_ref[0].to_dict()
    if data['wash_type'] not in ['standard', 'premium']:
        return jsonify({"error": "Invalid wash_type. It should be 'standard' or 'premium'"}), 400
    if not isinstance(data['quantity'], int) or data['quantity'] <= 0:
        return jsonify({"error": "Quantity must be a positive integer"}), 400
    order = Order(data['address'], data['car_type_name'], data['wash_type'], data['quantity'])
    order_data = order.to_dict(car_type)
    payment_url, payment_id = checkout(order_data["amount"], car_type['name'], data['quantity'], data['redirect_url'])
    order_data["payment_url"] = payment_url
    order_data["payment_id"] = payment_id
    doc_ref = db.collection('orders').add(order_data)
    return jsonify({"id": doc_ref[1].id, "amount": order_data["amount"], "quantity": order_data["quantity"], "total_amount": order_data["amount"]*order_data["quantity"], "payment_url": payment_url, "payment_id": payment_id, "address": order_data["address"]}), 201

@route('/order/<order_id>', methods=['GET'])
def get_order(order_id, request):
    order_ref = db.collection('orders').document(order_id)
    order_doc = order_ref.get()
    if not order_doc.exists:
        return jsonify({"error": "Order not found"}), 404
    order_data = order_doc.to_dict()
    car_type_ref = db.collection('car_types').document(order_data['car_type_name'])
    car_type_doc = car_type_ref.get()
    if car_type_doc.exists:
        order_data['car_type'] = car_type_doc.to_dict()
    return jsonify(order_data), 200

@route('/order/<order_id>', methods=['DELETE'])
def cancel_order(order_id, request):
    order_ref = db.collection('orders').document(order_id)
    order = order_ref.get()
    if order.exists:
        payment_id = order.to_dict().get('payment_id')
        if payment_id:
            session = stripe.checkout.Session.retrieve(payment_id)
            if session.payment_status != 'paid':
                expire_checkout_session(payment_id)
                order_ref.update({'payment_status': 'canceled'})
                return jsonify({"message": "Order canceled and payment status updated"}), 200
            return jsonify({"message": "Payment already made, cancellation not allowed"}), 400
    return jsonify({"error": "Order not found"}), 404

@route('/payment/webhook', methods=['POST'])
def handle_payment_webhook(request):
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({"error": "Invalid signature"}), 400
    session = event['data']['object']
    session_id = session.get('id')
    payment_status = session.get('payment_status')
    order_ref = db.collection('orders').where('payment_id', '==', session_id).limit(1).get()
    if order_ref:
        order_ref[0].reference.update({'payment_status': payment_status})
    return jsonify({"status": "completed"}), 200


@route('/payment/verify', methods=['GET'])
def verify_payment(request):
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({"status": "failure", "message": "No session ID provided"}), 400
    session = stripe.checkout.Session.retrieve(session_id)
    if session.payment_status == 'paid':
        return jsonify({"status": "success", "message": "Payment successful"}), 200
    else:
        return jsonify({"status": "failure", "message": "Payment failed"}), 400

