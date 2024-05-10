from flask import request, render_template
from flask.views import MethodView
from classes import parser_classes as classes, currencies as curr


class Input_form(MethodView):

    @staticmethod
    def get():
        """

        :return: - возвращает готовый шаблон веб-интерфейса для считывания данных.
        """
        return render_template('website.html')

    @staticmethod
    def post():
        """
        Получает выбранную пользователем валюту и диапазон, считываются данные со страницы для выбранных параметров.
        :return: - возвращает шаблон страницы, содержащий таблицу полученных данных.
        """
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
        scraper.parse_page(currency, start_date, end_date, curr.currencies)
        scraper.update_data_base()
        print(scraper.get_url())
        df = scraper.get_data()
        df_html = df.iloc[:, 1:].to_html(index=False)
        print(df)

        return render_template('data.html', table=df_html, title=curr.currencies[currency])
