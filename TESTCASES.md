## Тестирование микросервиса, предоставляющего REST API для управления объявлениями

Использован стек: Python с фреймворком Pytest

Хост сервиса:
https://qa-internship.avito.com


## Структура тестов

1. **test_statistic_integrity_bug** — проверка статистики

2. **test_empty_body_should_fail**, **test_negative_price_should_fail**, **test_missing_required_fields_should_fail** — тесты валидации при создании

3. **test_invalid_uuid** — проверка UUID для статистики

4. **test_double_delete** — тест повторного удаления

5. **test_route_not_found_status_code** — проверка роутинга

6. **test_wrong_data_types** — валидация типов данных при создании

7. **test_too_long_name** — валидация длины имени

8. **test_created_at** — проверка временной метки

9. **test_basic_crud_flow** — комплексный тест

