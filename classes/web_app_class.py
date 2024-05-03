from flask import Flask, request, render_template
from flask.views import MethodView
from classes import parser_classes as classes


class Input_form(MethodView):

    def get(self):
        return render_template('website.html')

    def post(self):
        sep = ""
        currency = request.form['currency']
        currency = sep.join(currency)
        start_date = request.form['start_date']
        start_date = sep.join(start_date)
        end_date = request.form['end_date']
        end_date = sep.join(end_date)

        print("Валюта:", currency, flush=True)
        print("Начальная дата:", start_date, flush=True)
        print("Конечная дата:", end_date, flush=True)

        scraper = classes.Webscraper()
        scraper.parse_page(currency, start_date, end_date)
        scraper.update_data_base()
        print(scraper.get_url())
        df = scraper.get_data()
        df_html = df.to_html(index=False)
        print(df)

        return render_template('data.html', table=df_html)

