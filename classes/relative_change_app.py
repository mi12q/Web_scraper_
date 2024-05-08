from flask import request, render_template
from flask.views import MethodView
from classes import currencies as curr, data_base as db
from concurrent.futures import ThreadPoolExecutor


class Relative_change(MethodView):

    def get(self):
        return render_template('website_countries.html')

    def post(self):
        sep = ""
        countries = request.form.getlist('countries')
        start_date = sep.join(request.form['start_date'])
        end_date = sep.join(request.form['end_date'])

        print(f"Страны: {', '.join(countries)}", flush=True)
        print(f"Начальная дата: {start_date}", flush=True)
        print(f"Конечная дата: {end_date}", flush=True)

        data_base_instance = db.DataBase('2015-02-01')
        data_base_instance.set_parameters(curr.currencies.keys())
        currency_list = data_base_instance.get_currency_by_country(countries)
        data_base_instance.set_data(currency_list)

        currency_codes = (curr.reversed_dict[currency] for currency in currency_list['Валюта'])
        with ThreadPoolExecutor() as executor:
            threads = list(executor.map(data_base_instance.scrape_and_update, currency_codes,
                                        [start_date] * len(currency_list['Валюта']),
                                        [end_date] * len(currency_list['Валюта'])))
        graph = data_base_instance.plot_data(countries, start_date, end_date)
        return render_template('graph.html', graph_html=graph)
