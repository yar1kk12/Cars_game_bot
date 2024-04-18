import telebot
from random import choice, randint
from telebot import types
from os import listdir
# BOT_TOKEN = YOUR BOT TOKEN
bot = telebot.TeleBot(BOT_TOKEN)


isStarted = False
isModeStarted = False

checker = True

Results = {
    'Correct_answers' : 0,
    'Incorrect_answers' : 0,
    'Points' : 0,
    'Coins' : 30
}
Tip = False
current_mode = ''
rand_list = []
list_years = []
year = ''
message_id = 0





# Глобальна клавіатура-меню
markup_keyb_global = types.ReplyKeyboardMarkup()
button_1 = 'Вгадай логотип'
button_2 = 'Вгадай марку за фрагментом фото'
button_3 = 'Вгадай рік випуску авто'
button_4 = 'Баланс 💵'
markup_keyb_global.add(button_1, button_2)
markup_keyb_global.add(button_3)
markup_keyb_global.add(button_4)


def Tips_keyb():
    keyb = types.InlineKeyboardMarkup()
    button_a = types.InlineKeyboardButton('Я згоден', callback_data='Agree')
    button_d = types.InlineKeyboardButton("Я не згоден", callback_data='Disagree')
    keyb.add(button_a,button_d)
    return keyb


# Функція що визиває клавіатуру з кнопокю завершення гри та підсказками
def cancel_keyb():
    markup_keyb = types.ReplyKeyboardMarkup()
    markup_keyb.add('Завершити гру')
    markup_keyb.add('Підсказка 💡')
    return markup_keyb

# Функція надсилає результати, онуляє рахунок та визиває меню-клавіатуру
def send_results(message):
    global Correct_answers, Incorrect_answers, isModeStarted,Results
    isModeStarted = False
    Results["Coins"] += Results["Points"] * 2
    bot.send_message(message.chat.id,
                     f'🏁 Гру завершенно! \n\n'
                     f'✅ Ви відповіли на {Results["Correct_answers"]} з {Results["Correct_answers"]+Results["Incorrect_answers"]}\n\n'
                     f'🏆 Всього балів набрано: {Results["Points"]}\n\n'
                     f'💵 За це ви отримали {Results["Points"] * 2} монет, які можете витратити на підсказки',
                     reply_markup=markup_keyb_global)

    Results['Correct_answers'] = 0
    Results['Incorrect_answers'] = 0
    Results['Points'] = 0
    isModeStarted = False


# Сама гра
def game(message):
    global current_mode, list_ph, rand_list, isModeStarted, year, list_years,message_id, Tip, checker
# Оновлення списку елементів, якщо гра ще не розпочата
    if not isModeStarted:
        list_ph = listdir(current_mode)
        rand_list = list_ph.copy()

    isModeStarted = True

    if current_mode == 'Logos' or current_mode == 'Pictures':
        global temp_list, name, ph_data
        if not Tip and checker:
            temp_list = [] #Створення списку для зберігання рандомних елементів(для вибору)
            name = choice(list_ph) #Вибір елементу який треба вгадати
            list_ph.pop(list_ph.index(name)) #Видалення цього елементу зі списку
            rand_list.pop(rand_list.index(name))

            with open(f'{current_mode}/{name}', 'rb') as ph: #зчитування данних фото
                ph_data = ph.read()

        inl_keyb = types.InlineKeyboardMarkup() #створення інлайн клавіатури
        if Tip:
            count = 2
        else:
            count = 4

        if len(list_ph) > 1: #Поки є об'єкти для питання
            num = randint(1, count)  # це рандомне число що відповідає за те на якому місці буде правильна відповідь
            for i in range(1,count+1):
                if num == i: #Вставка правильної відповіді до клавіатури
                    button = types.InlineKeyboardButton(name.split('.')[0], callback_data='True')
                    inl_keyb.add(button)
                else: #Вставка неправильних відповідей до клавіатури
                    name_rand = choice(rand_list)
                    button = types.InlineKeyboardButton(name_rand.split('.')[0], callback_data='False')
                    inl_keyb.add(button)
                    rand_list.pop(rand_list.index(name_rand))
                    temp_list.append(name_rand) #Додає елемент до тимчасового списку
            rand_list.append(name) #Повертає елемент правильної відповіді до списку з рандомними
            if message_id:
                bot.delete_message(message.chat.id, message_id) #Видаляє минуле питання

            message_id = bot.send_photo(message.chat.id, #Надсилає наступне питання
                           ph_data,
                           reply_markup=inl_keyb).message_id
            Tip = False
            checker = True

            for el in temp_list:
                rand_list.append(el) #Повертає елементи до рандомного списку
        else: #Якщо елементи закінчилися
            bot.send_message(message.chat.id,
                             'Автомобілі закінчилися 🤷‍♂️')

            send_results(message)

    elif current_mode == 'Year': #Логіка для третього режиму
        name = choice(list_ph) #Обриає елемент який треба вгадати
        year = (name.split('.')[0])[:-2] #Бере назву без зайвих знаків
        list_ph.pop(list_ph.index(name)) #Видалаяє елемент зі списку

        if len(list_ph) > 1:
            with open(f'{current_mode}/{name}', 'rb') as ph:
                ph_data = ph.read()
            bot.send_photo(message.chat.id,
                           ph_data)
        else:
            bot.send_message(message.chat.id,
                             'Автомобілі закінчилися 🤷‍♂️')
            send_results(message)
        return year


@bot.message_handler(commands=['start'])
def start_game(message):
    global markup_keyb_global, isStarted
    if message.text == '/start':
        isStarted = True
        bot.send_message(message.chat.id, 'Вітаю тебе, Друже.')
        bot.send_message(message.chat.id, f'Для початку гри обери режим нижче:  ',
                         reply_markup = markup_keyb_global) #Виклик глобальної клавіатури


@bot.message_handler(content_types='text')
def mode_select(message):
    global current_mode,isModeStarted, Results, Tip
    if isStarted:
        if not isModeStarted: #Реагує на повідомлення для вибіру режиму гри
            if message.text == 'Завершити гру':
                bot.send_message(message.chat.id,
                                 'Гру ще не розпочато. Якщо бажаєте розпочати, оберіть режим нижче.', reply_markup=markup_keyb_global)

            elif message.text == 'Вгадай логотип':
                current_mode = 'Logos'

                bot.send_message(message.chat.id,
                                 'Ваша задача вгадати що за логотип зображений на фото та натиснути відповідну кнопку '
                                 'під зображенням', reply_markup=cancel_keyb())
                game(message)
            elif message.text == 'Вгадай марку за фрагментом фото':
                current_mode = 'Pictures'
                bot.send_message(message.chat.id,
                                 'Ваша задача вгадати що за авто зображенно на фото та натиснути відповідну кнопку '
                                 'під зображенням', reply_markup=cancel_keyb())
                game(message)
            elif message.text == 'Вгадай рік випуску авто':
                current_mode = 'Year'
                bot.send_message(message.chat.id,
                                 f'Ваша задача вгадати який рік випуску авто зображенного на фото та надіслати відповідь.\n\n'
                                 f'Якщо ваша відповідь відрізняється від правильної не більше ніж на 2 роки: +3 бали\n\n'
                                 f'Якщо ваша відповідь дорівнює правильній: +5 балів', reply_markup=cancel_keyb())
                game(message)

            elif message.text == 'Баланс 💵':
                bot.send_message(message.chat.id, f'💵 Ваш поточний баланс: \n\n{Results["Coins"]} монет')
                bot.send_message(message.chat.id, f'\n\nЦі монети ви можете використовувати для підсказок ')
        elif isModeStarted:
            if message.text == 'Завершити гру':
                send_results(message)
            elif message.text == 'Підсказка 💡':
                if Results["Coins"] > 5:
                    bot.send_message(message.chat.id, f'Якщо ви бажаєте скористатися підсказкою, то з вашого балансу буде знято 5 монет.\n'
                                                      f'\nВаш поточний баланс: {Results["Coins"]}\n'
                                                      f'\nВи згодні?', reply_markup=Tips_keyb())

                else:
                    bot.send_message(message.chat.id,'На вашому балансі недостатньо монет. Для цього потрібно щонайменше 5 монет.')

            elif current_mode == 'Year': #Логіка нараховування балів в третьому режимі гри
                if message.text == year:
                    Results['Correct_answers'] += 1
                    bot.send_message(message.chat.id,
                                     f'Відповідь правильна ✅\n\nВам нараховано +5 балів')
                    Results["Points"] += 5
                    game(message)

                elif int(message.text) >= int(year)-2 and int(message.text) <= int(year)+2:
                    Results['Correct_answers'] += 1
                    bot.send_message(message.chat.id,
                                     f'Ви майже вгадали. Цей автомобіль {year} року\n\n'
                                     f'Вам нараховано +3 бали ')
                    Results["Points"] += 3
                    game(message)

                elif message.text != year:
                    Results['Incorrect_answers'] += 1
                    bot.send_message(message.chat.id,
                                     f'Відповідь неправильна ❌.\nПравильна відповідь: {year}')
                    game(message)

    else:
        bot.send_message(message.chat.id,
                         f'Спочатку треба прописати /start')


@bot.callback_query_handler(lambda a: True)
def get_query(query): #Обробка натиснень на клавіатуру для перших двох режимів
    global Correct_answers, Incorrect_answers, Results, Tip, checker
    if query.data == 'True':
        Results['Correct_answers'] += 1
        Results["Points"] += 2
        bot.send_message(query.message.chat.id,
                         f'Відповідь правильна ✅\n\n+2 бали')
        game(query.message)
    elif query.data == 'False':
        Results['Incorrect_answers'] += 1
        bot.send_message(query.message.chat.id,
                         f'Відповідь неправильна ❌')
        game(query.message)

    elif query.data == 'Agree':
        Results["Coins"] -= 5
        if current_mode == 'Logos' or current_mode == 'Pictures':
            Tip = True
            game(query.message)
        elif current_mode == 'Year':
            bot.send_message(query.message.chat.id,
                             f'Цей авто було випущенно у проміжку від {int(year) - 3} до {int(year) + 3}')

    elif query.data == 'Disagree':
        checker = False
        game(query.message)

bot.polling()