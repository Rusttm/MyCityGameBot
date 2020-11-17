import telebot
import time
import pandas
import psycopg2
import os

huser=str(os.environ.get('User_heroku'))
hpassword=str(os.environ.get('Password_heroku'))
hhost=str(os.environ.get('Host_heroku'))
hport=int(os.environ.get('Port_heroku'))
hdatabase=str(os.environ.get('Database_heroku'))
tb_token = int(os.environ.get('bot_token'))




try:
    connection = psycopg2.connect(user=huser,
                                  password=hpassword,
                                  host=hhost,
                                  port=hport,
                                  database=hdatabase)
    #connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cities")
    tuples_city = cursor.fetchall()
    df_city= pandas.DataFrame(tuples_city, columns=['region_id', 'country_id', 'city_id', 'city'])
    cursor.execute("SELECT * FROM countries")
    tuples_country = cursor.fetchall()
    df_country=pandas.DataFrame(tuples_country, columns=['country_id', 'country'])

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")


#bot_url = f"https://api.telegram.org/bot{bot_token}/"
bot_user_name='MyCityBot'
my_chat_id=731370983 #John Lennon id
tb = telebot.TeleBot('tb_token')
users_archive={1:[]} # будем сохранять данные в виде {chatid:'last_city'}
exceptions=['ь', 'ъ', 'ы', 'ё',  'й']
def messg_from_user(user_id,text):
    c = text.lower()
    if c in users_archive[user_id]:
        y=c[0].title()+c[1:]
        tb.send_message(user_id, f'город {y} уже называли')
    find_user_answer(user_id,text)

def find_user_answer(user_id,c):
    c=c.lower()
    last_city_in_game=users_archive[user_id][-1]
    countr='Russia'
    if last_city_in_game[-1] in exceptions:
        last_symbol = last_city_in_game[-2]
    else:
        last_symbol = last_city_in_game[-1]
    for _, row in df_city.iterrows():  # looking in cities file
        # print(row[3].lower(),c) check a accordance
        if (row[3].lower() == c) and (c[0] == last_symbol) and (c not in users_archive[user_id]):
            for _, rrow in df_country.iterrows():
                #tb.send_message(user_id, f'Ive find it!!!{rrow[2]}-{rrow[0]}')
                if row[1] == rrow[0]:
                    countr = rrow[1]
                    #tb.send_message(user_id, f'Ive find it!!!{rrow[2]}')
            users_archive[user_id].append(c)
            tb.send_message(user_id, f'{row[3]} ({countr})-прекрасный город')
            find_comp_answer(user_id,c)
            break
        if row[3].lower() == "индепенденс":
            x=last_city_in_game[0].title()+last_city_in_game[1:]
            tb.send_message(user_id, f'Последний названный город был - {x}, назовите город на букву "{last_symbol.title()}"')
            break

def find_comp_answer(user_id,c):
    countr = 'Russia'
    if c[-1] in exceptions:
        last_symbol = c[-2]
    else:
        last_symbol = c[-1]
    for index, row in df_city.iterrows():
        if (row[3].lower()[0] == last_symbol) and (row[3].lower() not in users_archive[user_id]):  #
            for index, rrow in df_country.iterrows():
                if row[1] == rrow[0]: countr = rrow[1]
            city = row[3]
            tb.send_message(user_id,f'Мой ответ - {city} ({countr})')
            users_archive[user_id].append(city.lower())
            break
        if row[3].lower() == "индепенденс":
            tb.send_message(user_id, "Потрясающе!!! Вы выиграли. Мои поздравления!")


def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        chatid = m.chat.id
        users_name = m.chat.first_name
        if m.content_type == 'text':
            if chatid not in users_archive.keys():
                users_archive[chatid]=[]
                users_archive[chatid].append('Анапа')
                tb.send_message(chatid, f'Добро пожаловать, {users_name}, сыграем в игру "Города"?')
                tb.send_message(chatid, f'Введите город на букву "А"')
            else:
                messg_from_user(chatid,m.text)

tb.set_update_listener(listener) #register listener
#tb.polling()
#Use none_stop flag let polling will not stop when get new message occur error.
#tb.polling(none_stop=True)
# Interval setup. Sleep 3 secs between request new message.
tb.polling(interval=3)

#while True: # Don't let the main Thread end.
#    pass
