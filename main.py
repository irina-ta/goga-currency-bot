
import traceback
from datetime import date, datetime, timedelta
import telebot
from tabulate import tabulate
import pandas as pd 

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from data_source import get_currencies, get_for_period

token = '1421014662:AAEbW9Gk94QFLYUH1wF_7FxnA-B51XoqkWQ'

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")


def format_list(df: pd.DataFrame) -> str: 

    output = df.apply(lambda r: f'''[{r['Букв. код']}] {r['Валюта']}: {r['Курс']} Р. ''', axis=1)
    output = '\n'.join(output)

    return output

def format_period(df: pd.DataFrame) -> str:
    output = 'Валюта ' + df['Валюта'].values[0] + '\n'
    
    output += '\n'.join( df.apply(lambda x: f'''{x['Дата'].strftime('%d.%m.%Y')}: {x['Курс']}''', axis=1) )

    return output



@bot.message_handler(commands=['сегодня'])
def print_today(message):

    df = get_currencies(date.today())

    bot.send_message(message.chat.id, format_list(df))


@bot.message_handler(commands=['на'])
def print_on_day(message):
    
    def send_format_date_error():
        bot.send_message(message.chat.id, 'Введите дату в формате dd.mm.yyyy, например: \n \\на 31.12.2012')

    text: str = message.text
    text_parts = text.split(' ')
    if len(text_parts) < 2:
        send_format_date_error()
        return
    text = text_parts[1].strip()
    if not text:
        send_format_date_error()
        return
    
    inp_date: date = None
    try:
        inp_date = datetime.strptime(text, '%d.%m.%Y')
    except:
        send_format_date_error()
        return

    inp_date = inp_date.date()

    df = get_currencies(inp_date)
    bot.send_message(message.chat.id, format_list(df))
    # print(tabulate(for_sending, headers=for_sending.columns))

@bot.message_handler(commands=['валюта'])
def print_one_currency(message):
    # print(message)
    try:
        text: str = message.text
        text = text.split(' ')[1]
        curr = text.upper()

        bot.send_message(message.chat.id, 'Минутку...')

        fr = date.today() - timedelta(days=30)
        to = date.today()
        df: pd.DataFrame = get_for_period(fr, to)
        df = df[(df['Букв. код'] == curr)]

        if df.shape[0]:
            # bot.send_message(message.chat.id, format_period(df))
            
            cur_date = df[ df['Дата'] == date.today()]
            cur_status = f'''Курс на сегодня {cur_date['Курс'].values[0]} Р.'''
            bot.send_message(message.chat.id, cur_status)
            
            plt_data = df[['Курс', 'Дата']].groupby('Дата').mean()

            plt.ioff()
            plt.plot(plt_data)
            #plt.close()
            
            plt.xticks(rotation=45)
                # plt.sca(ax)
                # tick.set_rotation(45)
            
            plt.xlabel("Дата")
            plt.ylabel("Курс")
            
            filename = 'plot_' + str(message.chat.id) + '.png'
            plt.savefig(filename, bbox_inches="tight")
            
            with open(filename, 'rb') as f:
                bot.send_photo(message.chat.id, photo=f)
            plt.close()
        else:
            bot.send_message(message.chat.id, 'Неизвестный код валюты')
    except: 
        try:
            bot.send_message(message.chat.id, 'Кажется, что-то пошло не так. Попробуйте позже')
        except: 
            pass
        # traceback.print_exc()
    

if __name__ == '__main__':
    bot.infinity_polling()
    