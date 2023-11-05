Python version 3.11.3
Перед тем как запускать скрипт, все положить в одну папку и нужно в терминале
перейти в директорию этой папки и от туда запускать
После в терминале прописать команду python main.py -c 'config.ini'

Действия для запуска бота в Dockerfile:
(В одной директории должны быть файлы: 
bot.py config.env  Dockerfile  logger.log  
logger.py requirements.txt)
1. docker build -t <ваше название контейнера>
2. Команда запуска для Linux:
    docker run -d 
    -v $(pwd)/logger.log:/app/logger.log 
    -v $(pwd)/config.env:/app/config.env
    <ваше название контейнера>
3. Команда запуска для Windows:
    docker run -d 
    -v ${PWD}/logger.log:/app/logger.log 
    -v ${PWD}/config.env:/app/config.env 
    <ваше название контейнера>

Если logger.log не оказывается на хостовой машине, то контейнер создаёт его
в своей файловой системе, но хосту он не передаётся, чтобы передавался, надо
в конце монтирования файла добавить ":z"

Запуск бота с docker-compose:
(В одной директории должны быть файлы, если хост Linux:
bot.py configLin.env logger.py requirements.txt logger.log
Dockerfile docker-compose.yml)
(Если хост Windows:
bot.py configWin.env logger.py requirements.txt logger.log
Dockerfile docker-compose.yml)
1. docker-compose up -d

В случае docker-compose если на хосте не оказывается файла, 
то docker создаёт директорию

Если возникает ошибка "http: invalid Host header":
snap refresh --revision=2893 docker
