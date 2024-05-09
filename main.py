import logging
from aiogram.types import ParseMode
from background import keep_alive, add_id, logger
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '7040913152:AAHJ9LadCW8pZyjo9MdpzvUA2-u5F4B7aG8'
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


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
    number = contact.phone_number
    if '+' not in number:
        number = '+' + number
    response = add_id(number, contact.user_id)
    if response == 'added':
        await m.answer("Вы успешно зарегистрировались!", reply_markup=types.ReplyKeyboardRemove(),
                   parse_mode=ParseMode.MARKDOWN)
    elif response == 'already exists':
        await m.answer("Вы уже зарегистрированы.", reply_markup=types.ReplyKeyboardRemove(),
                       parse_mode=ParseMode.MARKDOWN)
    await m.answer("Если вы ещё не внесли свой номер в список для рассылки в мобильном приложении"
                   " на телефоне вашей бабки, обязательно сделайте это! Это необходимо для того, чтобы бот "
                   " присылал вам информацию об измерениях давления.")


@dp.message_handler()
async def debug(message: types.Message):
    logger.info(f'{message.date} {message.from_user.username}: {message.text}')


keep_alive()
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
