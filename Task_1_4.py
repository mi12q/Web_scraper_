from classes import web_app_class as wa, currencies as curr, parser_classes as parser, data_base as db
from flask import Flask
from classes import currencies as curr
import pandas as pd

def main():
    print(curr.currencies.keys())
    start_date = '2022-02-01'
    end_date = '2022-02-02'
    global_scr = parser.Global_currencies()
    global_scr.parse_page()
    global_scr.update_data_base()
    scraper = parser.Webscraper()

    data_base = db.DataBase(global_scr.get_data())
    for currency in curr.currencies.keys():
        scraper.parse_page(currency, start_date, end_date)
        scraper.update_data_base()
        values = (scraper.get_data().iloc[:1])
        data_base.update_parameters(values)


    # df2 = global_scr.get_data()
    # print(df2)
    # merged_data = pd.merge(scraper.get_data().iloc[1:][['Валюта','Дата','Курс']], data_base.get()[['Страна','Валюта',]],on='Валюта', how="inner")
    # print(merged_data.iloc[:,[3,0,1,2]])

if __name__ == '__main__':
    main()