# Yatube 
___
<h2>Описание</h2>

Yatube — это социальная сеть для публикации личных дневников. 
На сайте пользователи могут создавать и подписываться на посты, а также редактировать свои посты. В проекте используется пагинация постов и кеширование. Регистрация реализована с верификацией данных, сменой и восстановления пароля через email. 

___
<h2>Список задач для данного спринта</h2>

1. С помощью sorl-thumbnail выведены иллюстрации к постам:
    - в шаблон главной страницы,
    - в шаблон профайла автора,
    - в шаблон страницы группы,
    - на отдельную страницу поста.
    Написаны тесты, которые проверяют:
    - при выводе поста с картинкой изображение передаётся в словаре context
        - на главную страницу,
        - на страницу профайла,
        - на страницу группы,
        - на отдельную страницу поста;
    - при отправке поста с картинкой через форму PostForm создаётся запись в базе данных;

2. Создана система комментариев
    Написана система комментирования записей. На странице поста под текстом записи выводится форма для отправки комментария, а ниже — список комментариев. Комментировать могут только авторизованные пользователи. Работоспособность модуля протестирована.
3. Кеширование главной страницы
    Список постов на главной странице сайта хранится в кэше и обновляется раз в 20 секунд.
4. Тестирование кэша
    Написан тест для проверки кеширования главной страницы. Логика теста: при удалении записи из базы, она остаётся в response.content главной страницы до тех пор, пока кэш не будет очищен принудительно.
5. Созданы кастомные страницы для ошибок
6. Созданы подписки на авторов и лента их постов.
    - Модель Follow должна иметь такие поля:
        - user — ссылка на объект пользователя, который подписывается. Укажите имя связи: related_name='follower'
        - author — ссылка на объект пользователя, на которого подписываются, имя связи пусть будет related_name='following'
    - написана view-функция страницы, куда будут выведены посты авторов, на которых подписан текущий пользователь.
    - Ещё две view-функции нужны для подписки на интересного автора и для того, чтобы отписаться от надоевшего графомана:
    - и соотвествующие шаблоны.
7. Тестирование
    
    Напишите тесты, проверяющие работу нового сервиса:
        - Авторизованный пользователь может подписываться на других пользователей и удалять их из подписок.
        - Новая запись пользователя появляется в ленте тех, кто на него подписан и не появляется в ленте тех, кто не подписан.
___ 
<h2>Инструкция</h2>

1. Cкопировать проект 
```
    git.clone git@github.com:Arseny13/hw05_final.git
```
2. Установить виртуальное окр и запустить его 
```
python -m venv venv
source venv/Scripts/activate
python -m pip intall --upgrade pip
```
3. Написать в консоль(установка библеотек)
```
pip install -r requirements.txt
```
4. Перейти в папку yatube(```cd yatube```)
    Запустить программу
```
python manage.py runserver
```

<h2>Используемые технологии</h2>

- Django==2.2.28
- mixer==7.1.2
- Pillow==9.3.0
- pytest==6.2.4
- pytest-django==4.4.0
- pytest-pythonpath==0.7.3
- requests==2.26.0
- six==1.16.0
- sorl-thumbnail==12.7.0
- Faker==12.0.1
- python-dotenv==0.21.0
