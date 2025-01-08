import requests

data = {
    "name": "SUVa",
    "standard": 15.50,
    "premium": 25.75
}

new_data = {
    "name": "aaa",
    "standard": 15.50,
    "premium": 25.75
}

def create_cartype(data):
    url = "http://127.0.0.1:5000/cartype"
    response = requests.post(url, json=data)
    return response.json()

def read_cartype():
    url = f"http://127.0.0.1:5000/cartype"
    response = requests.get(url)
    return response.json()

def update_cartype(cartype_name, data):
    url = f"http://127.0.0.1:5000/cartype/{cartype_name}"
    response = requests.put(url, json=data)
    return response.json()

def delete_cartype(cartype_name):
    url = f"http://127.0.0.1:5000/cartype/{cartype_name}"
    response = requests.delete(url)
    return response.json()

print(create_cartype(data))
print(update_cartype("SUVa", new_data))
print(read_cartype())
print(delete_cartype("aaa"))
print(read_cartype())
