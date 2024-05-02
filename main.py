import datetime

import requests
from flask import Flask, request
import telebot
from datetime import datetime
import json

app = Flask(__name__)

bot = telebot.TeleBot('7040913152:AAF08LsRRx4y-jbCN9T8WnAtppFqwrgJCos')

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


@app.route('/', methods=['GET'])
def index():
    return 'Привет, мир! Это удалённый сервер.'


def send_to_server(number: int, id: int):
    url = 'https://tonometer.onrender.com/auth/XXXXXXXXXXXXXXXXXXXXXX'

    headers = {'Content-Type': 'application/json'}

    data = {
        "number": str(number),
        "id": str(id)
    }
    json_data = json.dumps(data)
    print(f'SENT JSON DATA: {json_data}')

    response = requests.get(url, headers=headers, data=json_data)

    if response.status_code == 200:
        print('Успешный запрос!')
        print(response.json())
    else:
        print('Ошибка при запросе:', response.status_code)


@app.route('/send_message', methods=['POST'])
def webhook():
    got = request.stream.read().decode('utf-8')
    parsed_json = json.loads(got)
    send_message(parsed_json)
    return '', 200


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("Поделиться контактом", request_contact=True)
    markup.add(button)
    bot.send_message(message.chat.id,
                     'Здравствуйте! Нажмите на кнопку "Поделиться контактом", чтобы зарегистрироваться в боте.',
                     reply_markup=markup)


@bot.message_handler(content_types=['contact'])
def handle_contact(m):
    contact = m.contact
    send_to_server(contact.phone_number, contact.user_id)
    bot.send_message(m.chat.id, "Вы успешно зарегистрировались!", reply_markup=telebot.types.ReplyKeyboardRemove(),
                     parse_mode='Markdown')
    bot.send_message(m.chat.id, "Если вы ещё не внесли свой номер в список для рассылки в мобильном приложении"
                                "на телефоне вашей бабки, обязательно сделайте это! Это необходимо для того, чтобы бот "
                                "моментально присылал вам информацию об измерениях давления.")


def send_message(pjs):
    chat_id = pjs['id']
    dia = pjs['info'][0]['dia']
    sys = pjs['info'][1]['sys']
    pulse = pjs['info'][2]['pulse']
    date_info = datetime.fromisoformat(pjs['info'][3]['date'])
    date = date_info.strftime("%d %B %Y года в %H:%M").format(month=month_names[date_info.month])
    name = pjs['info'][4]['name']
    # image = pjs['image']
    # image_bytes = bytes(image)
    text = f'Получены данные об измерении, произведённом {date} от {name}:\nDIA: {dia}\nSYS: {sys}\nPULSE: {pulse}\nБудьте здоровы!'
    bot.send_message(chat_id, text)


@bot.message_handler()
def debug(message):
    print(f'{datetime.fromtimestamp(message.date)} {message.from_user.username}: {message.text} {message}')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
