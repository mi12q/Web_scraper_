from classes import web_app_class as wa
from flask import Flask


def main():
    """
    Открывается веб-интерфейс для считывания данных.
    Считываются данные для выбранной пользователем валюты и диапазона дат.
    Данные синхронизуются в локальной базе данных 'local_data_base.db', в таблице 'ЦБ_currency_rates'.
    :return:
    """
    app = Flask(__name__)
    app.add_url_rule('/', view_func=wa.Input_form.as_view('input_form'))
    app.run(debug=False)


if __name__ == '__main__':
    main()
