from classes import data_base as db
from classes import currencies as curr


def main():
    start_date = '2015-02-01'
    end_date = '2016-02-01'
    data_base = db.DataBase(start_date)
    data_base.set_global_data()
    data_base.set_parameters(curr.currencies.keys())
    data_base.create_relative_change_db(curr.currencies.keys(), start_date, end_date)


if __name__ == '__main__':
    main()
