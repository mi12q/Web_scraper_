from classes import relative_change_app as rc
from flask import Flask


def main():
    app = Flask(__name__)
    app.add_url_rule('/', view_func=rc.Relative_change.as_view('template'))
    app.run(debug=False)


if __name__ == '__main__':
    main()
