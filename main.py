import telebot
from telebot import types
import requests

TOKEN = '6554318715:AAGiNkkQCn2Gf_O_zwQvNDd7st13lvkEyzo'

cash = 0

bot = telebot.TeleBot(TOKEN)

keys = {
    'Доллар':'USD',
    'Евро':'EUR',
    'Фунт':'GBR',
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ':'Другое',
}

@bot.message_handler(commands=['help'])
def help(message: telebot.types.Message):
    text = 'После ввода суммы используйте клавиши для выбора необходимой валюты и курса перевода. При некорректной работе бота нажмите /start. Для того чтобы получить весь спиок доступных валют нажмите /values'
    bot.reply_to(message,text)

@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты для перевода:'
    for key in keys.keys():
        text ='\n'.join((text, key ))
    bot.reply_to(message, text)

@bot.message_handler(commands=['start'])
def func(message):
        bot.send_message(message.chat.id, "Чтобы начать работу введите сумму для перевода валюты")
        bot.register_next_step_handler(message, func2)

def func2(message):
        global cash

        try:
                cash=float(message.text.strip())
        except ValueError:
                bot.send_message(message.chat.id, "Неверный формат")
                return
        if cash>0:
                markup = types.InlineKeyboardMarkup(row_width=2)
                btn1 = types.InlineKeyboardButton("USD/EUR", callback_data="usd/eur")
                btn2 = types.InlineKeyboardButton("EUR/USD", callback_data="eur/usd")
                btn3 = types.InlineKeyboardButton("USD/GBR", callback_data="usd/gbr")
                btn4 = types.InlineKeyboardButton("Другое", callback_data="else")
                markup.add(btn1,btn2,btn3,btn4)
                bot.send_message(message.chat.id, 'Выберите пару валют', reply_markup=markup)
        else:
                bot.send_message(message.chat.id, 'Введите число больше 0')
                bot.register_next_step_handler(message, func2())

@bot.callback_query_handler(func = lambda call:True)
def callback_message(call):
        if call.data != 'else':
              val = call.data.upper().split('/')
              url = f'https://api.exchangerate.host/convert?from={val[0]}&to={val[1]}'
              response = requests.get(url)
              data = response.json()
              rate = data['info']['rate']
              res = cash * rate
              bot.send_message(call.message.chat.id, f'Итог {round(res, 2)} курс перевода {rate} для пары валют {val[0]}/{val[1]}')
              bot.register_next_step_handler(call.message,func2)
        else:
                bot.send_message(call.message.chat.id, f'Введите пару значений /')
                bot.register_next_step_handler(call.message, my_cur)

def my_cur(message):
        val = message.text.upper().split('/')
        url = f'https://api.exchangerate.host/convert?from={val[0]}&to={val[1]}'
        response = requests.get(url)
        data = response.json()
        rate = data['info']['rate']
        res = cash * rate
        bot.send_message(message.chat.id,f'Итог {round(res, 2)} курс перевода {rate} для пары валют {val[0]}/{val[1]}')
        bot.register_next_step_handler(message, func2())


bot.polling(none_stop=True)