#Импортируем все нужные компоненты для разработки бота
from django.core.management.base import BaseCommand
from django.conf import settings

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    Filters,
    MessageHandler,
    Updater,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler)
from telegram.utils.request import Request

from AlphaBots.models import Profile
from AlphaBots.GoogleSheets.export_data import set_data

#Создадим обьект бота с токеном взятым с настроек
bot = Bot(token=settings.TOKEN)

def start(update, _):
    #Обьявляем глобальные переменные для дальнейшей передачи их в админу и в таблицу
    #При перезапуске бота поля обновляются
    global chat_id
    global username
    global selected_answers
    global quest_keyboard
    global result

    selected_answers = []
    result = []
    username = update.message.from_user.username
    chat_id = update.message.chat_id

    #Сразу при старте сохраним айди пользователя и его юзернейм
    result.append(chat_id)
    result.append(username)

    #Создадим клавиатуры для дальнейшей работы
    #Это нужно чтобы выбранные ответы не сохранялись
    quest_keyboard = [
        [
            InlineKeyboardButton("Ответ 1", callback_data=1),
            InlineKeyboardButton("Ответ 2", callback_data=2),
            InlineKeyboardButton("Ответ 3", callback_data=3),
        ],
        [InlineKeyboardButton("Продолжить \u27A1", callback_data='submit')],
    ]

    keyboard = [
        [InlineKeyboardButton("Пройти \u27A1", callback_data='submit')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Приветствую \n\n Пожалуйста, пройдите анкету:', reply_markup=reply_markup)

def start_error(update: Update, _):
    #Если пользователь запустил бота и пишет сообщение
    update.message.reply_text('Нажмите на кнопку\nИли перезапустите бота >> /start')

def button(update, _):
    #Переход на следующее состояние после нажатия кнопки
    query = update.callback_query
    query.answer()
    query.delete_message()
    bot.sendMessage(chat_id=chat_id, text='Введите ваше имя:\nДвойное имя вводить через пробел')

    return 'GET_USERNAME'

def get_name(update: Update, _):
    global fullname

    #Валидация введённого имени пользователя.
    #Оно не должно быть короче двух символов и длинее 20 символов.
    #при вводе двойного имени слова не должны быть короче двух символов.
    #имя должно состоять только из букв.
    string = update.message.text
    subString = ''
    words = []
    if ' ' in string and len(string) <= 35:
        for word in string.split(' '):
            if 2 <= len(word) <= 20:
                words.append(word)
            else:
                words.clear()
                break
        subString = ''.join(words)
        fullname = ' '.join(words)
    else:
        fullname = string
    if (fullname.isalpha() and 2 <= len(fullname) <= 20) or subString.isalpha():
        update.message.reply_text(text="Введите ваш номер телефона: \n\n+38(XXX)XXX-XX-XX")
        result.append(fullname)
        return 'GET_PHONE'
    else:
        update.message.reply_text(
            text='Неверное имя'
        )

def get_phone(update: Update, _):
    global phone

    #Валидация номера телефона пользователя.
    #Он должен быть строго 10 символов и состоять только из цифр
    phone = update.message.text
    if phone.isdigit() and len(phone) == 10:
        reply_markup = InlineKeyboardMarkup(quest_keyboard)
        update.message.reply_text('Пожалуйста, ответьте:\n\n *Вопрос*', reply_markup=reply_markup)
        result.append(phone)

        return 'SUBMIT'
    else:
        update.message.reply_text(
            text='Неверный номер телефона',
        )

def submit(update: Update, _):
    query = update.callback_query
    variant = query.data

    #Обработка кнопок опроса
    if not variant == 'submit':
        answer = query.message.reply_markup.inline_keyboard[0][int(variant) - 1].text
        # Ставим галочку если кнопка до этого не была нажата
        if answer == 'Ответ {}'.format(variant):
            #сохраняем выбранные варианты
            selected_answers.append(answer)
            quest_keyboard[0][int(variant)-1] = InlineKeyboardButton('\u2705 Ответ {}'.format(variant), callback_data='{}'.format(variant))
        # Убираем галочку при повторном нажатии на кнопку
        else:
            answer = answer[2:]
            print(answer)
            selected_answers.remove(answer)
            quest_keyboard[0][int(variant)-1] = InlineKeyboardButton('Ответ {}'.format(variant), callback_data='{}'.format(variant))

        reply_markup = InlineKeyboardMarkup(quest_keyboard)
        query.edit_message_text(text='Пожалуйста, ответьте:\n\n *Вопрос*', reply_markup=reply_markup)
    else:
        if len(selected_answers) == 0:
            bot.sendMessage(chat_id=chat_id, text='Пожалуйста, выберите ответ')
        else:
            query.edit_message_text(text='Спасибо за ответы')
            result.append(', '.join(selected_answers))

            #Сохраняем данные в базу данных
            p, created = Profile.objects.get_or_create(
                external_id=chat_id,
                username=username,
                name=fullname.title(),
                phoneNumber=phone,
                answers=', '.join(selected_answers)
            )
            #Передаем данные для записи в гугл таблицу
            #AlphaBots > GoogleSheets > export_data
            set_data(result)
            return ConversationHandler.END

def cancel(update: Update, _):
    update.message.reply_text(
        text="Пока!",
    )
    return ConversationHandler.END

def error_format(update, _):
    #При отправке фото или видео боту
    update.message.reply_text(text='Неверный формат сообщения')

class Command(BaseCommand):
    help = 'Телеграм-бот'

    @staticmethod
    def handle(*args, **options):
        request = Request(
            connect_timeout=15,
            read_timeout=20,
        )
        bot = Bot(
            request=request,
            token=settings.TOKEN,
        )

        updater = Updater(
            bot=bot,
            use_context=True,
        )

        updater.dispatcher.add_handler(MessageHandler(Filters.photo | Filters.video | Filters.audio, error_format))
        updater.dispatcher.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler('start', start),
                CallbackQueryHandler(button),
                MessageHandler(Filters.text, start_error),
            ],
            states={
                'GET_USERNAME': [
                    MessageHandler(Filters.text, get_name)
                ],
                'GET_PHONE': [
                    MessageHandler(Filters.text, get_phone),
                ],
                'SUBMIT': [
                    CallbackQueryHandler(submit)
                ]
            },
            fallbacks=[
                CommandHandler('cancel', cancel)
            ]
        ))

        updater.start_polling()
        updater.idle()
