import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3


class Webscraper:

    def __init__(self):
        """
        :param url: - шаблон ссылки
        :param data: - данные полученные со страницы
        :param updated_url: - ссылка на сайт, с выбранной валютой и диапазоном дат
        """
        self.url = 'https://www.finmarket.ru/currency/rates/?id=10148&pv=1&cur={}&bd={}&bm={}&by={}&ed={}&em={}&ey={' \
                   '}&x=48&y=13#archive'
        self.data = None
        self.updated_url = None

    def get_data(self):
        """

        :return: - возвращает поле data
        """
        return self.data

    def get_url(self):
        """

        :return: - возвращает поле updated_url
        """
        return self.updated_url

    def parse_page(self, currency, start_date, end_date, currencies):
        """
        Считывает курсы валют за выбранный диапазон со страницы.
        :param currency: - валюта
        :param start_date: - начальная дата
        :param end_date: - конечная дата
        :param currencies: - словарь всех валют
        :return: - возрашает поле data
        """
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
        """
        Обновляет базу данных новыми данными.
        :return:
        """
        conn = sqlite3.connect('ЦБ_currency_data.db')
        cursor = conn.cursor()
        df = self.data.copy()
        df['Дата'] = pd.to_datetime(df['Дата'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ЦБ_currency_rates (
            Валюта TEXT,
            Дата DATE,
            Количество INTEGER,
            Курс NUMERIC,
            Изменение NUMERIC,
            UNIQUE(Валюта, Дата)  
        )
        ''')

        update_query = '''
        INSERT INTO ЦБ_currency_rates (Валюта, Дата, Количество, Курс, Изменение )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(Валюта, Дата)
        DO UPDATE SET Количество = excluded.Количество,
                    Курс = excluded.Курс,
                    Изменение = excluded.Изменение
         WHERE Количество != excluded.Количество OR Изменение != excluded.Изменение OR Курс!= excluded.Курс;
        '''

        data_tuples = list(df.itertuples(index=False, name=None))
        cursor.executemany(update_query, data_tuples)
        conn.commit()
        conn.close()


class Global_currencies:
    def __init__(self):
        """
        :param url: - ссылка на страницу
        :param data: - данные полученные со страницы
        """
        self.url = 'https://www.iban.ru/currency-codes'
        self.data = None

    def get_data(self):
        """

        :return: - возвращает поле data
        """
        return self.data

    def parse_page(self):
        """
        Считывает данные со страницы.
        :return:
        """
        page = requests.get(self.url)
        content = BeautifulSoup(page.content, "html.parser")
        table_of_values = content.find('table')
        table = [element.text.strip() for element in table_of_values.find_all('td')]
        df = pd.DataFrame(
            {'Страна': table[::4], 'Валюта': table[1:][::4], 'Код': table[2:][::4], 'Номер': table[3:][::4]})
        self.data = df
        return self.data

    def update_data_base(self):
        """
        Обновляет базу данных новыми данными.
        :return:
        """
        conn = sqlite3.connect('global_currency_data.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_currency_info (
            Страна TEXT PRIMARY KEY,
            Валюта TEXT,
            Код TEXT,
            Номер INTEGER
        )
        ''')

        update_query = '''
        INSERT INTO global_currency_info (Страна, Валюта, Код, Номер)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(Страна)
        DO UPDATE SET Валюта = excluded.Валюта,
                    Код = excluded.Код,
                    Номер = excluded.Номер
         WHERE Валюта != excluded.Валюта OR Код != excluded.Код OR Номер!= excluded.Номер;
        '''

        data_tuples = list(self.data.itertuples(index=False, name=None))
        cursor.executemany(update_query, data_tuples)
        conn.commit()
        conn.close()
