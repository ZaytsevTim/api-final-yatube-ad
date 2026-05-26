# API для Yatube

## Описание
API для социальной сети Yatube. Позволяет создавать посты, комментарии, подписываться на авторов.

## Установка
1. Клонируйте репозиторий
2. Создайте виртуальное окружение: `python -m venv venv`
3. Активируйте его: `source venv/bin/activate`
4. Установите зависимости: `pip install -r requirements.txt`
5. Выполните миграции: `python manage.py migrate`
6. Запустите сервер: `python manage.py runserver`

## Примеры запросов

### Получение токена