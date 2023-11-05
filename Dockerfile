FROM python:3.11.3
WORKDIR /app
COPY requirements.txt bot.py logger.py ./
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "bot.py"]