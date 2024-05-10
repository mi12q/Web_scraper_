from classes import parser_classes as classes


def main():
    """
    Считывается список валют стран мира со страницы 'https://www.iban.ru/currency-codes'.
    Данные синхронизуются в локальной базе данных 'local_data_base.db', в таблице 'global_currency_info'.
    :return:
    """
    scr = classes.Global_currencies()
    scr.parse_page()
    scr.update_data_base()


if __name__ == '__main__':
    main()
