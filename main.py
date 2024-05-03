import json
from datetime import datetime

from flask import Flask, request
import requests

app = Flask(__name__)

token = "7040913152:AAF08LsRRx4y-jbCN9T8WnAtppFqwrgJCos"


def set_webhook():
    url = f"https://api.telegram.org/bot{token}/setWebhook?https://tonoscan-bot.onrender.com/webhook/{token}"
    webhook_url = "https://tonoscan-bot.onrender.com/webhook"
    data = {"url": webhook_url}
    response = requests.post(url)
    if response.ok:
        print("Вебхук установлен успешно.")
    else:
        print("Ошибка при установке вебхука:", response.text)


@app.route('/webhook', methods=['POST'])
def webhook_handler():
    if request.headers['Content-Type'] == 'application/json':
        update = request.json
        if 'message' in update:
            message = update['message']
            date = datetime.fromtimestamp(message['date'] / 1000.0).isoformat()
            username = message['from']['username']
            text = message['text']
            print(f'{date} {username}: {text}')
            handle_message(message)
        return 'ok', 200
    else:
        return 'unsupported media type', 415


def handle_message(message):
    if 'text' in message:
        text = message['text']
        chat_id = message['chat']['id']

        if text.startswith('/start'):
            send_message_with_contact_button(chat_id)
        else:
            send_message(chat_id, "Извините, у меня слабые социальные навыки, поэтому в ответ на ваши сообщения я "
                                  "всегда буду присылать вам этот текст.")
    elif 'contact' in message:
        contact = message['contact']
        chat_id = message['chat']['id']
        handle_contact(chat_id, contact['phone_number'], contact['user_id'])


def send_message_with_contact_button(chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": "Здравствуйте! Нажмите на кнопку 'Поделиться контактом', чтобы зарегистрироваться в боте.",
        "reply_markup": {
            "keyboard": [
                [{"text": "Поделиться контактом", "request_contact": True}]
            ],
            "resize_keyboard": True
        }
    }
    response = requests.post(url, json=data)
    if response.ok:
        print("Сообщение с кнопкой контакта отправлено успешно.")
    else:
        print("Ошибка при отправке сообщения:", response.text)


def handle_contact(chat_id, phone_number, user_id):
    send_to_server(phone_number, user_id)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    text1 = "Вы успешно зарегистрировались!"
    text2 = ("Если вы ещё не внесли свой номер в список для рассылки в мобильном приложении на телефоне вашей бабки, "
             "обязательно сделайте это! Это необходимо для того, чтобы бот моментально присылал вам информацию об измерениях давления.")
    data1 = {
        "chat_id": chat_id,
        "text": text1,
        "reply_markup": {
            "remove_keyboard": True
        }
    }
    data2 = {"chat_id": chat_id, "text": text2}
    requests.post(url, json=data1)
    requests.post(url, json=data2)


def send_message(chat_id, text):
    method = "sendMessage"
    token = "7040913152:AAF08LsRRx4y-jbCN9T8WnAtppFqwrgJCos"
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


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
    date = date_info.strftime("%d {month} %Y года в %H:%M").format(month=month_names[date_info.month])
    name = pjs['info'][4]['name']
    text = f'Получены данные об измерении, произведённом {date} от {name}:\nDIA: {dia}\nSYS: {sys}\nPULSE: {pulse}\nБудьте здоровы!'
    send_message(chat_id, text)


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


def send_to_server(number: int, id: int):
    url = 'https://tonometer.onrender.com/auth/add-telegram-id'

    headers = {'Content-Type': 'application/json'}

    data = {
        "number": str(number),
        "telegramId": str(id)
    }
    json_data = json.dumps(data)
    print(f'SENT JSON DATA: {json_data}')

    response = requests.get(url, headers=headers, data=json_data)

    if response.status_code == 200:
        print('Успешный запрос!')
        print(response.json())
    else:
        print('Ошибка при запросе:', response.status_code)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
    set_webhook()
