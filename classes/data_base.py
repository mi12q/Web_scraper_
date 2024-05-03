import pandas as pd
from classes import parser_classes as parser, currencies as curr
import sqlite3
from datetime import datetime, timedelta


class DataBase:
    def __init__(self, start_date):
        scr = parser.Global_currencies()
        scr.parse_page()
        self.data = scr.get_data()
        self.start_date = start_date
        self.parameters = None

    def get_parameters(self):
        return self.parameters

    def update_parameters(self, new_data):
        merged_data = pd.merge(new_data[['Валюта', 'Дата', 'Курс']], self.data[['Валюта', 'Страна']], on='Валюта',
                               how="inner").iloc[:, [3, 0, 1, 2]]
        conn = sqlite3.connect('parameters.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parameters (
            Страна TEXT,
            Валюта TEXT,
            Дата DATE,
            Курс NUMERIC
        )
        ''')

        for _, row in merged_data.iterrows():

            cursor.execute('''
                        SELECT EXISTS(
                        SELECT 1
                        FROM parameters
                        WHERE Страна=? AND Валюта=? AND Дата=? AND Курс=?)
                    ''', (row['Страна'], row['Валюта'], row['Дата'], row['Курс']))
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute('''
                    INSERT INTO parameters (Страна, Валюта, Дата,  Курс) 
                    VALUES (?, ?, ?, ?)
                    ''', (row['Страна'], row['Валюта'], row['Дата'], row['Курс']))
                print('Updated parameters')

        self.parameters = pd.read_sql_query("SELECT * FROM parameters", conn)
        conn.commit()
        conn.close()

    def create_parameters_db(self, currency_dict):
        end_date = datetime.strptime(self.start_date, '%Y-%m-%d') + timedelta(days=365)
        end_date = end_date.strftime('%Y-%m-%d')
        scr = parser.Webscraper()
        for currency in currency_dict:
            scr.parse_page(currency, self.start_date, end_date, curr.currencies)
            values = (scr.get_data().iloc[:1])
            if len(values) != 0:
                self.update_parameters(values)

    def update_relative_currency_info(self, new_data):
        merged_data = pd.merge(new_data[['Валюта', 'Дата', 'Курс']], self.data[['Валюта', 'Страна']], on='Валюта',
                               how="inner").iloc[:, [3, 0, 1, 2]]
        conn = sqlite3.connect('currency_relative_change_by_country.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS relative_change (
            Страна TEXT,
            Валюта TEXT,
            Дата DATE,
            Курс NUMERIC,
            Изменение NUMERIC
        )
        ''')
        val = self.parameters
        for _, row in merged_data.iterrows():
            if val.loc[val['Валюта'] == row['Валюта']] is None:
                continue
            str_val = (val.loc[val['Валюта'] == row['Валюта']]['Курс'].iloc[0])
            float_val = float(str_val.replace(',', '.'))
            relative_change = (float_val - float(row['Курс'].replace(',', '.'))) / float(row['Курс'].replace(',', '.'))
            cursor.execute('''
                        SELECT EXISTS(
                        SELECT 1
                        FROM relative_change
                        WHERE Страна=? AND Валюта=? AND Дата=? AND Курс=? AND Изменение=? )
                    ''', (row['Страна'], row['Валюта'], row['Дата'], row['Курс'], relative_change))
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute('''
                    INSERT INTO relative_change (Страна, Валюта, Дата,  Курс, Изменение )
                    VALUES (?, ?, ?, ?, ?)
                    ''', (row['Страна'], row['Валюта'], row['Дата'], row['Курс'], relative_change))
                print('Updated relative change table')

        conn.commit()
        conn.close()

    def create_relative_change_db(self, currency_dict, start_date, end_date):
        scr = parser.Webscraper()
        for currency in currency_dict:
            scr.parse_page(currency, start_date, end_date, curr.currencies)
            values = (scr.get_data())
            self.update_relative_currency_info(values)
