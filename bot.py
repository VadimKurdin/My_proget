import config
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from logic import *
from random import randint
import sqlite3 
      
bot = telebot.TeleBot(config.API_TOKEN)

id_generes=''
user_state = {}

row=["Часто задаваемые вопросы","Другое"]

def marcup_1(bot, message):
        info = f"""
Выберите:              
"""    
        bot.send_message(message.chat.id, info, reply_markup=add_to_favorite(row[0]))

def marcup_2(bot, message):
        info = f"""
Выберите к кому вы хотите обратиться:              
"""    
        bot.send_message(message.chat.id, info, reply_markup=add_to_id(row[0]))

def add_to_favorite(id):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton(row[0], callback_data=f'favorite_{id}'))
        markup.add(InlineKeyboardButton(row[1], callback_data=f'favorite1_{id}'))
        return markup

def add_to_id(id):
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton('Программисты(сообщить об ошибке на сайте)', callback_data=f'id_{id}'))
        markup.add(InlineKeyboardButton('Отдел покупок(проблема с товаром)', callback_data=f'id1_{id}'))
        return markup

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    if user_id in manager.get_users():
        bot.reply_to(message, "Ты уже зарегестрирован!")
    else:
        manager.add_user(user_id, message.from_user.username)
    
    marcup_1(bot, message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global id_generes, question_id
    question_id=''
    user_id = call.message.chat.id
    if call.data.startswith("favorite1"):
        id_generes = call.data[call.data.find("_")+1:]
        marcup_2(bot, call.message)
        

    elif call.data.startswith("favorite"):
        id_generes = call.data[call.data.find("_")+1:]
        msg = bot.send_message(call.message.chat.id, """
        Выберите вопрос:
        /1 Как оформить заказ?
        /2 Как узнать статус заказа?
        /3 Как отменить заказ?
        /4 Что делать, если товар пришел поврежденным?
        /5 Как связаться с технической поддержкой?
        /6 Как узнать информацию о доставке?
        """)

        # Сохраняем ID сообщения со списком
        message_list_id = msg.message_id

        # Добавляем флаг, чтобы бот знал, что сейчас ждет вопрос
        waiting_for_question[call.message.chat.id] = message_list_id
    if call.data.startswith("id1"):
        question_id = 2
        # Store the current state for the user to track when to expect their response
        # You can use a dictionary to store user states if necessary
        user_state[user_id] = 'waiting_for_question'  
        bot.send_message(call.message.chat.id, "Введите ваш вопрос:")
        


    elif call.data.startswith("id"):
       
        question_id = 1
        # Store the current state for the user to track when to expect their response
        # You can use a dictionary to store user states if necessary
        user_state[user_id] = 'waiting_for_question'  
        bot.send_message(call.message.chat.id, "Введите ваш вопрос:")
       


@bot.message_handler(func=lambda message: isinstance(waiting_for_question.get(message.chat.id), int))
def handle_question(message):
    global response_map
    question_id = message.text
    message_list_id = waiting_for_question[message.chat.id]

    response_map = {
        "/1": 'Для оформления заказа, пожалуйста, выберите интересующий вас товар и нажмите кнопку "Добавить в корзину", затем перейдите в корзину и следуйте инструкциям для завершения покупки.',
        "/2": 'Вы можете узнать статус вашего заказа, войдя в свой аккаунт на нашем сайте и перейдя в раздел "Мои заказы". Там будет указан текущий статус вашего заказа.',
        "/3": 'Если вы хотите отменить заказ, пожалуйста, свяжитесь с нашей службой поддержки как можно скорее. Мы постараемся помочь вам с отменой заказа до его отправки.',
        "/4": 'При получении поврежденного товара, пожалуйста, сразу свяжитесь с нашей службой поддержки и предоставьте фотографии повреждений. Мы поможем вам с обменом или возвратом товара.',
        "/5": "Вы можете связаться с нашей технической поддержкой через телефон на нашем сайте или написать нам в чат-бота.",
        "/6": "Информацию о доставке вы можете найти на странице оформления заказа на нашем сайте. Там указаны доступные способы доставки и сроки."
    }

    if question_id in response_map:
        bot.send_message(message.chat.id, response_map[question_id])
        
        # Удаляем сообщение со списком вопросов
        bot.delete_message(message.chat.id, message_list_id)
        
        # Удаляем сообщение пользователя
        bot.delete_message(message.chat.id, message.message_id)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите номер вопроса из списка.")
    
    # Сбрасываем состояние ожидания
    del waiting_for_question[message.chat.id]

# Словарь для отслеживания состояния ожидания
waiting_for_question = {}

@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    global question_id
    user_id = message.chat.id
    # Check if the user is in the waiting state for a question
    if user_id in user_state and user_state[user_id] == 'waiting_for_question':
        input_str_1 = message.text.lower()  # Get the user's response
        if input_str_1=='':
            bot.send_message(message.chat.id, "Вы ничего не ввели")
        else:
            conn = sqlite3.connect("questiens.db")
            with conn:
                user_id = message.chat.id
                cur = conn.cursor()
                cur.execute('INSERT INTO selected VALUES (?, ?, ?)', (user_id, question_id, input_str_1))
            # Reset the user's state after capturing the input
            user_state[user_id] = None  # or delete the entry if you're using a dict
            bot.send_message(message.chat.id, "Ваш вопрос был отправлен. Ожидайте с вами свяжутся как можно скорее!")
    
        
    






     

bot.infinity_polling()