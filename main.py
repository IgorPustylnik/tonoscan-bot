import json
import requests
from aiogram.types import ParseMode
from flask import Flask, request
from flask_restful import Api
import asyncio
from aiogram import Bot, Dispatcher, executor, types

app = Flask(__name__)
api = Api(app)
dp = Dispatcher(Bot(token="7040913152:AAF08LsRRx4y-jbCN9T8WnAtppFqwrgJCos"))

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
    url = 'https://tonometer.onrender.com/auth/add-telegram-id'

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
def message_request():
    if request.headers['Content-Type'] == 'application/json':
        parsed_json = request.json
        print("tried to parse request")
        print(parsed_json)
        send_message(parsed_json)
        return 'success', 200
    else:
        return 'unsupported media type', 415


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Поделиться контактом", request_contact=True)
    markup.add(button)
    await message.answer('Здравствуйте! Нажмите на кнопку "Поделиться контактом", чтобы зарегистрироваться в боте.',
                         reply_markup=markup)


@dp.message_handler(content_types=['contact'])
async def handle_contact(m: types.Message):
    contact = m.contact
    await m.answer("Вы успешно зарегистрировались!", reply_markup=types.ReplyKeyboardRemove(),
                   parse_mode=ParseMode.MARKDOWN)
    await m.answer("Если вы ещё не внесли свой номер в список для рассылки в мобильном приложении"
                   " на телефоне вашей бабки, обязательно сделайте это! Это необходимо для того, чтобы бот "
                   " моментально присылал вам информацию об измерениях давления.")
    await send_to_server(contact.phone_number, contact.user_id)


async def send_message(pjs):
    from datetime import datetime
    chat_id = pjs['id']
    dia = pjs['info'][0]['dia']
    sys = pjs['info'][1]['sys']
    pulse = pjs['info'][2]['pulse']
    date_info = datetime.fromisoformat(pjs['info'][3]['date'])
    date = date_info.strftime("%d %B %Y года в %H:%M").format(month=month_names[date_info.month])
    name = pjs['info'][4]['name']
    text = f'Получены данные об измерении, произведённом {date} от {name}:\nDIA: {dia}\nSYS: {sys}\nPULSE: {pulse}\nБудьте здоровы!'

    await dp.bot.send_message(chat_id=chat_id, text=text)


@dp.message_handler()
async def debug(message: types.Message):
    print(f'{message.date} {message.from_user.username}: {message.text}')


async def is_enabled():
  while True:
    await app.run()

async def on_startup(x):
    asyncio.create_task(asyncio.to_thread(app.run(host='0.0.0.0', port=5000, debug=True)))

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
