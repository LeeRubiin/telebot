import telebot
from telebot import types
import csv
import os
import requests

bot = telebot.TeleBot('7095289212:AAF-4TR25WYJSQlaSPgkpcBPwPimDylrQBs', parse_mode="html")

user_language = {}
user_data = {}

@bot.message_handler(commands=['start'])
def startBot(message):
    chat_id = message.from_user.id
    send_data_to_server(chat_id, 'start', message.date)
    if chat_id in user_data:
        user_lang = user_language.get(chat_id, 'kaz')
        if user_lang == 'kaz':
            bot.send_message(chat_id, f"<b>{message.from_user.first_name}</b>, Сіз қайтадан оралдыңыз!")
        elif user_lang == 'rus':
            bot.send_message(chat_id, f"<b>{message.from_user.first_name}</b>, Вы снова здесь!")
        start_to_study(message)
    else:
        first_mess = f"<b>{message.from_user.first_name}</b>, Сізді онлайн қазақ тілін үйренуге арналған бот қарсы алады! Жұмыс жасауға ыңғайлы тілді таңдаңыз: \n \n<b>{message.from_user.first_name}</b>, Вас приветствует бот для изучения казахского языка онлайн! Выберите язык, с которым вам удобно работать:"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_kaz = types.KeyboardButton('Қазақ тілі/Казахский язык')
        button_rus = types.KeyboardButton('Орыс тілі/Русский язык')
        markup.add(button_kaz, button_rus)
        bot.send_message(message.chat.id, first_mess, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ['Қазақ тілі/Казахский язык', 'Орыс тілі/Русский язык'])
def select_language(message):
    chat_id = message.from_user.id
    send_data_to_server(chat_id, 'select_language', message.date)
    if message.text == 'Қазақ тілі/Казахский язык':
        user_language[chat_id] = 'kaz'
        response_second(message)
    elif message.text == 'Орыс тілі/Русский язык':
        user_language[chat_id] = 'rus'
        response_second(message)

class User:
    def __init__(self, surname=None, name=None, patronymic=None, iin=None, city=None, nationality=None, age=None):
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.iin = iin
        self.city = city
        self.nationality = nationality
        self.age = age

def save_user_data():
    with open('flask/userdata.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['user_id', 'surname', 'name', 'patronymic', 'iin', 'city', 'nationality', 'age'])
        for user_id, user in user_data.items():
            writer.writerow([user_id, user.surname, user.name, user.patronymic, user.iin, user.city, user.nationality, user.age])

def load_user_data():
    if os.path.exists('flask/userdata.csv'):
        with open('flask/userdata.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = int(row['user_id'])
                user_data[user_id] = User(
                    surname=row['surname'],
                    name=row['name'],
                    patronymic=row['patronymic'],
                    iin=row['iin'],
                    city=row['city'],
                    nationality=row['nationality'],
                    age=row['age']
                )

my_courses = {}

class Courses:
    def __init__(self, cours=None):
        if cours is None:
            cours = []
        self.cours = cours

def save_cours_data():
    with open('coursdata.db', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['user_id', 'cours'])
        for user_id, mycourse in my_courses.items():
            writer.writerow([user_id, ','.join(mycourse.cours)])


def load_cours_data():
    if os.path.exists('coursdata.db'):
        with open('coursdata.db', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = int(row['user_id'])
                cours = row['cours'].split(',') if row['cours'] else []
                my_courses[user_id] = Courses(cours=cours)


def response_second(message):
    chat_id = message.from_user.id
    user_data[chat_id] = User()
    user_lang = user_language.get(chat_id)
    if user_lang == 'kaz':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Тіркелу")
        markup.add(btn1)
        bot.send_message(chat_id, "Сіз таңдаған тіл сақталды. Оқуды бастамас бұрын тіркеуден өтуді өтінеміз.", reply_markup=markup)
    elif user_lang == 'rus':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Зарегистрироваться")
        markup.add(btn1)
        bot.send_message(chat_id, "Выбранный вами язык сохранен. Прежде чем начать обучение, пожалуйста, пройдите регистрацию.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Тіркелу", "Зарегистрироваться"])
def handle_registration(message):
    markup = types.ReplyKeyboardRemove()
    chat_id = message.from_user.id
    user_lang = user_language.get(chat_id)
    if user_lang == "kaz":
        bot.send_message(chat_id, "Тегіңізді енгізіңіз:", reply_markup=markup)
    elif user_lang == "rus":
        bot.send_message(chat_id, "Введите вашу фамилию:", reply_markup=markup)
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    chat_id = message.from_user.id
    user_data[chat_id].surname = message.text
    user_lang = user_language.get(chat_id, 'kaz')
    if user_lang == "kaz":
        bot.send_message(chat_id, "Атыңызды енгізіңіз:")
    elif user_lang == "rus":
        bot.send_message(chat_id, "Введите ваше имя:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    chat_id = message.from_user.id
    user_data[chat_id].name = message.text
    user_lang = user_language.get(chat_id, 'kaz')
    if user_lang == "kaz":
        bot.send_message(chat_id, "Әкеңіздің атын енгізіңіз:")
    elif user_lang == "rus":
        bot.send_message(chat_id, "Введите ваше отчество:")
    bot.register_next_step_handler(message, get_patronymic)

def get_patronymic(message):
    chat_id = message.from_user.id
    user_data[chat_id].patronymic = message.text
    user_lang = user_language.get(chat_id, 'kaz')
    if user_lang == "kaz":
        bot.send_message(chat_id, "ЖСН енгізіңіз:")
    elif user_lang == "rus":
        bot.send_message(chat_id, "Введите ваш ИИН:")
    bot.register_next_step_handler(message, get_iin)

def get_iin(message):
    chat_id = message.from_user.id
    iin = message.text
    if not iin.isdigit() or len(iin) != 12:
        user_lang = user_language.get(chat_id, 'kaz')
        if user_lang == "kaz":
            bot.send_message(chat_id, "ЖСН 12 цифр болуы керек")
        elif user_lang == "rus":
            bot.send_message(chat_id, "ИИН должен состоять из 12 цифр")
        bot.register_next_step_handler(message, get_iin)
        return
    user_data[chat_id].iin = iin
    user_lang = user_language.get(chat_id, 'kaz')
    if user_lang == "kaz":
        bot.send_message(chat_id, "Қалаңызды енгізіңіз:")
    elif user_lang == "rus":
        bot.send_message(chat_id, "Введите ваш город:")
    bot.register_next_step_handler(message, get_city)

def get_city(message):
    chat_id = message.from_user.id
    user_data[chat_id].city = message.text
    user_lang = user_language.get(chat_id, 'kaz')
    if user_lang == "kaz":
        bot.send_message(chat_id, "Ұлтыңызды енгізіңіз:")
    elif user_lang == "rus":
        bot.send_message(chat_id, "Введите вашу национальность:")
    bot.register_next_step_handler(message, get_nationality)

def get_nationality(message):
    chat_id = message.from_user.id
    user_data[chat_id].nationality = message.text
    user_lang = user_language.get(chat_id, 'kaz')
    if user_lang == "kaz":
        bot.send_message(chat_id, "Жасыңызды енгізіңіз:")
    elif user_lang == "rus":
        bot.send_message(chat_id, "Введите ваш возраст:")
    bot.register_next_step_handler(message, get_age)

def get_age(message):
    chat_id = message.from_user.id
    user_data[chat_id].age = message.text
    save_user_data()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    user_lang = user_language.get(chat_id)
    if user_lang == 'kaz':
        btn1 = types.KeyboardButton("Оқуды бастау")
        markup.add(btn1)
        bot.send_message(chat_id, "Тіркеу сәтті өтті!", reply_markup=markup)
    elif user_lang == 'rus':
        btn1 = types.KeyboardButton("Начать обучение")
        markup.add(btn1)
        bot.send_message(chat_id, "Регистрация прошла успешно!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Оқуды бастау", "Начать обучение", "Артқа", "Назад"])
def start_to_study(message):
    user_lang = user_language.get(message.from_user.id, 'kaz')
    if user_lang == "kaz":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Менің курстарым")
        btn2 = types.KeyboardButton('Курстар тізімі')
        btn3 = types.KeyboardButton('Байланыс контактілері')
        btn4 = types.KeyboardButton("Деректерді өзгерту")
        btn5 = types.KeyboardButton('Тілді ауыстыру')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(message.from_user.id, '👀 Өзіңізге қызықты бөлімді таңдаңыз', reply_markup=markup)
    elif user_lang == "rus":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Мои курсы")
        btn2 = types.KeyboardButton('Список курсов')
        btn3 = types.KeyboardButton('Контакты')
        btn4 = types.KeyboardButton('Изменить данные')
        btn5 = types.KeyboardButton('Сменить язык')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(message.from_user.id, '👀 Выберите интересующий вас раздел', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Байланыс контактілері", "Контакты", "Деректерді өзгерту","Изменить данные", "Тілді ауыстыру", "Сменить язык"])
def handle_buttons(message):
    if message.text == "Байланыс контактілері":
        bot.send_message(message.from_user.id, "Электрондық поштамыз: tiloqu@courses.kz\n"
                         "Қолдау қызметінің телефон нөмірі: 000-000\n"
                         "Веб-сайт: tiloqu.kz\n")
    elif message.text == "Контакты":
        bot.send_message(message.from_user.id, "Наша электронная почта: tiloqu@courses.kz\n"
                         "Номер телефона службы поддержки: 000-000\n"
                         "Веб-сайт: tiloqu.kz\n")
    elif message.text == "Деректерді өзгерту":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Тег")
        btn2 = types.KeyboardButton("Есім")
        btn3 = types.KeyboardButton("Әкесінің аты")
        btn4 = types.KeyboardButton("ЖСН")
        btn5 = types.KeyboardButton("Қала")
        btn6 = types.KeyboardButton("Ұлт")
        btn7 = types.KeyboardButton("Жас")
        btn8 = types.KeyboardButton("Артқа")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
        bot.send_message(message.from_user.id, "Өзгерткіңіз келетін деректі таңдаңыз:", reply_markup=markup)
    elif message.text == "Изменить данные":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Фамилия")
        btn2 = types.KeyboardButton("Имя")
        btn3 = types.KeyboardButton("Отчество")
        btn4 = types.KeyboardButton("ИИН")
        btn5 = types.KeyboardButton("Город")
        btn6 = types.KeyboardButton("Национальность")
        btn7 = types.KeyboardButton("Возраст")
        btn8 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
        bot.send_message(message.from_user.id, "Выберите данный который хотите поменять:", reply_markup=markup)
    elif message.text in ['Тілді ауыстыру', 'Сменить язык']:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Қазақ тілі")
        btn2 = types.KeyboardButton("Русский язык")
        markup.add(btn1, btn2)
        bot.send_message(message.from_user.id, "Тілді таңдаңыз / Выберите язык", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Фамилия", "Имя", "Отчество", "ИИН", "Город", "Национальность", "Возраст", "Тег", "Есім", "Әкесінің аты", "ЖСН", "Қала", "Ұлт", "Жас", "Артқа","Назад"])
def handle_data_change(message):
    chat_id = message.from_user.id
    attribute = message.text
    attributes_map = {
        "Фамилия": "surname",
        "Имя": "name",
        "Отчество": "patronymic",
        "ИИН": "iin",
        "Город": "city",
        "Национальность": "nationality",
        "Возраст": "age",
        "Тег": "surname",
        "Есім": "name",
        "Әкесінің аты": "patronymic",
        "ЖСН": "iin",
        "Қала": "city",
        "Ұлт": "nationality",
        "Жас": "age"
    }
    if attribute in attributes_map:
        markup = types.ReplyKeyboardRemove()
        bot.send_message(chat_id, f"Введите новое значение для {attribute}:" if attribute in ["Фамилия", "Имя", "Отчество", "Город", "Национальность", "Возраст"]
                         else f"Жаңа {attribute} үшін мәнді енгізіңіз:", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: update_user_data(msg, attributes_map[attribute]))
    elif message.text == 'Артқа':
        start_to_study(message)
    elif message.text == 'Назад':
        start_to_study(message)


def update_user_data(message, attribute):
    chat_id = message.from_user.id
    new_value = message.text
    if attribute == 'iin' and (not new_value.isdigit() or len(new_value) != 12):
        user_lang = user_language.get(chat_id, 'kaz')
        if user_lang == "kaz":
            bot.send_message(chat_id, "ЖСН 12 цифр болуы керек")
        elif user_lang == "rus":
            bot.send_message(chat_id, "ИИН должен состоять из 12 цифр")
        bot.register_next_step_handler(message, lambda msg: update_user_data(msg, attribute))
        return

    setattr(user_data[chat_id], attribute, new_value)
    save_user_data()

    user_lang = user_language.get(chat_id, 'kaz')
    if user_lang == 'kaz':
        bot.send_message(chat_id, "Деректер сәтті жаңартылды!")
    elif user_lang == 'rus':
        bot.send_message(chat_id, "Данные успешно обновлены!")

    start_to_study(message)


@bot.message_handler(func=lambda message: message.text in ["Менің курстарым", "Мои курсы"])
def My_course(message):
    chat_id = message.from_user.id
    mycourse = my_courses.get(chat_id, Courses())
    if message.text == "Менің курстарым":
        cours_list = "\n".join(mycourse.cours) if mycourse.cours else "📚 Бұл жерде сіздің курстарыңыз тізімі болады"
        bot.send_message(chat_id, cours_list)
    elif message.text == "Мои курсы":
        cours_list = "\n".join(mycourse.cours) if mycourse.cours else "📚 Здесь будет список ваших курсов"
        bot.send_message(chat_id, cours_list)


@bot.message_handler(func=lambda message: message.text in ["Курстар тізімі", "Список курсов"])
def handle_back_to_courses(message):
    chat_id = message.from_user.id
    user_lang = user_language.get(chat_id, 'kaz')
    if user_lang == 'kaz':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Қазақ тілі А (Бастапқы деңгей)")
        btn2 = types.KeyboardButton("Қазақ тілі В (Ортаңғы деңгей)")
        btn3 = types.KeyboardButton("Қазақ тілі С (Жоғарғы деңгей)")
        btn4 = types.KeyboardButton("Артқа")
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)
        markup.add(btn4)
        bot.send_message(chat_id, "📚 Өзіңізге қолайлы курсты таңдаңыз: ", reply_markup=markup)
    elif user_lang == 'rus':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Казахский язык А (Начальный уровень)")
        btn2 = types.KeyboardButton("Казахский язык В (Средний уровень)")
        btn3 = types.KeyboardButton("Казахский язык С (Высокий уровень)")
        btn4 = types.KeyboardButton("Назад")
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)
        markup.add(btn4)
        bot.send_message(chat_id, "📚 Выберите подходящий для себя курс: ", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ['Қазақ тілі А (Бастапқы деңгей)', 'Қазақ тілі В (Ортаңғы деңгей)', 'Қазақ тілі С (Жоғарғы деңгей)', 'Казахский язык А (Начальный уровень)', 'Казахский язык В (Средний уровень)', 'Казахский язык С (Высокий уровень)'])
def choiche_of_course(message):
    chat_id = message.from_user.id
    selected_course = None
    if message.text == 'Қазақ тілі А (Бастапқы деңгей)':
        user_language[chat_id] = 'kaz'
        selected_course = 'Қазақ тілі А (Бастапқы деңгей)'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Қосу")
        btn2 = types.KeyboardButton("Курстарға оралу")
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(message.from_user.id,'Қазақ тілі А (Бастапқы деңгей) курсын таңдадыңыз', reply_markup=markup)
    elif message.text == 'Қазақ тілі В (Ортаңғы деңгей)':
        user_language[chat_id] = 'kaz'
        selected_course = 'Қазақ тілі В (Ортаңғы деңгей)'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Қосу")
        btn2 = types.KeyboardButton("Курстарға оралу")
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(message.from_user.id,'Қазақ тілі В (Ортаңғы деңгей) курсын таңдадыңыз', reply_markup=markup)
    elif message.text == 'Қазақ тілі С (Жоғарғы деңгей)':
        user_language[chat_id] = 'kaz'
        selected_course = 'Қазақ тілі С (Жоғарғы деңгей)'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Қосу")
        btn2 = types.KeyboardButton("Курстарға оралу")
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(message.from_user.id, 'Қазақ тілі С (Жоғарғы деңгей) курсын таңдадыңыз', reply_markup=markup)
    elif message.text == 'Казахский язык А (Начальный уровень)':
        user_language[chat_id] = 'rus'
        selected_course = 'Казахский язык А (Начальный уровень)'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить")
        btn2 = types.KeyboardButton("Назад к курсам")
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(message.from_user.id, 'Вы выбрали курс Казахский язык А (Начальный уровень)', reply_markup=markup)
    elif message.text == 'Казахский язык В (Средний уровень)':
        user_language[chat_id] = 'rus'
        selected_course = 'Казахский язык В (Средний уровень)'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить")
        btn2 = types.KeyboardButton("Назад к курсам")
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(message.from_user.id, 'Вы выбрали курс Казахский язык В (Средний уровень)', reply_markup=markup)
    elif message.text == 'Казахский язык С (Высокий уровень)':
        user_language[chat_id] = 'rus'
        selected_course = 'Казахский язык С (Высокий уровень)'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить")
        btn2 = types.KeyboardButton("Назад к курсам")
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(message.from_user.id, 'Вы выбрали курс Казахский язык С (Высокий уровень)', reply_markup=markup)
    my_courses[chat_id] = my_courses.get(chat_id, Courses())
    my_courses[chat_id].selected_course = selected_course
    print("Selected course:", selected_course)


@bot.message_handler(func=lambda message: message.text in ['Добавить', 'Қосу'])
def add_course(message):
    chat_id = message.from_user.id
    mycourse = my_courses.get(chat_id, Courses())
    selected_course = mycourse.selected_course
    if selected_course:
        if selected_course in mycourse.cours:
            if user_language.get(chat_id) == 'kaz':
                bot.send_message(chat_id, "Сіз бұл курсқа жазылып қойдыңыз")
            elif user_language.get(chat_id) == 'rus':
                bot.send_message(chat_id, "Вы уже записаны на этот курс")
        else:
            mycourse.cours.append(selected_course)
            my_courses[chat_id] = mycourse
            save_cours_data()
            if user_language.get(chat_id) == 'kaz':
                bot.send_message(chat_id, "Курсқа қосылдыңыз")
            elif user_language.get(chat_id) == 'rus':
                bot.send_message(chat_id, "Вы добавились к курсу")
        start_to_study(message)
    else:
        print("Selected course not found.")



@bot.message_handler(func=lambda message: message.text in ['Назад к курсам', 'Курстарға оралу'])
def cours_back(message):
    if message.text == 'Курстарға оралу':
        handle_back_to_courses(message)
    elif message.text == 'Назад к курсам':
        handle_back_to_courses(message)

@bot.message_handler(func=lambda message: message.text in ['Қазақ тілі', 'Русский язык'])
def change_language(message):
    chat_id = message.from_user.id
    if message.text == 'Қазақ тілі':
        user_language[chat_id] = 'kaz'
        start_to_study(message)
    elif message.text == 'Русский язык':
        user_language[chat_id] = 'rus'
        start_to_study(message)

@bot.message_handler()
def send_welcome(message: telebot.types.Message):
    bot.reply_to(message, message.text)
bot.set_my_commands([
    telebot.types.BotCommand("/start", "Перезапуск бота/Ботты қайта қосу"),
])

def send_data_to_server(user_id, action, timestamp, metadata=None):
    data = {
        'user_id': user_id,
        'action': action,
        'timestamp': timestamp,
        'metadata': metadata
    }
    response = requests.post('http://127.0.0.1:8088/log_action', json=data)
    if response.status_code == 200:
        print("Данные успешно отправлены на сервер")
    else:
        print("Ошибка при отправке данных на сервер")

load_user_data()
load_cours_data()
bot.infinity_polling()

