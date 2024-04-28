import requests
from bs4 import BeautifulSoup
import pandas as pd


class Webscraper:

    def __init__(self):
        self.url = 'https://www.finmarket.ru/currency/rates/?id=10148&pv=1&cur={}&bd={}&bm={}&by={}&ed={}&em={}&ey={' \
                   '}&x=48&y=13#archive'

    def parse_page(self, currency, start_date, end_date):
        dt1 = start_date.split('-')
        dt2 = end_date.split('-')
        currencies = {'ЕВРО': 52170, 'Доллар США': 52148, 'Фунт стерлингов': 52146, 'Японская йена': 52246,
                      'Турецкая лира': 52158, 'Индийская рупия': 52238, 'Китайский юань': 52207}
        self.url = self.url.format(str(currencies[currency]), dt1[2], dt1[1], dt1[1], dt2[2], dt2[1], dt2[0])
        page = requests.get(self.url)
        content = BeautifulSoup(page.content, "html.parser")
        table_of_values = content.find('table', {'class': 'karramba'})
        table = [element.text.strip() for element in table_of_values.find_all('td')]
        df = pd.DataFrame(
            {'Дата': table[::4], 'Количество': table[1:][::4], 'Курс': table[2:][::4], 'Изменение': table[3:][::4]})
        return df


class Global_currencies:
    def __init__(self):
        self.url = 'https://www.iban.ru/currency-codes'

    def parse_page(self):
        page = requests.get(self.url)
        content = BeautifulSoup(page.content, "html.parser")
        table_of_values = content.find('table')
        table = [element.text.strip() for element in table_of_values.find_all('td')]
        df = pd.DataFrame(
            {'Страна': table[::4], 'Валюта': table[1:][::4], 'Код': table[2:][::4], 'Номер': table[3:][::4]})
        return df