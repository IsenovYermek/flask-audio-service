

# Установка зависимостей
$ pip install -r requirements.txt

# Создадим docker образ
$ docker build -t flask-audio-service .

# Запускаем сервер
$ docker-compose up

# Для создания нового пользователя необходимо отправить POST запрос на /users с телом запроса в формате JSON. Имя может быть любое у меня будет имя Ermek
$ curl -X POST -H "Content-Type: application/json" -d '{"name": "Ermek"}' http://localhost:5000/user

# Добавление аудиозаписи:
$ curl -X POST -H "Content-Type: multipart/form-data" -F "audio=@path/to/file.wav" -F "user_id=123" -F "token=SOME_TOKEN" http://localhost:5000/records
Где вместо path/to/file.wav нужно указать путь к реальному файлу на вашем компьютере.


# Доступ к аудиозаписи:
$curl -OJL http://localhost:5000/record?id=456&user=123

