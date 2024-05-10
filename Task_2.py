from classes import relative_change_app as rc
from flask import Flask


def main():
    """
    Открывается веб-интерфейс к относительным изменениям курсов.
    Считываются данные для выбранной пользователем страны,
    строится график относительных изменения курса валюты.
    Данные синхронизуются в локальной базе данных 'local_data_base.db'.
    :return:
    """
    app = Flask(__name__)
    app.add_url_rule('/', view_func=rc.Relative_change.as_view('input_form'))
    app.run(debug=False)


if __name__ == '__main__':
    main()
