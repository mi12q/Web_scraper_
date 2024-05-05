from classes import data_base as db
from classes import currencies as curr
from classes import relative_change_app as rc
from flask import Flask


# def main():
    # data_base = db.DataBase('2022-02-01')
    # start_date = '2022-01-01'
    # end_date = '2022-05-16'
    # countries = ['Чехия', 'США']
    # data_base.plot_data(countries, start_date, end_date)

def main():
    app = Flask(__name__)
    app.add_url_rule('/', view_func=rc.Relative_change.as_view('template'))
    app.run(debug=False)

if __name__ == '__main__':
    main()
