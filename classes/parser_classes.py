import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from datetime import datetime

class Webscraper:

    def __init__(self):
        self.url = 'https://www.finmarket.ru/currency/rates/?id=10148&pv=1&cur={}&bd={}&bm={}&by={}&ed={}&em={}&ey={' \
                   '}&x=48&y=13#archive'
        self.data = None
        self.updated_url = None

    def get_data(self):
        return self.data

    def get_url(self):
        return self.updated_url

    def parse_page(self, currency, start_date, end_date, currencies):
        dt1 = start_date.split('-')
        dt2 = end_date.split('-')
        self.updated_url = self.url.format(currency, dt1[2], dt1[1], dt1[0], dt2[2], dt2[1], dt2[0])
        page = requests.get(self.updated_url)
        content = BeautifulSoup(page.content, "html.parser")
        table_of_values = content.find('table', {'class': 'karramba'})
        table = [element.text.strip() for element in table_of_values.find_all('td')]
        df = pd.DataFrame(
            {'Валюта': currencies[currency], 'Дата': table[::4], 'Количество': table[1:][::4], 'Курс': table[2:][::4],
             'Изменение': table[3:][::4]})
        self.data = df
        return self.data

    def update_data_base(self):
        conn = sqlite3.connect('ЦБ_currency_data.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ЦБ_currency_rates (
            Валюта TEXT,
            Дата DATE,
            Количество INTEGER,
            Курс NUMERIC,
            Изменение NUMERIC,
            UNIQUE(Дата, Валюта)  
        )
        ''')

        for _, row in self.data.iterrows():
            data = datetime.strptime(row['Дата'], '%d.%m.%Y').strftime('%Y-%m-%d')
            cursor.execute('''
                    SELECT COUNT(*) 
                    FROM ЦБ_currency_rates
                    WHERE Валюта=? AND Дата=? AND Количество=? AND Курс=? AND Изменение=?
                ''', (row['Валюта'], data, row['Количество'], row['Курс'], row['Изменение']))

            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute('''
                        INSERT INTO ЦБ_currency_rates (Валюта, Дата, Количество, Курс, Изменение) 
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(Валюта, Дата) DO UPDATE SET 
                        Количество=excluded.Количество,
                        Курс=excluded.Курс,
                        Изменение=excluded.Изменение
                    ''', (row['Валюта'], data, row['Количество'], row['Курс'], row['Изменение']))

        conn.commit()
        conn.close()


class Global_currencies:
    def __init__(self):
        self.url = 'https://www.iban.ru/currency-codes'
        self.data = None

    def get_data(self):
        return self.data

    def parse_page(self):
        page = requests.get(self.url)
        content = BeautifulSoup(page.content, "html.parser")
        table_of_values = content.find('table')
        table = [element.text.strip() for element in table_of_values.find_all('td')]
        df = pd.DataFrame(
            {'Страна': table[::4], 'Валюта': table[1:][::4], 'Код': table[2:][::4], 'Номер': table[3:][::4]})
        self.data = df

    def update_data_base(self):
        conn = sqlite3.connect('global_currency_data.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_currency_info (
            Страна TEXT,
            Валюта TEXT,
            Код TEXT,
            Номер INTEGER
        )
        ''')

        for _, row in self.data.iterrows():

            cursor.execute('''
                    SELECT EXISTS(
                    SELECT 1
                    FROM global_currency_info
                    WHERE Страна=? AND Валюта=? AND Код=? AND Номер=? )
                ''', (row['Страна'], row['Валюта'], row['Код'], row['Номер']))
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute('''
                INSERT INTO global_currency_info (Страна, Валюта, Код, Номер) 
                VALUES (?, ?, ?, ?)
                ''', (row['Страна'], row['Валюта'], row['Код'], row['Номер']))
                print('updated')

        conn.commit()
        conn.close()
