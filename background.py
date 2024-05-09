import base64
import logging
import os
import struct

import psycopg2
import requests
from flask import Flask
from flask import request
from threading import Thread
from datetime import datetime, timedelta
import json


def create_table():  # для первого запуска
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS number_id (number VARCHAR(255) PRIMARY KEY, telegramId VARCHAR(255))")
    conn.commit()
    conn.close()


def get_db_connection():
    conn = psycopg2.connect(host='dpg-cothsiocmk4c73aru4q0-a.frankfurt-postgres.render.com',
                            database='number_id',
                            user='admin',
                            password='6M5NIjTYzhkAMJ7HN1XQbzjjdvs15uV6')
    return conn


def add_id(number_str, id_str):
    if '+' not in number_str:
        number_str = '+' + number_str
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO number_id (number, telegramId) VALUES (%s, %s)", (number_str, id_str))
        conn.commit()
        logger.info(f'Successfully added {number_str}:{id_str} to the database')
        response = 'added'
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        logger.warning(f'Number {number_str} already exists in the database')
        response = 'already exists'
    finally:
        conn.close()
    return response


def get_id(number_str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT telegramId FROM number_id WHERE number=%s", (number_str,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None


app = Flask('')
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@app.route('/', methods=['GET'])
def index():
    return 'TonoScan Bot server'


@app.route('/send_message', methods=['POST'])
def message_request():
    logger.info(request.json)
    parsed_json = request.json
    return send_info(parsed_json)


def send_info(pjs):
    date_iso = datetime.strptime(pjs['date'], "%b %d, %Y, %I:%M:%S %p").isoformat()
    date_info = datetime.fromisoformat(date_iso) + timedelta(hours=3)
    date = date_info.strftime("%d {month} %Y года в %H:%M мск").format(
        month=month_names[date_info.month])
    name = pjs['name']
    if 'photo' in pjs:
        photo = pjs['photo']
        text = (f'Получено фото, сделанное {date} от {name} (не удалось распознать данные).'
                f'\nБудьте здоровы!')
        phones = pjs['phone']
        for phone in phones:
            if phone[0] == '8':
                phone = '+7' + phone[1:]
            elif phone[0] == '7':
                phone = '+' + phone
            chat_id = get_id(phone)
            if chat_id is None:
                logger.info(f'Пользователь с номером {phone} не зарегистрирован '
                            f'(сообщение не было отправлено)')
            send_photo(chat_id, text, photo)
    else:
        dia = pjs['dia']
        sys = pjs['sys']
        pulse = pjs['pulse']
        text = (f'Получены данные об измерении, произведённом {date} от {name}:\nDIA: {dia}\nSYS: {sys}\nPULSE: {pulse}'
                f'\nБудьте здоровы!')
        phones = pjs['phone']
        for phone in phones:
            if phone[0] == '8':
                phone = '+7' + phone[1:]
            elif phone[0] == '7':
                phone = '+' + phone
            chat_id = get_id(phone)
            if chat_id is None:
                logger.info(f'Пользователь с номером {phone} не зарегистрирован '
                            f'(сообщение не было отправлено)')
            send_message(chat_id, text)
    return 'success', 200


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

    # костыли для раскодировки
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
