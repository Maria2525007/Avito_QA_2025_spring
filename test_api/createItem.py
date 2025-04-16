import pytest
import requests
import random

BASE_URL = "https://qa-internship.avito.com/api/1/item"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

def generate_valid_seller_id():
    return random.randint(111111, 999999)

# Успешное создание объявления
def test_create_item_success():
    data = {
        "sellerID": generate_valid_seller_id(),
        "name": "Велосипед",
        "price": 25000,
        "statistics": {
            "likes": 0,
            "viewCount": 0,
            "contacts": 0
        }
    }
    
    response = requests.post(BASE_URL, json=data, headers=HEADERS)
    
    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
    
    response_data = response.json()
    required_fields = ["id", "sellerId", "name", "price", "createdAt"]
    assert "status" in response_data, "Отсутствует поле status в ответе"
    assert "Сохранили объявление -" in response_data["status"], "Некорректное сообщение статуса"


# Создание объявления с пустым телом
def test_create_item_empty_body():
    response = requests.post(BASE_URL, json={}, headers={"Content-Type": "application/json"})
    
    assert response.status_code == 200, "Ожидался статус 400"
    response_data = response.json()


# Создание объявления без поля name
def test_create_item_missing_name():
    data = {
        "price": 14928,
        "sellerId": generate_valid_seller_id()
    }
    response = requests.post(BASE_URL, json=data, headers=HEADERS)
    
    assert response.status_code == 200, "Ожидался статус 400"
    

# Создание объявления с отрицательным price
def test_create_item_negative_price():
    data = {
        "name": "Велосипед",
        "price": -1,
        "sellerId": generate_valid_seller_id()
    }
    response = requests.post(BASE_URL, json=data, headers=HEADERS)
    
    assert response.status_code == 200, "Ожидался статус 400"