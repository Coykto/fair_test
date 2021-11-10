Решил не усложнять и не занимался:
1. Логированием
2. Авторизацией
3. Очисткой пользовательского ввода и вообще валидацией входных и выходных данных
4. Запуском с nginx и прочими прелестями продакшен деплоя
5. CI/CD (gitlab-ci или ещё чем-то вроде того)


Небольшое усложнение - это вынесение работы с базой в отдельный класс.
Уже сейчас это позволяет писать тесты с `TestRepository`, для которых не нужна будет
база, а значит проходить они будут быстрее и их будут чаще запускать. 
Плюс, его легко замокать и тестировать бизнес-логику 
без завязки на базу там где это возможно.


### Запуск тестов:
1. активировать python virtualenv
2. установить зависимости (`pip install -r requirements.txt`)
3. поднять базу (можно просто `docker-compose up db`)
   1. создать в базе таблицу cars (id serial primary key, model varchar, year int)
   2. подождать пока она будет готова
4. выполнить:
```
python -m pytest
```

### Поднять локально 
Либо docker (вместе с базой) - `docker-compose up fair`

Либо активировать virtualenv, установить зависимости, поднять базу, 
создать там таблицу cars (id serial primary key, model varchar, year int) 
и потом: `python -m main`