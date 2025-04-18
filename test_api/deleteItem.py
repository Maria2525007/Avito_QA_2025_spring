import pytest
import requests
import random

BASE_URL = "https://qa-internship.avito.com/api/1/item"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def generate_valid_seller_id():
    return random.randint(100000, 999999)


def create_item():
    data = {
        "sellerId": generate_valid_seller_id(),
        "name": "Тестовое объявление для удаления",
        "price": 1000,
        "statistics": {
            "likes": 0,
            "viewCount": 0,
            "contacts": 0
        }
    }
    response = requests.post(BASE_URL, json=data, headers=HEADERS)
    assert response.status_code == 200
    return response.json()["status"].split(" - ")[1]  # извлекаем id из строки вида: "Сохранили объявление - f4v1c8h8"


# Успешное удаление существующего объекта
def test_delete_item_success():
    item_id = create_item()
    response = requests.delete(f"{BASE_URL}/{item_id}", headers=HEADERS)

    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
    response_data = response.json()
    assert "status" in response_data
    assert "удалили объявление" in response_data["status"].lower()


# Повторное удаление того же объекта (БАГ #4)
def test_delete_item_twice_returns_404():
    item_id = create_item()
    
    # Первое удаление
    requests.delete(f"{BASE_URL}/{item_id}", headers=HEADERS)
    
    # Повторное удаление
    response = requests.delete(f"{BASE_URL}/{item_id}", headers=HEADERS)

    assert response.status_code == 404, f"Ожидался 404 при повторном удалении, получен {response.status_code}"
    response_data = response.json()
    assert "message" in response_data.get("result", {}), "Отсутствует ключ 'message' в ответе"
    assert response_data.get("status") == "404", "Поле 'status' должно быть '404'"


# Удаление по несуществующему ID
def test_delete_nonexistent_item():
    fake_id = "zzzz9999"
    response = requests.delete(f"{BASE_URL}/{fake_id}", headers=HEADERS)

    assert response.status_code == 404, f"Ожидался статус 404, получен {response.status_code}"
    assert "result" in response.json()


# Удаление по некорректному ID (символы вместо UUID)
def test_delete_invalid_id_format():
    invalid_id = "not-a-valid-id"
    response = requests.delete(f"{BASE_URL}/{invalid_id}", headers=HEADERS)

    assert response.status_code == 400 or response.status_code == 404, (
        f"Ожидался статус 400 или 404 при некорректном ID, получен {response.status_code}"
    )


# БАГ #4
def test_delete_response_status_consistency():
    item_id = create_item()
    requests.delete(f"{BASE_URL}/{item_id}", headers=HEADERS)

    # Повторное удаление
    response = requests.delete(f"{BASE_URL}/{item_id}", headers=HEADERS)
    json_data = response.json()

    assert str(response.status_code) == json_data.get("status"), (
        f"Несоответствие статуса: HTTP {response.status_code} vs. тело {json_data.get('status')}"
    )
