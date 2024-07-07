import sqlite3
import os
import telebot
from telebot import types
import threading

bot = telebot.TeleBot('7209234950:AAGaPCk7wINlqRVo-yR43U9J-ZgrwbHpcLw')
user_data = {}
name = ''
vidil = ''
dirakcia = ''
department = ''
education = ''
experience = ''
downloaded_file = None
# Це в нас функція для обробки команди "start", для того щоб бот запустився
@bot.message_handler(commands=['start'])
def main(message):
    conn = sqlite3.connect('databaseTrainee.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS trainee (id int auto_increment primary key, name varchar(50),'
                'downloaded_file BLOB, vidil TEXT,dirakcia TEXT, department TEXT, education TEXT, experience TEXT)')
    conn.commit()
    cur.close()
    conn.close()

    welcome_video = open('images/welcome_video.mp4', 'rb')
    welcome_caption = (f'Привіт, {message.from_user.first_name} {message.from_user.last_name}! Вітаємо в команді АГРОМАТ!\n\n'
                       'Я Качка - символ компанії. І я тут, щоб допомогти знайти відповіді на всі ті питання, які виникають у перші тижні та місяці роботи. \n\n'
                       'Моя мета: пришвидшити твою адаптацію та зробити її комфортною. Тож не соромся - запитуй')
    bot.send_video(message.chat.id, welcome_video, caption=welcome_caption)
    bot.send_message(message.chat.id, 'Просимо тебе більш детально заповнити данні для того, щоб ми могли надати тобі повну інформацію:\n\n'
                                      'Введи своє повне ім\'я (ПІБ):')
    name = message.text.strip()
    bot.register_next_step_handler(message, get_full_name)

# Тут ми отримуємо повне ім'я стажера (ПІБ). За пробілом можна розбити на частини, для бази даних
def get_full_name(message):
    global name
    name = message.text.strip()
    save_data(message.chat.id, 'full_name', message.text)
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, message.message_id - 1)
    send_dep_top_keyboard(message)

def send_dep_top_keyboard(message):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Адміністративний відділ", callback_data="top1")
    button2 = types.InlineKeyboardButton(text="ДУОН", callback_data="top2")
    button3 = types.InlineKeyboardButton(text="Персонал", callback_data="top3")
    keyboard.add(button1, button2, button3)
    bot.send_message(message.chat.id, 'Обери свій відділ:', reply_markup=keyboard)

# В цій функції ми надсилаємо користувачу опції для вибору свого відділу
@bot.callback_query_handler(func=lambda call: call.data.startswith('top'))
def callback_dep_top(call):
    global vidil
    dep_top = call.data
    vidil = dep_top
    user_data[call.message.chat.id] = {'Відділ': dep_top}

    if dep_top == 'top1':
        options = ['Логістика', 'Маркетинг', 'Розвиток бізнеса', 'Закупівлі', 'Комерція', 'Фінанси', 'Юридичний']
    elif dep_top == 'top2' or dep_top == 'top3':
        options = []

    if options:
        keyboard = types.InlineKeyboardMarkup()
        for i, option in enumerate(options):
            button = types.InlineKeyboardButton(text=option, callback_data=f'mid_{i}')
            keyboard.add(button)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Обери свою дирекцію:", reply_markup=keyboard)
    else:
        confirm_selection(call)

# Тут користувач обирає свою дирекцію, якщо така існує, інакше пропускається до наступного кроку
@bot.callback_query_handler(func=lambda call: call.data.startswith('mid_'))
def callback_dep_middle(call):
    global dirakcia
    index = int(call.data.split('_')[1])
    options = ['Логістика', 'Маркетинг', 'Розвиток бізнеса', 'Закупівлі', 'Комерція', 'Фінанси', 'Юридичний']
    dep_middle = options[index]
    dirakcia = dep_middle
    user_data[call.message.chat.id]['Дирекція'] = dep_middle

    if dep_middle == 'Логістика':
        options = ['Експлуатація транспорту', 'ЗЕД', 'Складська логістика', 'Транспортна логістика', 'Управління товарними запасами']
    elif dep_middle == 'Закупівлі':
        options = ['Мерчандайзинг', 'Підлогові покриття', 'Плитка Економ', 'Плитка Середній та Еліт', 'Сантехніка']
    elif dep_middle == 'Комерція':
        options = ['Власні торгові марки', 'Роздрібні продажі', 'Комплектація об\'єктів', 'Оптові продажі', 'Сервіс (рекламації)', 'Супутні напрямки']
    else:
        options = []

    if options:
        keyboard = types.InlineKeyboardMarkup()
        for i, option in enumerate(options):
            button = types.InlineKeyboardButton(text=option, callback_data=f'low_{i}')
            keyboard.add(button)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Обери свій департамент:", reply_markup=keyboard)
    else:
        confirm_selection(call)

# Тут користувач обирає свій департамент, якщо такий існує, інакше пропускається до наступного кроку
@bot.callback_query_handler(func=lambda call: call.data.startswith('low_'))
def callback_dep_lower(call):
    global department
    index = int(call.data.split('_')[1])
    dep_middle = user_data[call.message.chat.id]['Дирекція']

    if dep_middle == 'Логістика':
        options = ['Експлуатація транспорту', 'ЗЕД', 'Складська логістика', 'Транспортна логістика', 'Управління товарними запасами']
    elif dep_middle == 'Закупівлі':
        options = ['Мерчандайзинг', 'Підлогові покриття', 'Плитка Економ', 'Плитка Середній та Еліт', 'Сантехніка']
    elif dep_middle == 'Комерція':
        options = ['Власні торгові марки', 'Роздрібні продажі', 'Комплектація об\'єктів', 'Оптові продажі', 'Сервіс (рекламації)', 'Супутні напрямки']

    dep_lower = options[index]
    user_data[call.message.chat.id]['Департамент'] = dep_lower
    confirm_selection(call)
    department = dep_lower
# Тут ми просимо стажера перевірити чи правильно він обрав структуру і змінити в разі помилки
def confirm_selection(call):
    user_id = call.message.chat.id
    dep_top = user_data[user_id]['Відділ']
    dep_middle = user_data[user_id].get('Дирекція', 'Не обрано')
    dep_lower = user_data[user_id].get('Департамент', 'Не обрано')

    confirmation_text = (f"Ви обрали:\n"
                         f"Відділ: {dep_top}\n"
                         f"Дирекція: {dep_middle}\n"
                         f"Департамент: {dep_lower}\n\n"
                         "Підтвердіть або змініть свій вибір.")

    keyboard = types.InlineKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton(text="Підтвердити", callback_data="confirm")
    change_button = types.InlineKeyboardButton(text="Змінити", callback_data="change")
    keyboard.add(confirm_button, change_button)
    bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text=confirmation_text, reply_markup=keyboard)

# Ця функція описує дію кнопки Підтвердити
@bot.callback_query_handler(func=lambda call: call.data == 'confirm')
def callback_confirm(call):
    user_id = call.message.chat.id
    confirmation_message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Дякуємо! Ваш вибір підтверджено. Реєстрацію закінчено.")
    threading.Timer(5.0, delete_message, args=[call.message.chat.id, confirmation_message.message_id]).start()
    confirmation_message = bot.send_message(user_id, 'У нас є маленька традиція: представляти нових співробітників у внутрішніх каналах комунікацій. '
                                                     'І для того щоб зробити твою візитівку нам потрібно познайомитися трохи ближче. '
                                                     'Тому давайте почнемо.')
    threading.Timer(30.0, delete_message, args=[call.message.chat.id, confirmation_message.message_id]).start()

    # Початок процесу заповнення візитівки
    get_hobby(call.message)

# Ця функція описує дію кнопки змінити
@bot.callback_query_handler(func=lambda call: call.data == 'change')
def callback_change(call):
    confirmation_message = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Давайте почнемо спочатку.")
    threading.Timer(5.0, delete_message, args=[call.message.chat.id, confirmation_message.message_id]).start()
    send_dep_top_keyboard(call.message)

# Тут ми просто відсилаємо повідомлення і реяструємо наступний крок
def get_hobby(message):
    global education
    bot.send_message(message.chat.id, 'Яка в тебе освіта?')
    education = message.text.strip()
    bot.register_next_step_handler(message, get_degree)
# Тут ми отримуємо інформацію про освіту стажера (треба подумати в якій формі він заповнюватиме)
def get_degree(message):
    global experience
    save_data(message.chat.id, 'degree', message.text)
    bot.delete_message(message.chat.id, message.message_id)
    bot.edit_message_text('Розкажи декількома реченнями про свій попередній досвід роботи.', message.chat.id, message.message_id-1)
    experience = message.text.strip()
    bot.register_next_step_handler(message, get_experience)

# Тут ми отримуємо інформацію проо його попереднє працевлаштування та досвід роботи (тут буде простий текст)
def get_experience(message):
    save_data(message.chat.id, 'experience', message.text)
    bot.delete_message(message.chat.id, message.message_id)
    confirmation_message = bot.edit_message_text('Додай своє фото.', message.chat.id, message.message_id-2)
    threading.Timer(20.0, delete_message, args=[message.chat.id, confirmation_message.message_id]).start()
    bot.register_next_step_handler(message, get_photo)

# Тут ми отримуємо фото працівника, яке буде на його візитівці
def get_photo(message):
    global downloaded_file
    if message.photo:
        # Отримуємо ID повідомлення, яке містить фото
        message_id_with_photo = message.message_id
        # Отримуємо ідентифікатор найбільшого фото (найкращої якості)
        photo_id = message.photo[-1].file_id
        # Отримуємо інформацію про фото за його ідентифікатором
        file_info = bot.get_file(photo_id)
        # Завантажуємо фото
        downloaded_file = bot.download_file(file_info.file_path)
        # Зберігаємо фото на сервері або обробляємо його
        #if not os.path.exists('photos'):
        #    os.makedirs('photos')
        #with open(f'photos/{photo_id}.jpg', 'wb') as new_file:
        #    new_file.write(downloaded_file)
        confirmation_message = bot.send_message(message.chat.id,'Фото збережено.')
        threading.Timer(5.0, delete_message, args=[message.chat.id, confirmation_message.message_id]).start()

        confirmation_message = bot.send_message(message.chat.id, 'Дякуємо! Форму заповнено.')
        threading.Timer(5.0, delete_message, args=[message.chat.id, confirmation_message.message_id]).start()

        # Видаляємо повідомлення з фото після його обробки
        threading.Timer(5.0, delete_message, args=[message.chat.id, message_id_with_photo]).start()

        bot.send_message(message.chat.id, 'А зараз ми тобі розкажемо, хто ми є!')
        send_info_slides(message.chat.id)
    else:
        msg =bot.send_message(message.chat.id, 'Будь ласка, надішли фото.')
        threading.Timer(5.0, delete_message, args=[message.chat.id, msg.message_id]).start()
        bot.register_next_step_handler(message, get_photo)

# media = [
#     'images/welcome_slide_info.mp4', 'images/slide1_info.png', 'images/slide2_info.png',
#     'images/slide3_info.png', 'images/slide4_info.png', 'images/slide5_info.png',
#     'images/slide6_info.png', 'images/slide7_info.png', 'images/slide8_info.png',
#     'images/slide9_info.png', 'images/slide10_info.png', 'images/slide11_info.png',
#     'images/slide12_info.png', 'images/slide13_info.png', 'images/slide14_info.png',
#     'images/slide15_info.png', 'images/slide16_info.png',
# ]
#
# # Індекс поточного медіа
# info_slides_index = 0
# last_message_id = None
#
# # Функція для відправлення поточного зображення з кнопками "Попередній" і "Наступний"
# def send_info_slides(chat_id):
#     global info_slides_index, last_message_id
#     markup = types.InlineKeyboardMarkup(row_width=2)
#     prev_button = types.InlineKeyboardButton(text='Попередній', callback_data='prev')
#     next_button = types.InlineKeyboardButton(text='Наступний', callback_data='next')
#     markup.add(prev_button, next_button)
#
#     if media[info_slides_index].endswith('.mp4'):
#         with open(media[info_slides_index], 'rb') as video:
#             if last_message_id:
#                 media_input = types.InputMediaVideo(video.read())
#                 try:
#                     bot.edit_message_media(media=media_input, chat_id=chat_id, message_id=last_message_id, reply_markup=markup)
#                 except telebot.apihelper.ApiException as e:
#                     bot.send_message(chat_id, f"Error: {e}")
#             else:
#                 msg = bot.send_video(chat_id, video, reply_markup=markup)
#                 last_message_id = msg.message_id
#     else:
#         with open(media[info_slides_index], 'rb') as photo:
#             if last_message_id:
#                 media_input = types.InputMediaPhoto(photo.read())
#                 try:
#                     bot.edit_message_media(media=media_input, chat_id=chat_id, message_id=last_message_id, reply_markup=markup)
#                 except telebot.apihelper.ApiException as e:
#                     bot.send_message(chat_id, f"Error: {e}")
#             else:
#                 msg = bot.send_photo(chat_id, photo, reply_markup=markup)
#                 last_message_id = msg.message_id
#
# # Обробник натискання кнопок "Попередній" та "Наступний"
# @bot.callback_query_handler(func=lambda call: call.data in ['prev', 'next'])
# def callback_inline(call):
#     global info_slides_index
#     # Оновлення індексу слайдів
#     if call.data == 'prev':
#         info_slides_index = max(0, info_slides_index - 1)
#     elif call.data == 'next':
#         if info_slides_index < len(media) - 1:
#             info_slides_index += 1
#         else:
#             bot.delete_message(call.message.chat.id, call.message.message_id)
#             confirmation_message = bot.send_message(call.message.chat.id, "Це був останній слайд. Дякуємо за перегляд!")
#             threading.Timer(5.0, delete_message, args=[call.message.chat.id, confirmation_message.message_id]).start()
#
#             bot.send_message(call.message.chat.id, 'А тепер познайомимо тебе з керівниками Компанії!')
#             tour(call.message.chat.id)
#             return
#
#     # Відправлення поточного слайда з кнопками
#     send_info_slides(call.message.chat.id)
#
#
# # Функція для відправлення відео з кнопкою "Далі"
# def tour(chat_id):
#     markup = types.InlineKeyboardMarkup(row_width=1)
#     next_button = types.InlineKeyboardButton(text='Далі', callback_data='next_stage')
#     markup.add(next_button)
#
#     bot.send_video(chat_id, open('images/tour.mp4', 'rb'), reply_markup=markup, timeout=60)
#
# image = [
#     'images/slide1_structure.png', 'images/slide2_structure.png',
#     'images/slide3_structure.png', 'images/slide4_structure.png',
#     'images/slide5_structure.png'
# ]
#
# structure_slides_index = 0
# # Функція для відправлення поточного зображення з кнопками "Попередній" і "Наступний"
# def send_structure_slides(chat_id):
#     global structure_slides_index
#     markup = types.InlineKeyboardMarkup(row_width=2)
#     prev_button = types.InlineKeyboardButton(text='Попередній', callback_data='prev')
#     next_button = types.InlineKeyboardButton(text='Наступний', callback_data='next')
#     markup.add(prev_button, next_button)
#
#     if image[structure_slides_index].endswith('.mp4'):
#         with (open(image[structure_slides_index], 'rb') as video):
#             bot.send_video(chat_id, video, reply_markup=markup)
#     else:
#         bot.send_photo(chat_id, open(image[structure_slides_index], 'rb'), reply_markup=markup)
#
#
# # Обробник натискання кнопки "Далі" для переходу до слайдів
# @bot.callback_query_handler(func=lambda call: call.data == 'next_stage')
# def next_stage(call):
#     global structure_slides_index
#     structure_slides_index = 0  # Скидання індексу для слайдів
#     bot.delete_message(call.message.chat.id, call.message.message_id)
#     send_structure_slides(call.message.chat.id)
#
# # Обробник натискання кнопок "Попередній" та "Наступний"
# @bot.callback_query_handler(func=lambda call: call.data in ['prev', 'next'])
# def callback_inline(call):
#     global structure_slides_index
#     bot.delete_message(call.message.chat.id, call.message.message_id)
#
#     if call.data == 'prev':
#         structure_slides_index = max(0, structure_slides_index - 1)
#     elif call.data == 'next':
#         if structure_slides_index < len(image) - 2:  # Останнє зображення має індекс len(image) - 2
#             structure_slides_index += 1
#         else:
#             bot.send_message(call.message.chat.id, "Це був останній слайд. Дякуємо за перегляд!")
#             return
#
#     send_info_slides(call.message.chat.id)
#
# def delete_message(chat_id, message_id):
#     bot.delete_message(chat_id, message_id)
#
# def save_data(user_id, key, value):
#     if user_id not in user_data:
#         user_data[user_id] = {}
#     user_data[user_id][key] = value
#
# bot.polling(none_stop=True)

media = [
    'images/welcome_slide_info.mp4', 'images/slide1_info.png', 'images/slide2_info.png',
    'images/slide3_info.png', 'images/slide4_info.png', 'images/slide5_info.png',
    'images/slide6_info.png', 'images/slide7_info.png', 'images/slide8_info.png',
    'images/slide9_info.png', 'images/slide10_info.png', 'images/slide11_info.png',
    'images/slide12_info.png', 'images/slide13_info.png', 'images/slide14_info.png',
    'images/slide15_info.png', 'images/slide16_info.png',
]

# Індекс поточного медіа
info_slides_index = 0
last_message_id = None

# Функція для відправлення інформації про Агромат
def send_info_slides(chat_id):
    global info_slides_index, last_message_id
    markup = types.InlineKeyboardMarkup(row_width=2)
    prev_button = types.InlineKeyboardButton(text='Попередній', callback_data='prev')
    next_button = types.InlineKeyboardButton(text='Наступний', callback_data='next')
    markup.add(prev_button, next_button)

    try:
        if media[info_slides_index].endswith('.mp4'):
            with open(media[info_slides_index], 'rb') as video:
                video_data = video.read()
                media_input = types.InputMediaVideo(video_data)
                if last_message_id:
                    try:
                        bot.edit_message_media(media=media_input, chat_id=chat_id, message_id=last_message_id, reply_markup=markup)
                    except telebot.apihelper.ApiException:
                        msg = bot.send_video(chat_id, video_data, reply_markup=markup)
                        last_message_id = msg.message_id
                else:
                    msg = bot.send_video(chat_id, video_data, reply_markup=markup)
                    last_message_id = msg.message_id
        else:
            with open(media[info_slides_index], 'rb') as photo:
                photo_data = photo.read()
                media_input = types.InputMediaPhoto(photo_data)
                if last_message_id:
                    try:
                        bot.edit_message_media(media=media_input, chat_id=chat_id, message_id=last_message_id, reply_markup=markup)
                    except telebot.apihelper.ApiException:
                        msg = bot.send_photo(chat_id, photo_data, reply_markup=markup)
                        last_message_id = msg.message_id
                else:
                    msg = bot.send_photo(chat_id, photo_data, reply_markup=markup)
                    last_message_id = msg.message_id
    except FileNotFoundError:
        bot.send_message(chat_id, "Помилка: файл не знайдено.")

# Обробник натискання кнопок "Попередній" та "Наступний"
@bot.callback_query_handler(func=lambda call: call.data in ['prev', 'next'])
def callback_inline(call):
    global info_slides_index
    if call.message:
        chat_id = call.message.chat.id
        bot.delete_message(chat_id, call.message.message_id)
        if call.data == 'prev':
            info_slides_index = max(0, info_slides_index - 1)
        elif call.data == 'next':
            if info_slides_index < len(media) - 1:
                info_slides_index += 1
            else:
                bot.send_message(chat_id, "Це був останній слайд. Дякуємо за перегляд!")
                bot.send_message(chat_id, "Поринь у світ нашої компанії через це захоплююче відео.")
                tour(chat_id)
                return
        send_info_slides(chat_id)

# Функція для відправлення вітального відео з Аліною
def tour(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    next_button = types.InlineKeyboardButton(text='Далі', callback_data='next_stage')
    markup.add(next_button)
    bot.send_video(chat_id, open('images/tour.mp4', 'rb'), reply_markup=markup, timeout=60)

image = [
    'images/slide1_structure.png', 'images/slide2_structure.png',
    'images/slide3_structure.png', 'images/slide4_structure.png',
    'images/slide5_structure.png'
]

structure_slides_index = 0

# Функція для відправлення структури компанії
def send_structure_slides(chat_id):
    global structure_slides_index, last_message_id
    markup = types.InlineKeyboardMarkup(row_width=2)
    prev_button = types.InlineKeyboardButton(text='Попередній', callback_data='prev_structure')
    next_button = types.InlineKeyboardButton(text='Наступний', callback_data='next_structure')
    markup.add(prev_button, next_button)

    try:
        with open(image[structure_slides_index], 'rb') as photo:
            photo_data = photo.read()
            media_input = types.InputMediaPhoto(photo_data)
            if last_message_id:
                try:
                    bot.edit_message_media(media=media_input, chat_id=chat_id, message_id=last_message_id, reply_markup=markup)
                except telebot.apihelper.ApiException:
                    msg = bot.send_photo(chat_id, photo_data, reply_markup=markup)
                    last_message_id = msg.message_id
            else:
                msg = bot.send_photo(chat_id, photo_data, reply_markup=markup)
                last_message_id = msg.message_id
    except FileNotFoundError:
        bot.send_message(chat_id, "Помилка: файл не знайдено.")

# Обробник натискання кнопки "Далі" під відео
@bot.callback_query_handler(func=lambda call: call.data == 'next_stage')
def next_stage(call):
    global structure_slides_index
    structure_slides_index = 0  # Скидання індексу для слайдів
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, 'А тепер познайомимо тебе з керівниками Компанії')
    send_structure_slides(call.message.chat.id)

# Обробник натискання кнопок "Попередній" та "Наступний" для слайдів структури компанії
@bot.callback_query_handler(func=lambda call: call.data in ['prev_structure', 'next_structure'])
def callback_inline_structure(call):
    global structure_slides_index
    if call.message:
        chat_id = call.message.chat.id
        bot.delete_message(chat_id, call.message.message_id)
        if call.data == 'prev_structure':
            structure_slides_index = max(0, structure_slides_index - 1)
        elif call.data == 'next_structure':
            if structure_slides_index < len(image) - 1:
                structure_slides_index += 1
            else:
                bot.send_message(chat_id, "Це був останній слайд. Дякуємо за перегляд!")
                bot.send_message(chat_id, "Познайомся з нашими правилами.")
                send_rules_slides(chat_id)
                return
        send_structure_slides(chat_id)

rules_slides_index = 0
# Медиафайлы для слайдов правил
rules = [
    'images/slide1_rules.png', 'images/slide2_rules.png',
    'images/slide3_rules.png', 'images/slide4_rules.png', 'images/slide5_rules.png'
]

# Функция для отправки текущего изображений с правилами компании
def send_rules_slides(chat_id):
    global rules_slides_index, last_message_id
    markup = types.InlineKeyboardMarkup(row_width=2)
    prev_button = types.InlineKeyboardButton(text='Попередній', callback_data='prev_rules')
    next_button = types.InlineKeyboardButton(text='Наступний', callback_data='next_rules')
    markup.add(prev_button, next_button)

    try:
        with open(rules[rules_slides_index], 'rb') as photo:
            photo_data = photo.read()
            media_input = types.InputMediaPhoto(photo_data)
            if last_message_id:
                try:
                    bot.edit_message_media(media=media_input, chat_id=chat_id, message_id=last_message_id, reply_markup=markup)
                except telebot.apihelper.ApiException:
                    msg = bot.send_photo(chat_id, photo_data, reply_markup=markup)
                    last_message_id = msg.message_id
            else:
                msg = bot.send_photo(chat_id, photo_data, reply_markup=markup)
                last_message_id = msg.message_id
    except FileNotFoundError:
        bot.send_message(chat_id, "Помилка: файл не знайдено.")

# Обработчик нажатия кнопок "Попередній" и "Наступний" для слайдов правил
@bot.callback_query_handler(func=lambda call: call.data in ['prev_rules', 'next_rules'])
def callback_inline_rules(call):
    global rules_slides_index
    if call.message:
        chat_id = call.message.chat.id
        bot.delete_message(chat_id, call.message.message_id)
        if call.data == 'prev_rules':
            rules_slides_index = max(0, rules_slides_index - 1)
        elif call.data == 'next_rules':
            if rules_slides_index < len(rules) - 1:
                rules_slides_index += 1
            else:
                bot.send_message(chat_id, "Це був останній слайд. Дякуємо за перегляд!")
                return
        send_rules_slides(chat_id)
def save_data(user_id, key, value):
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id][key] = value
# Функція для видалення повідомлення
def delete_message(chat_id, message_id):
    bot.delete_message(chat_id, message_id)

    conn = sqlite3.connect('databaseTrainee.sql')
    cur = conn.cursor()

    cur.execute('INSERT INTO trainee (name,downloaded_file, vidil,dirakcia , department,'
                ' education , experience)VALUES ({%name},{%downloaded_file},{%vidil},{%dirakcia},{%department},{%education},{%experience})')
    conn.commit()
    cur.close()

bot.polling(none_stop=True)

# def save_data(user_id, key, value):
#     if user_id not in user_data:
#         user_data[user_id] = {}
#     user_data[user_id][key] = value
#
# @bot.message_handler(commands=['start'])
# def main(message):
#     welcome_photo = open('welcome_image.png', 'rb')
#     welcome_caption = (f'Вітаю, {message.from_user.first_name} {message.from_user.last_name}. \n\n'
#                        'Ласкаво просимо до компанії Агромат! Я ваш чат-бот асистент і готовий допомогти вам з усіма питаннями,'
#                        'які можуть виникнути під час вашої адаптації в нашій команді. \n\n'
#                        'Першим кроком, вам потрібно заповнити реєстраційну форму, тож \n\n')
#     bot.send_photo(message.chat.id, welcome_photo, caption=welcome_caption)
#
#     bot.send_message(message.chat.id, 'Введіть ваше повне ім\'я (ПІБ):')
#     bot.register_next_step_handler(message, get_full_name)
#
# def get_full_name(message):
#     save_data(message.chat.id, 'full_name', message.text)
#     bot.delete_message(message.chat.id, message.message_id)
#     bot.edit_message_text('Введіть вашу стать:', message.chat.id, message.message_id-1)
#     bot.register_next_step_handler(message, get_gender)
#
# def get_gender(message):
#     save_data(message.chat.id, 'gender', message.text)
#     bot.delete_message(message.chat.id, message.message_id)
#     bot.edit_message_text('Введіть ваш вік:', message.chat.id, message.message_id-2)
#     bot.register_next_step_handler(message, get_age)
#
# def get_age(message):
#     save_data(message.chat.id, 'age', message.text)
#     bot.delete_message(message.chat.id, message.message_id)
#     bot.edit_message_text('Введіть ваше місце народження:', message.chat.id, message.message_id-3)
#     bot.register_next_step_handler(message, get_birthplace)
#
# def get_birthplace(message):
#     save_data(message.chat.id, 'birthplace', message.text)
#     bot.delete_message(message.chat.id, message.message_id)
#     bot.edit_message_text('Введіть ваш паспортний номер:', message.chat.id, message.message_id-4)
#     bot.register_next_step_handler(message, get_passport_number)
#
# def get_passport_number(message):
#     save_data(message.chat.id, 'passport_number', message.text)
#     bot.delete_message(message.chat.id, message.message_id)
#     bot.edit_message_text('Введіть дату початку стажування:', message.chat.id, message.message_id-5)
#     calendar, step = DetailedTelegramCalendar().build()
#     bot.send_message(message.chat.id, f"Оберіть {translate_step(step)}", reply_markup=calendar)
#
# @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
# def calendar_callback(call):
#     result, key, step = DetailedTelegramCalendar().process(call.data)
#     if not result and key:
#         bot.edit_message_text(f"Оберіть {translate_step(step)}", call.message.chat.id, call.message.message_id, reply_markup=key)
#     elif result:
#         if 'start_date' not in user_data[call.message.chat.id]:
#             bot.edit_message_text(f"Дата початку стажування: {result}", call.message.chat.id, call.message.message_id)
#             bot.delete_message(call.message.chat.id, call.message.message_id-8)
#             save_data(call.message.chat.id, 'start_date', result)
#             bot.send_message(call.message.chat.id, 'Введіть дату закінчення випробовувального терміну:')
#             calendar, step = DetailedTelegramCalendar().build()
#             bot.send_message(call.message.chat.id, f"Оберіть {translate_step(step)}", reply_markup=calendar)
#         else:
#             bot.edit_message_text(f"Дата закінчення випробовувального терміну: {result}", call.message.chat.id, call.message.message_id)
#             save_data(call.message.chat.id, 'end_date', result)
#             bot.send_message(call.message.chat.id, 'Введіть вашу посаду:')
#             bot.register_next_step_handler(call.message, get_position)
# def translate_step(step):
#     if step == 'y':
#         return 'рік'
#     elif step == 'm':
#         return 'місяць'
#     elif step == 'd':
#         return 'день'
#     else:
#         return 'параметр'
#
# def get_position(message):
#     save_data(message.chat.id, 'position', message.text)
#     show_summary(message.chat.id)
#
# def show_summary(user_id):
#     summary = (
#         f"Ваші дані:\n\n"
#         f"ПІБ: {user_data[user_id]['full_name']}\n"
#         f"Стать: {user_data[user_id]['gender']}\n"
#         f"Вік: {user_data[user_id]['age']}\n"
#         f"Місце народження: {user_data[user_id]['birthplace']}\n"
#         f"Паспортний номер: {user_data[user_id]['passport_number']}\n"
#         f"Дата початку стажування: {user_data[user_id]['start_date']}\n"
#         f"Дата закінчення випробовувального терміну: {user_data[user_id]['end_date']}\n"
#         f"Посада: {user_data[user_id]['position']}\n"
#     )
#
#     markup = types.InlineKeyboardMarkup()
#     markup.add(types.InlineKeyboardButton("Змінити", callback_data="edit"))
#     markup.add(types.InlineKeyboardButton("Зберегти", callback_data="save"))
#
#     bot.send_message(user_id, summary, reply_markup=markup)
#
# @bot.callback_query_handler(func=lambda call: call.data in ["edit", "save"])
# def callback_query(call):
#     if call.data == "edit":
#         show_edit_menu(call.message)
#     elif call.data == "save":
#         bot.send_message(call.message.chat.id, "Дякую, форму відправлено!")
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#
# def show_edit_menu(message):
#     markup = types.InlineKeyboardMarkup()
#     markup.add(types.InlineKeyboardButton("ПІБ", callback_data="edit_full_name"))
#     markup.add(types.InlineKeyboardButton("Стать", callback_data="edit_gender"))
#     markup.add(types.InlineKeyboardButton("Вік", callback_data="edit_age"))
#     markup.add(types.InlineKeyboardButton("Місце народження", callback_data="edit_birthplace"))
#     markup.add(types.InlineKeyboardButton("Паспортний номер", callback_data="edit_passport_number"))
#     markup.add(types.InlineKeyboardButton("Дата початку стажування", callback_data="edit_start_date"))
#     markup.add(types.InlineKeyboardButton("Дата закінчення випробовувального терміну", callback_data="edit_end_date"))
#     markup.add(types.InlineKeyboardButton("Посада", callback_data="edit_position"))
#     markup.add(types.InlineKeyboardButton("Скасувати", callback_data="cancel"))
#     markup.add(types.InlineKeyboardButton("Зберегти", callback_data="save"))
#
#     bot.edit_message_text("Виберіть поле для редагування:", message.chat.id, message.message_id, reply_markup=markup)
#
# @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
# def edit_field(call):
#     field = call.data.split("_")[1] + "_" + call.data.split("_")[2] if len(call.data.split("_")) > 2 else call.data.split("_")[1]
#     prompt = {
#         "full_name": "Введіть ваше повне ім'я (ПІБ):",
#         "gender": "Введіть вашу стать:",
#         "age": "Введіть ваш вік:",
#         "birthplace": "Введіть ваше місце народження:",
#         "passport_number": "Введіть ваш паспортний номер:",
#         "start_date": "Введіть дату початку стажування (в форматі YYYY-MM-DD):",
#         "end_date": "Введіть дату закінчення випробовувального терміну (в форматі YYYY-MM-DD):",
#         "position": "Введіть вашу посаду:"
#     }
#
#     bot.send_message(call.message.chat.id, prompt[field])
#     bot.register_next_step_handler(call.message, lambda msg, field=field: update_field(msg, field))
#     bot.delete_message(call.message.chat.id, call.message.message_id)
#     bot.delete_message(call.message.chat.id, call.message.message_id-1)
#
# def update_field(message, field):
#     save_data(message.chat.id, field, message.text)
#     bot.delete_message(message.chat.id, message.message_id)
#     show_summary(message.chat.id)
#
# @bot.callback_query_handler(func=lambda call: call.data == "cancel")
# def cancel_edit(call):
#     show_summary(call.message.chat.id)