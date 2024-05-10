from classes import data_base as db
from classes import currencies as curr


def main():
    """
    Считываются данные со страницы для выбранного диапазона дат.
    Данные синхронизуются в локальной базе данных 'local_data_base.db', создаётся таблица параметров 'parameters',
    в отдельной таблице 'relative_change', синхронизуется расчёт относительных изменений курса.
    Диапазон дат взят для примера.
    :return:
    """
    start_date = '2022-02-01'
    end_date = '2024-02-01'
    data_base = db.DataBase(start_date)
    data_base.set_global_data()
    data_base.create_parameters_db(curr.currencies.keys())
    data_base.create_relative_change_db(curr.currencies.keys(), start_date, end_date)


if __name__ == '__main__':
    main()
