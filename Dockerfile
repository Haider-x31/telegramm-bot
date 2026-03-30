FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install pyTelegramBotAPI requests

CMD ["python", "bot.py"]
