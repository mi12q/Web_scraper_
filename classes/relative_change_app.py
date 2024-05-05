from flask import request, render_template
from flask.views import MethodView
from classes import parser_classes as parser, currencies as curr, data_base as db
import sqlite3

class Relative_change(MethodView):

    def get(self):
        return render_template('website_countries.html')

    def post(self):
        sep = ""
        countries = request.form.getlist('countries')
        start_date = request.form['start_date']
        start_date = sep.join(start_date)
        end_date = request.form['end_date']
        end_date = sep.join(end_date)

        print("Страны:", ', '.join(countries), flush=True)
        print("Начальная дата:", start_date, flush=True)
        print("Конечная дата:", end_date, flush=True)

        data_base = db.DataBase('2022-02-01')
        data_base.set_parameters(curr.currencies.keys())
        currency_list = data_base.get_currency_by_country(countries)
        data_base.set_data(currency_list)
        print(currency_list)
        scr = parser.Webscraper()
        for currency in currency_list['Валюта']:
            code = next((k for k, v in curr.currencies.items() if v == currency), None)
            scr.parse_page(code,start_date,end_date,curr.currencies)
            data_base.update_relative_currency_info(scr.get_data())
        graph = data_base.plot_data(countries, start_date, end_date)

        return render_template('graph.html', graph_html=graph)
