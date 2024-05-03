import pandas as pd
from classes import parser_classes as parser
import sqlite3


class DataBase:
    def __init__(self, data):
        self.data = data

    def get(self):
        return(self.data)

    def update_parameters(self, new_data):
        merged_data = pd.merge(new_data[['Валюта','Дата','Курс']], self.data[['Валюта','Страна']],on='Валюта', how="inner").iloc[:,[3,0,1,2]]
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

        conn.commit()
        conn.close()