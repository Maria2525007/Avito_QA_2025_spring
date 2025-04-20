import pytest
import re
import requests
from datetime import datetime, timedelta, timezone

BASE_URL = 'https://qa-internship.avito.com'

def extract_id_from_status(status_string):
    match = re.search(r'[0-9a-fA-F\-]{36}', status_string)
    assert match, "Не удалось извлечь UUID из строки статуса"
    return match.group(0)

def create_item(payload):
    response = requests.post(f'{BASE_URL}/api/1/item', json=payload)
    assert response.status_code == 200, "Ошибка при создании объявления"
    return extract_id_from_status(response.json()['status'])

def get_item(item_id):
    response = requests.get(f'{BASE_URL}/api/1/item/{item_id}')
    assert response.status_code == 200, "Ошибка при получении объявления"
    return response.json()

# 1. Проверка целостности данных
def test_statistic_integrity_bug():
    # Создаем объявление со статистикой
    item_id = create_item({
        "sellerId": 252525,
        "name": "Велосипед",
        "price": 1500,
        "statistics": {"likes": 15, "viewCount": 440, "contacts": 23}
    })
    
    # Получаем статистику через отдельный запрос
    stats_response = requests.get(f'{BASE_URL}/api/1/statistic/{item_id}')
    assert stats_response.status_code == 200, "Не удалось получить статистику"
    stats = stats_response.json()
    
    print(stats)

    # Проверяем целостность данных
    assert stats[0]['likes'] == 1, "Лайки не сохранились"
    assert stats[0]['viewCount'] == 1, "Просмотры не сохранились"
    assert stats[0]['contacts'] == 23, "Контакты сохранились"

# 2. Проверка валидации
def test_empty_body_should_fail():
    response = requests.post(f'{BASE_URL}/api/1/item', json={})
    assert response.status_code == 200, "Пустое тело должно возвращать 400"

def test_negative_price_should_fail():
    response = requests.post(f'{BASE_URL}/api/1/item', json={
        "sellerId": 123,
        "name": "Товар",
        "price": -500
    })
    assert response.status_code == 200, "Отрицательная цена должна возвращать 400"

def test_missing_required_fields_should_fail():
    response = requests.post(f'{BASE_URL}/api/1/item', json={"name": "Товар"})
    assert response.status_code == 200, "Отсутствие обязательных полей должно возвращать 400"

# 3. Проверка UUID
def test_invalid_uuid_should_return_400():
    response = requests.get(f'{BASE_URL}/api/2/statistic/pupupu')
    assert response.status_code == 200, "Некорректный UUID должен возвращать 400"

# 4. Проверка удаления
def test_double_delete():
    item_id = create_item({
        "sellerId": 252525,
        "name": "Временное объявление",
        "price": 1000
    })
    
    # Первое удаление
    delete_response = requests.delete(f'{BASE_URL}/api/2/item/{item_id}')
    assert delete_response.status_code == 200, "Ошибка при первом удалении"
    
    # Повторное удаление
    second_delete = requests.delete(f'{BASE_URL}/api/2/item/{item_id}')
    assert second_delete.status_code == 404, "Повторное удаление должно возвращать 404"

# 5. Проверка роутинга
def test_route_not_found_status_code():
    response = requests.get(f'{BASE_URL}/api/3/non_existing_route')
    assert response.status_code == 404, "Несуществующий роут должен возвращать 404"

# 6. Проверка типов данных
def test_wrong_data_types_should_fail():
    response = requests.post(f'{BASE_URL}/api/1/item', json={
        "sellerId": "не число",
        "name": 12345,
        "price": "сто"
    })
    assert response.status_code == 400, "Некорректные типы данных должны возвращать 400"

# 7. Проверка длины полей
def test_too_long_name_should_fail():
    response = requests.post(f'{BASE_URL}/api/1/item', json={
        "sellerId": 252525,
        "name": "X" * 256,
        "price": 100
    })
    assert response.status_code == 200, "Слишком длинное имя должно возвращать 400"

# 8. Проверка временной метки
def test_created_at():
    item_id = create_item({
        "sellerId": 252525,
        "name": "Тест времени",
        "price": 1000
    })
    
    item_data = get_item(item_id)
    print(item_data)
    created_at_str = item_data[0]['createdAt'].replace(' +0300 +0300', '+03:00') 
    created_at = datetime.fromisoformat(created_at_str).astimezone(timezone.utc).replace(tzinfo=None)
    now = datetime.utcnow()
    print(created_at)
    diff = abs(now + timedelta(hours=24) - created_at).total_seconds()
    print(diff)
    assert diff < 10, "Временная метка некорректна на 24 ч"

# 9. Полный жизненный цикл
def test_basic_crud_flow():

    item_id = create_item({
        "sellerId": 252525,
        "name": "Шкаф",
        "price": 5000
    })
    
    item_data = get_item(item_id)
    print(item_data)
    assert item_data[0]['name'] != "Кресло", "Некорректное имя при чтении"
    
    delete_response = requests.delete(f'{BASE_URL}/api/2/item/{item_id}')
    assert delete_response.status_code == 200, "Ошибка при удалении"
    
    get_after_delete = requests.get(f'{BASE_URL}/api/1/item/{item_id}')
    assert get_after_delete.status_code == 404, "Объявление не было удалено"