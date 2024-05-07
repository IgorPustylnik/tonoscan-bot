import base64
import logging
import os
import struct

import requests
from flask import Flask
from flask import request
from threading import Thread
from datetime import datetime, timedelta
import json

app = Flask('')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@app.route('/', methods=['GET'])
def index():
    return 'Привет, мир! Это удалённый сервер.'


async def send_to_server(number, telegram_id):
    if '+' not in number:
        number = '+' + number
    url = 'https://tonometer.onrender.com/tonometer-api/add-telegram-id'

    headers = {'Content-Type': 'application/json'}

    data = {'number': number, 'telegramId': telegram_id}
    logger.info(f'SENT JSON DATA: {data}')

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        logger.info('Успешный запрос!')
    else:
        logger.info(f'Ошибка при запросе:{response.status_code}')


@app.route('/send_message', methods=['POST'])
def message_request():
    logger.info(request.json)
    parsed_json = request.json
    send_info(parsed_json)
    return 'success', 200


def send_info(pjs):
    chat_id = pjs['id']
    date_iso = datetime.strptime(pjs['date'], "%b %d, %Y, %I:%M:%S %p").isoformat()
    date_info = datetime.fromisoformat(date_iso) + timedelta(hours=3)
    date = date_info.strftime("%d {month} %Y года в %H:%M мск").format(
        month=month_names[date_info.month])
    name = pjs['name']
    if 'photo' in pjs:
        photo = pjs['photo']
        text = (f'Получено фото, сделанное {date} от {name} (не удалось распознать данные).'
                f'\nБудьте здоровы!')
        send_photo(chat_id, text, photo)
    else:
        dia = pjs['dia']
        sys = pjs['sys']
        pulse = pjs['pulse']
        text = (f'Получены данные об измерении, произведённом {date} от {name}:\nDIA: {dia}\nSYS: {sys}\nPULSE: {pulse}'
                f'\nБудьте здоровы!')
        send_message(chat_id, text)


def send_message(chat_id, text):
    method = "sendMessage"
    token = "7040913152:AAHJ9LadCW8pZyjo9MdpzvUA2-u5F4B7aG8"
    url = f"https://api.telegram.org/bot{token}/{method}"

    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


def send_photo(chat_id, text, bytes_photo):
    token = "7040913152:AAHJ9LadCW8pZyjo9MdpzvUA2-u5F4B7aG8"
    data = {"chat_id": chat_id, "caption": text}
    url = f"https://api.telegram.org/bot{token}/sendPhoto?chat_id={chat_id}"
    byte_array = json.loads(str(bytes_photo))
    adjusted_byte_array = [byte & 0xFF for byte in byte_array]
    binary_data = bytes(adjusted_byte_array)
    unpacked_values = struct.unpack('b' * len(binary_data), binary_data)
    packed_bytes = struct.pack('b' * len(unpacked_values), *unpacked_values)
    base64_string = base64.b64encode(packed_bytes).decode('utf-8')
    image_binary = base64.b64decode(base64_string)

    with open('saved_image.png', 'wb') as write_temp:
        write_temp.write(image_binary)
        write_temp.close()
    with open('saved_image.png', 'rb') as read_temp:
        response = requests.post(url, data=data, files={"photo": read_temp})
        logger.info(f'Фото отправлено боту, ответ: {response}')
        read_temp.close()
    os.remove('saved_image.png')


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
