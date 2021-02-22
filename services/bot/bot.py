import telebot
import yaml
from telebot import types

import tickets_from_mongo

with open('../config.yml', 'r') as f:
    config = yaml.safe_load(f)

token = config['bot_token']
bug_types = config['bug_types']

bot = telebot.TeleBot(token)

menu_keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
menu_keyboard.row('МЕНЮ БАГОВ')
menu_keyboard.row('ОБЩАЯ СТАТИСТИКА')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добавлено меню', reply_markup=menu_keyboard)


def make_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for bug_type in bug_types:
        keyboard.add(types.InlineKeyboardButton(text=f'Последний {bug_type}',
                                                callback_data=bug_type))
    return keyboard


@bot.callback_query_handler(lambda query: query.data in bug_types)
def process_callback(query):
#    bot.answer_callback_query(callback_query_id=query.id,
#                              text=tickets_from_mongo.get_bot_message(query.data),
#                              show_alert=True)
    bot.edit_message_text(chat_id=query.message.chat.id,
                          text=tickets_from_mongo.get_bot_message(query.data),
                          message_id=query.message.message_id)


@bot.message_handler(regexp='^[М][Е][Н][Ю][ ][Б][А][Г][О][В]$')
def bug_menu(message):
    bot.send_message(message.chat.id, 'Выбери', reply_markup=make_keyboard(),)


@bot.message_handler(regexp='^[О][Б][Щ][А][Я][ ][С][Т][А][Т][И][С][Т][И][К][А]$')
def statistic_message(message):
    bot.send_message(message.chat.id, tickets_from_mongo.get_statistic())


bot.polling()
