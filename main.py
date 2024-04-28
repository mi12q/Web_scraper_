import requests
from bs4 import BeautifulSoup
import pandas as pd


url = 'https://www.iban.ru/currency-codes'
page = requests.get(url)
content = BeautifulSoup(page.content, "html.parser")
table_of_values = content.find('table')
table = [element.text.strip() for element in table_of_values.find_all('td')]
df = pd.DataFrame(
    {'Страна': table[::4], 'Валюта': table[1:][::4], 'Код': table[2:][::4], 'Номер': table[3:][::4]})
print(df)