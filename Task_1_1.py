from classes import web_app_class as wa
from flask import Flask


def main():
    app = Flask(__name__)
    app.add_url_rule('/', view_func=wa.Input_form.as_view('input_form'))
    app.run(debug=False)


if __name__ == '__main__':
    main()
