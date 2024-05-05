import logging
from flask import Flask
from flask import request
from threading import Thread
import json
import requests

app = Flask('')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@app.route('/', methods=['GET'])
def index():
    return 'Привет, мир! Это удалённый сервер.'


async def send_to_server(number: int, id: int):
    url = 'https://tonometer.onrender.com/auth/add-telegram-id'

    headers = {'Content-Type': 'application/json'}

    data = {"number": number, "telegramId": id}
    json_data = json.dumps(data)
    logger.info(f'SENT JSON DATA: {json_data}')

    response = requests.post(url, headers=headers, data=json_data)

    if response.status_code == 200:
        logger.info('Успешный запрос!')
        logger.info(response.json())
    else:
        logger.info(f'Ошибка при запросе:{response.status_code}')


@app.route('/send_message', methods=['POST'])
def message_request():
    logger.info(request.json)
    if request.headers['Content-Type'] == 'application/json':
        parsed_json = request.json
        send_info(parsed_json)
        return 'success', 200
    else:
        return 'unsupported media type', 415


def send_info(pjs):
    from datetime import datetime
    chat_id = pjs['id']
    dia = pjs['dia']
    sys = pjs['sys']
    pulse = pjs['pulse']
    date_info = datetime.fromisoformat(pjs['date'])
    date = date_info.strftime("%d {month} %Y года в %H:%M").format(
        month=month_names[date_info.month])
    name = pjs['name']
    text = f'Получены данные об измерении, произведённом {date} от {name}:\nDIA: {dia}\nSYS: {sys}\nPULSE: {pulse}\nБудьте здоровы!'
    send_message(chat_id, text)


def send_message(chat_id, text):
    method = "sendMessage"
    token = "7040913152:AAHJ9LadCW8pZyjo9MdpzvUA2-u5F4B7aG8"
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


month_names = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря"
}


def run():
    app.run(host='0.0.0.0', port=80)


def keep_alive():
    t = Thread(target=run)
    t.start()
