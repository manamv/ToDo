import telebot
from telebot import types
import datetime
import sqlite3

# Создаем бота
bot = telebot.TeleBot('SECRET_TOKEN')


# Функция для добавления задачи в базу данных
def add_task_to_db(user_id, task_text, importance, deadline):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("INSERT INTO tasks (user_id, task, importance, deadline, completed) VALUES (?, ?, ?, ?, ?)",
              (user_id, task_text, importance, deadline, 0))
    conn.commit()
    conn.close()


# Функция для получения задач пользователя из базы данных
def get_user_tasks_from_db(user_id):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
    tasks = c.fetchall()
    conn.close()
    return tasks


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message,
                 f'''Я помогу тебе составить список дел на день! Вот список доступных команд:
/start
/add_task - добавить задачу (укажите текст задачи, степень важности (целое число от 1 до 10) и дедлайн в формате YYYY-MM-DD HH:MM, разделенные запятой)
/remove_task - удалить задачу ()
/view_tasks - посмотреть список задач
/set_time - изменить дедлайн задачи ()
/lestxt - изменить текст задачи ()
/importance - изменить важность ()
/complection - изменить состояние исполнения ()
                ''')


# Обработчик команды /start
@bot.message_handler(commands=['start', 'main', 'hello', 'привет'])
def start(message):
    bot.reply_to(message,
                 f'Привет, {message.from_user.first_name}! Я ToDo бот. Чтобы добавить задачу, используй команду /add_task.')


# Обработчик команды /add_task
@bot.message_handler(commands=['add_task'])
def add_task(message):
    try:
        task_text, importance, deadline = message.text.replace('/add_task', '').strip().split(',')
        task_text = task_text.strip()
        importance = int(importance.strip())
        deadline = datetime.datetime.strptime(deadline.strip(), "%Y-%m-%d %H:%M")
        user_id = message.chat.id
        add_task_to_db(user_id, task_text, importance, deadline)
        bot.reply_to(message, f'Задача "{task_text}" добавлена.')
    except ValueError:
        bot.reply_to(message,
                     'Пожалуйста, укажите текст задачи, степень важности (целое число от 1 до 10) и дедлайн в формате YYYY-MM-DD HH:MM, разделенные запятой.')


# Обработчик команды /view_tasks
@bot.message_handler(commands=['view_tasks'])
def view_tasks(message):
    user_id = message.chat.id
    tasks = get_user_tasks_from_db(user_id)
    if tasks:
        task_str = '\n'.join(
            [
                f"{'ПРОСРОЧЕНО: ' if datetime.datetime.strptime(task[4], '%Y-%m-%d %H:%M:%S') < datetime.datetime.now() else ''}{task[0]}. {task[2]} (Важность: {task[3]}, Дедлайн: {task[4]}, Завершено: {'Да' if task[5] else 'Нет'})"
                for task in tasks])
        bot.reply_to(message, f'Ваши текущие задачи:\n{task_str}')
    else:
        bot.reply_to(message, 'У вас нет задач.')


# Обработчик команды /remove_task
@bot.message_handler(commands=['remove_task'])
def remove_task(message):
    try:
        task_id = int(message.text.replace('/remove_task', '').strip())
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
        bot.reply_to(message, 'Задача удалена.')
    except ValueError:
        bot.reply_to(message, 'Пожалуйста, укажите номер задачи для удаления.')


# Обработчик команды /set_time
@bot.message_handler(commands=['set_time'])
def set_time(message, task_id, new_deadline):
    try:
        task_id, new_deadline = message.text.replace('/set_time', '').strip().split(',')
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("UPDATE tasks SET deadline=? WHERE id=?", (new_deadline, task_id))
        conn.commit()
        conn.close()
        succes(message)
    except:
        handle_unknown(message)


# Обработчик команды /lestxt
@bot.message_handler(commands=['lestxt'])
def lestxt(message):
    try:
        task_id, new_txt = message.text.replace('/lestxt', '').strip().split(',')
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("UPDATE tasks SET task=? WHERE id=?", (new_txt, task_id))
        conn.commit()
        conn.close()
        succes(message)
    except:
        handle_unknown(message)


# Обработчик команды /importance
@bot.message_handler(commands=['importance'])
def importance(message):
    try:
        task_id, new_importance = message.text.replace('/importance', '').strip().split(',')
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("UPDATE tasks SET importance=? WHERE id=?", (new_importance, task_id))
        conn.commit()
        conn.close()
        succes(message)
    except:
        handle_unknown(message)


# Обработчик команды /complection
@bot.message_handler(commands=['complection'])
def complection(message):
    try:
        task_id, completed = message.text.replace('/complection', '').strip().split(',')
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("UPDATE tasks SET completed=? WHERE id=?", (completed, task_id))
        conn.commit()
        conn.close()
        succes(message)
    except:
        handle_unknown(message)


# Функция для сортировки задач
@bot.message_handler(commands=['sort'])
def sort(message):
    try:
        user_id = message.from_user.id
        param = message.text.replace('/sort', '').strip().split(',')[0].lower()
        if param == 'дедлайн':
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("SELECT * FROM tasks WHERE user_id=? ORDER BY deadline", (user_id,))
            sorted_tasks = c.fetchall()
            conn.close()
            succes(message)
            return sorted_tasks
        elif param == "важность":
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("SELECT * FROM tasks WHERE user_id=? ORDER BY importance DESC", (user_id,))
            sorted_tasks = c.fetchall()
            conn.close()
            succes(message)
            return sorted_tasks
        else:
            handle_unknown(message)
    except:
        handle_unknown(message)


# Функция для удаления задач по параметру
@bot.message_handler(commands=['delete_tasks'])
def delete_tasks(message):
    try:
        param = message.text.replace('/delete_tasks', '').strip().split(',')[0].lower()
        if param == 'исполненные':
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE completed>0")
            conn.commit()
            conn.close()
            succes(message)
        elif param == 'просроченные':
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            current_date = datetime.datetime.now().date()
            c.execute("DELETE FROM tasks WHERE deadline < ?", (current_date,))
            conn.commit()
            conn.close()
            succes(message)
        else:
            handle_unknown(message)
    except:
        handle_unknown(message)


# вывод просроченных дедлайнов
@bot.message_handler(commands=['deadlines'])
def deadlines(message):
    pass

# Обработчик неизвестных команд
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.reply_to(message,
                 'Извините, я не понимаю эту команду. Возможно, вы допустили ошибку. Все доступные комнады в /help')


# успешная обработка команды
@bot.message_handler(func=lambda message: True)
def succes(message):
    bot.reply_to(message, 'Команда успешно исполнена')


# Запускаем бота
bot.polling()

# сделать так, чтобы для каждого пользователя создавалась новая таблица
# добавить указание просроченого делайна
# вывод просроченных дедлайнов
# добавить возможность прикрепления к задаче ссылки с картинкой
# добавить вывод списка дел на день на каждое утро
# добавить вывод списке сделанных дел на каждый вечер
