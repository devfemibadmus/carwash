import requests

data = {
    "address": "10 Downing Street London SW1A 2AA United Kingdom",
    "car_type_name": "Mini van",
    "wash_type": "standard",
    "status": "pending",
    "quantity": 2,
    "payment_id": "payment_789",
    "redirect_url": "http://localhost"
}

def create_order(data):
    url = "http://127.0.0.1:5000/order"
    response = requests.post(url, json=data)
    return response.json()

def read_order(order_id):
    url = f"http://127.0.0.1:5000/order/{order_id}"
    response = requests.get(url)
    return response.json()

def cancel_order(order_id):
    url = f"http://127.0.0.1:5000/order/{order_id}"
    response = requests.delete(url)
    return response.text

new_order = create_order(data)
print(new_order)
print(read_order(new_order['id']))
print(cancel_order(new_order['id']))
print(read_order(new_order['id']))

