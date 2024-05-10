# Web scraping app with interface
* ### Task_1_1.py
  * Открывается веб-интерфейс для считывания данных.
    * ![2024-05-05_17-18-35](https://github.com/mi12q/Web_scraper_/assets/94108357/f9ce5a46-bcf5-450a-a71f-cb11f17889a6)
  * Считываются данные для выбранной пользователем валюты и диапазона дат.
     * ![2024-05-10_16-54-29](https://github.com/mi12q/Web_scraper_/assets/94108357/844c0c12-7455-4e8a-b9dd-1c705ddf52d3)
  * Данные синхронизуются в локальной базе данных 'local_data_base.db', в таблице 'ЦБ_currency_rates'.
* ### Task_1_2.py
  * Считывается список валют стран мира со страницы 'https://www.iban.ru/currency-codes'.
  * Данные синхронизуются в локальной базе данных 'local_data_base.db', в таблице 'global_currency_info'.
* ### Task_1_4.py
  * Считываются данные со страницы для выбранного диапазона дат.
  * Данные синхронизуются в локальной базе данных 'local_data_base.db'.
  * Создаётся таблица параметров 'parameters'.
  * В отдельной таблице 'relative_change', синхронизуется расчёт относительных изменений курса.
  * Диапазон дат в программе взят для примера.
* ### Task_2.py
  * Открывается веб-интерфейс к относительным изменениям курсов.
    * ![2024-05-05_17-22-30](https://github.com/mi12q/Web_scraper_/assets/94108357/0d9d002a-95d7-4368-b52a-225aa5345b94)
  * Считываются данные для выбранной пользователем страны.
  * Строится график относительных изменений курса валюты.
    * ![2024-05-05_17-26-44](https://github.com/mi12q/Web_scraper_/assets/94108357/252c8846-94a9-4379-a034-7e65aa3d9b24)
