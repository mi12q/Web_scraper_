import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3


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

    def parse_page(self, currency, start_date, end_date):
        dt1 = start_date.split('-')
        dt2 = end_date.split('-')
        currencies = {'52148': 'Доллар США', '52170': 'Евро', '52146': 'Фунт стерлингов', '52133': 'Швейцарский франк',
                      '52182': 'Австралийский доллар', '52180': 'Азербайджанский манат', '52187': 'Армянский драм',
                      '52200': 'Белорусский рубль', '52197': 'Болгарский лев', '52174': 'Бразильский реал',
                      '52236': 'Венгерский форинт', '52073': 'Вона Республики Корея', '52124': 'Вьетнамский донг',
                      '52235': 'Гонконгский доллар', '52172': 'Грузинский лари', '52215': 'Датская крона',
                      '52139': 'Дирхам ОАЭ', '52145': 'Египетский фунт', '52238': 'Индийская рупия',
                      '52239': 'Индонезийская рупия', '52247': 'Казахстанский тенге', '52202': 'Канадский доллар',
                      '52115': 'Катарский риал', '52075': 'Киргизский сом', '52207': 'Китайский юань Жэньминьби',
                      '52079': 'Латвийский лат', '52082': 'Литовский лит', '52093': 'Молдавский лей',
                      '52103': 'Новозеландский доллар', '52141': 'Новый туркменский манат', '52106': 'Норвежская крона',
                      '52173': 'Польский злотый', '52157': 'Румынский лей', '52164': 'СДР (спец. прав заим-я)',
                      '52178': 'Сербский динар', '52122': 'Сингапурский доллар', '52168': 'Таджикский сомони',
                      '52136': 'Тайландский бат', '52158': 'Турецкая лира', '52150': 'Узбекский сум',
                      '52171': 'Украинская гривна', '52214': 'Чешская крона', '52132': 'Шведская крона',
                      '52220': 'Эстонская крона', '52127': 'Южноафриканский рэнд', '52246': 'Японская йена'}
        self.updated_url = self.url.format(currency, dt1[2], dt1[1], dt1[0], dt2[2], dt2[1], dt2[0])
        page = requests.get(self.updated_url)
        content = BeautifulSoup(page.content, "html.parser")
        table_of_values = content.find('table', {'class': 'karramba'})
        table = [element.text.strip() for element in table_of_values.find_all('td')]
        df = pd.DataFrame(
            {'Валюта': currencies[currency], 'Дата': table[::4], 'Количество': table[1:][::4], 'Курс': table[2:][::4],
             'Изменение': table[3:][::4]})
        self.data = df

    def update_data_base(self):
        conn = sqlite3.connect('../ЦБ_currency_data.db')
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

            cursor.execute('''
                    SELECT COUNT(*) 
                    FROM ЦБ_currency_rates
                    WHERE Валюта=? AND Дата=? AND Количество=? AND Курс=? AND Изменение=?
                ''', (row['Валюта'], row['Дата'], row['Количество'], row['Курс'], row['Изменение']))

            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute('''
                        INSERT INTO ЦБ_currency_rates (Валюта, Дата, Количество, Курс, Изменение) 
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(Валюта, Дата) DO UPDATE SET 
                        Количество=excluded.Количество,
                        Курс=excluded.Курс,
                        Изменение=excluded.Изменение
                    ''', (row['Валюта'], row['Дата'], row['Количество'], row['Курс'], row['Изменение']))

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
        conn = sqlite3.connect('../global_currency_data.db')
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
