import pandas as pd
from classes import parser_classes as parser, currencies as curr
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import mpld3


class DataBase:
    def __init__(self, start_date):
        self.data = None
        self.start_date = start_date
        self.parameters = None

    def get_parameters(self):
        return self.parameters

    def set_parameters(self, currency_dict):
        conn = sqlite3.connect('parameters.db')
        cursor = conn.cursor()
        cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS parameters (
            Страна TEXT,
            Валюта TEXT,
            Дата DATE,
            Курс NUMERIC,
            PRIMARY KEY (Страна, Валюта, Дата)
        ) WITHOUT ROWID;
        ''')
        cursor.execute('SELECT 1 FROM parameters LIMIT 1;')
        data = cursor.fetchone()
        if data is None:
            self.create_parameters_db(currency_dict)
        else:
            self.parameters = pd.read_sql_query("SELECT * FROM parameters", conn)

    def set_data(self, data):
        self.data = data

    def set_global_data(self):
        scr = parser.Global_currencies()
        scr.parse_page()
        self.data = scr.get_data()

    def update_parameters(self, new_data):
        merged_data = pd.merge(new_data[['Валюта', 'Дата', 'Курс']], self.data[['Валюта', 'Страна']], on='Валюта',
                               how="inner").iloc[:, [3, 0, 1, 2]]
        merged_data['Дата'] = pd.to_datetime(merged_data['Дата'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
        conn = sqlite3.connect('parameters.db')
        cursor = conn.cursor()

        cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS parameters (
            Страна TEXT,
            Валюта TEXT,
            Дата DATE,
            Курс NUMERIC,
            PRIMARY KEY (Страна, Валюта, Дата)
        ) WITHOUT ROWID;
        ''')

        update_query = '''
        INSERT INTO parameters (Страна, Валюта, Дата, Курс)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(Страна, Валюта, Дата)
        DO UPDATE SET Курс = excluded.Курс
        WHERE Курс != excluded.Курс;
        '''

        data_tuples = list(merged_data.itertuples(index=False, name=None))
        cursor.executemany(update_query, data_tuples)
        self.parameters = pd.read_sql_query("SELECT * FROM parameters", conn)
        conn.commit()
        conn.close()

    def create_parameters_db(self, currency_dict):
        end_date = (datetime.strptime(self.start_date, '%Y-%m-%d') + timedelta(days=365)).strftime('%Y-%m-%d')
        scr = parser.Webscraper()
        data_frames = [scr.parse_page(currency, self.start_date, end_date, curr.currencies) for currency in
                       currency_dict]
        non_empty_data = [df.iloc[:1] for df in data_frames if not df.empty]
        all_data = pd.concat(non_empty_data, ignore_index=True)
        if not all_data.empty:
            self.update_parameters(all_data)

    def update_relative_currency_info(self, new_data):
        merged_data = pd.merge(
            new_data[['Валюта', 'Дата', 'Курс']],
            self.parameters[['Валюта', 'Страна', 'Курс']].rename(columns={'Курс': 'Курс_на_дату'}),
            on=['Валюта'],
            how='inner'
        ).iloc[:, [3, 0, 1, 2, 4]]
        merged_data['Дата'] = pd.to_datetime(merged_data['Дата'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
        change = merged_data.apply(
            lambda row: (float(row['Курс_на_дату'].replace(',', '.')) - float(row['Курс'].replace(',', '.'))) / float(
                row['Курс'].replace(',', '.')) if row['Курс'] != '0' else 0, axis=1)
        change = pd.DataFrame(change)
        change = change[change.columns[0]]
        merged_data = merged_data.drop(columns=['Курс_на_дату'])
        merged_data.insert(4, "Изменение", change, True)
        conn = sqlite3.connect('currency_relative_change_by_country.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS relative_change (
            Страна TEXT,
            Валюта TEXT,
            Дата DATE,
            Курс NUMERIC,
            Изменение NUMERIC,
            PRIMARY KEY (Страна, Валюта, Дата)
        ) WITHOUT ROWID;
        ''')

        update_query = '''
        INSERT INTO relative_change (Страна, Валюта, Дата, Курс, Изменение)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(Страна, Валюта, Дата)
        DO UPDATE SET Курс = excluded.Курс,
                      Изменение = excluded.Изменение
         WHERE Изменение != excluded.Изменение;
        '''

        data_tuples = list(merged_data.itertuples(index=False, name=None))
        cursor.executemany(update_query, data_tuples)
        conn.commit()
        conn.close()

    def create_relative_change_db(self, currency_dict, start_date, end_date):
        scr = parser.Webscraper()
        data_frames = [scr.parse_page(currency, start_date, end_date, curr.currencies) for currency in
                       currency_dict]
        non_empty_data = [df for df in data_frames if not df.empty]
        all_data = pd.concat(non_empty_data, ignore_index=True)
        if not all_data.empty:
            self.update_relative_currency_info(all_data)

    def plot_data(self, country_list, start_date, end_date):
        conn = sqlite3.connect('currency_relative_change_by_country.db')
        country_placeholders = ','.join(['?'] * len(country_list))
        query = f"""
                SELECT Страна, Валюта, Дата, Курс, Изменение
                FROM relative_change
                WHERE
                    Страна IN ({country_placeholders})
                    AND
                    Дата BETWEEN DATE(?) AND DATE(?)
                ORDER BY Страна, Дата;
            """

        df = pd.read_sql_query(query, conn, params=country_list + [start_date, end_date])
        conn.close()
        df['Дата'] = pd.to_datetime(df['Дата'])
        print(df)
        filtered_df = df[
            (df['Страна'].isin(country_list)) &
            (df['Дата'] >= start_date) &
            (df['Дата'] <= end_date)
            ]

        new_df = filtered_df.pivot(index='Дата', columns='Страна', values='Изменение')
        fig, ax = plt.subplots()
        new_df.plot(figsize=(15, 10), ax=ax)
        plt.minorticks_on()
        plt.grid(which='major',
                 color='grey',
                 linewidth=0.7)
        plt.grid(which='minor',
                 color='grey',
                 linestyle=':')
        ax.set_title('Относительное изменение курса валют выбранных стран')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Изменение курса валюти')
        ax.legend()
        plt.savefig('currency_graph.png')
        mpld3_html = mpld3.fig_to_html(fig)
        plt.close()
        return mpld3_html

    def get_currency_by_country(self, country_list):
        conn = sqlite3.connect('parameters.db')
        country_placeholders = ','.join(['?'] * len(country_list))
        query = f"""
                    SELECT Страна, Валюта
                    FROM parameters
                    WHERE Страна IN ({country_placeholders});
                """
        df = pd.read_sql_query(query, conn, params=country_list)
        conn.close()
        return df

    def scrape_and_update(self, currency, start_date, end_date):
        scr = parser.Webscraper()
        scr.parse_page(currency, start_date, end_date, curr.currencies)
        data = scr.get_data()
        self.update_relative_currency_info(data)
        print(scr.get_url())