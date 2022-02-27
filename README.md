![django version](https://img.shields.io/badge/Django-2.2.6-green)
![python version](https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9-green)

**Учебный проект выполненный в рамках курса "Python-разработчик" от Яндекс.Практикум**
## Социальная сеть Yatube.
### Функционал
Создание аккаунта пользователя

Создание сообществ

Публикация постов на своей странице, а также выбор сообщества для публикации

Возможность добавить изображение к посту

Комментирование постов

Редатирование постов и комментариев авторами

Подписка на авторов


## Как запустить проект:
Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```
