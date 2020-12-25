
import requests

from bs4 import BeautifulSoup
import pandas as pd 

import math
from datetime import date, timedelta


def strip_name(s: str):
    # s = s[:15] + '..' if len(s) > 20 else s
    # s = s +  (' ' * (20 - len(s)))
    return s

def _get_raw(date: date) -> dict:
    
    date_str = date.strftime('%d.%m.%Y')
    url = 'https://cbr.ru/currency_base/daily/?UniDbQuery.Posted=True&UniDbQuery.To=' + date_str
    website = requests.get(url).text
    soup = BeautifulSoup(website, 'lxml')
    table = soup.find_all('table')[0]
    rows = table.find_all('tr')

    h_cells = list(map(lambda r: r.get_text(), rows[0].find_all('th'))) # заголовки
    data = {h: [] for h in h_cells}
    for row in rows[1:]:
        # row.find_all('td') - список ячеек в строке (i - номер, cell - содержимое ячейки)
        for i, cell in enumerate(row.find_all('td')):
            data[h_cells[i]].append(cell.get_text()) # по заголовкам - спиисок содержимого в столбце

    parse_float = lambda s: round(float(s.replace(',', '.')), 8) 
    data['Курс'] = list(map(parse_float, data['Курс']))
    data['Единиц'] = list(map(parse_float, data['Единиц']))

    return data



def get_currencies(input_date: date) -> pd.DataFrame:
    if input_date is None:
        input_date = date.today()

    data = _get_raw(input_date)
    df = pd.DataFrame(data)


    data['Валюта'] = list(map(strip_name, data['Валюта']))
    df['Курс'] = df['Курс'] / df['Единиц'] 

    return df


def get_for_period(fr: date, to: date):
    df = None
    for d in daterange(fr, to):
        c_data = get_currencies(d)
        # c_data['Дата'] = pd.Series([d] * len(c_data.shape()[0]))
        c_data['Дата'] = d

        if df is None:
            df = c_data
        else:
            df = pd.concat([c_data, df])
            stop = 2
            # df.append(c_data)
            # df = df.merge(c_data)

    return df

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)