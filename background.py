from flask import Flask
from flask import request
from threading import Thread
import time
import json
import requests

app = Flask('')


@app.route('/', methods=['GET'])
def index():
    return 'Привет, мир! Это удалённый сервер.'


def send_to_server(number: int, id: int):
    url = 'https://tonometer.onrender.com/auth/add-telegram-id'

    headers = {'Content-Type': 'application/json'}

    data = {"number": str(number), "telegramId": str(id)}
    json_data = json.dumps(data)
    print(f'SENT JSON DATA: {json_data}')

    response = requests.get(url, headers=headers, data=json_data)

    if response.status_code == 200:
        print('Успешный запрос!')
        print(response.json())
    else:
        print('Ошибка при запросе:', response.status_code)


@app.route('/send_message', methods=['POST'])
def message_request():
    if request.headers['Content-Type'] == 'application/json':
        parsed_json = request.json
        print("tried to parse request")
        print(parsed_json)
        send_info(parsed_json)
        return 'success', 200
    else:
        return 'unsupported media type', 415


def send_info(pjs):
    from datetime import datetime
    chat_id = pjs['id']
    dia = pjs['info'][0]['dia']
    sys = pjs['info'][1]['sys']
    pulse = pjs['info'][2]['pulse']
    date_info = datetime.fromisoformat(pjs['info'][3]['date'])
    date = date_info.strftime("%d {month} %Y года в %H:%M").format(
        month=month_names[date_info.month])
    name = pjs['info'][4]['name']
    text = f'Получены данные об измерении, произведённом {date} от {name}:\nDIA: {dia}\nSYS: {sys}\nPULSE: {pulse}\nБудьте здоровы!'
    send_message(chat_id, text)


def send_message(chat_id, text):
    method = "sendMessage"
    token = "7040913152:AAF08LsRRx4y-jbCN9T8WnAtppFqwrgJCos"
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
