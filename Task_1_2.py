from classes import parser_classes as classes


def main():
    scr = classes.Global_currencies()
    scr.parse_page()
    scr.update_data_base()


if __name__ == '__main__':
    main()
