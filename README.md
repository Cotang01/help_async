Python version 3.11.3
Перед тем как запускать скрипт, все положить в одну папку и нужно в терминале
перейти в директорию этой папки и от туда запускать
После в терминале прописать команду python main.py -c 'config.ini'

Действия для запуска бота в Dockerfile:
(В одной директории должны быть файлы: 
bot.py "ваш конфиг".env  Dockerfile  logger.log  
logger.py requirements.txt)
1. docker build -t <ваше название контейнера>
2. Команда запуска:
    docker run -d 
    -v $(pwd)/logger.log:/app/logger.log 
    -v $(pwd)/"ваш конфиг".env:/app/"ваш конфиг".env
    <ваше название контейнера>

Если logger.log не оказывается на хостовой машине, то контейнер создаёт его
в своей файловой системе, но хосту он не передаётся, чтобы передавался, надо
в конце монтирования файла добавить ":z"

Запуск бота с docker-compose:
(В одной директории должны быть файлы:
bot.py "ваш конфиг".env logger.py requirements.txt logger.log
Dockerfile docker-compose.yml)
1. docker-compose up -d

В случае docker-compose если на хосте не оказывается файла, 
то docker создаёт директорию

Если возникает ошибка "http: invalid Host header":
snap refresh --revision=2893 docker

Запуск приватного репозитория:

docker run -d -p 5000:5000 --restart=always --name registry registry:2

Пулл образа:
docker pull "repo"/"image"

Запуск образа со своим .env конфигом:
docker run -d --env-file ".env" "repo"/"image"
