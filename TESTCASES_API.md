## Тестирование микросервиса, предоставляющего REST API для управления объявлениями

Использован стек JavaScript с фреймворком Jest + Supertest

Хост сервиса:
https://qa-internship.avito.com


## Структура тестов

- createItem.test.js — создание объявления

- getItemById.test.js — получение по item_id

- getItemsBySeller.test.js — все объявления по seller_id

- getStats.test.js — статистика по item_id

- deleteItem.test.js — удаление объявления

## Установка и запуск

1. Установите зависимости:

```
npm install
```

2. Запустите тесты



