reformagkh
==========
Данные с сайта Реформа ЖКХ (http://www.reformagkh.ru) по многоквартирным жилым домам всех регионов РФ и инструмент для их получения/обновления.

##Что это?
* Скрипт-граббер, сохраняет данные в формате CSV и оригиналы страниц.
* Данные выкачанные для Москвы, Омска, Санкт-Петербурга (32, 31 и 25 тыс. домов).

##Как запускать

1. Находим идентификатор региона, который нужно скачать. Это может быть любой из уровней, скачиваться будут в т.ч. все подуровни. Идентификатор можно взять или в ![atd.csv](https://github.com/nextgis/reformagkh/blob/master/atd.csv) или непосредственно из ссылки (tid), ![например](https://www.reformagkh.ru/myhouse?tid=2208192).
2. Убеждаемся, что рядом со скриптом присутствует файл atd.csv (его можно либо скачать тут же, либо сделать самому запустив другой скрипт `get_reformagkh_atd.py`)
3. Выполняем шаги 1-4 [отсюда](http://answer-42.livejournal.com/136795.html) 
4. Запускаем скрипт.

ND: Для работы скрипта, кроме Python 2.7.x нужен модуль ![progressbar](https://pypi.python.org/pypi/progressbar)

```bash
pip install progressbar
```

```bash
python get_reformagkh_data-v3.py 2280999 data/housedata.csv -of html
```

![Example3](/img/running.png)

##Таблица с результатами (фрагмент)
![Example1](/img/table.png)

##Веб-карта с результатами
Демо: http://demo.nextgis.ru/ngw/resource/243/display
![Example2](/img/map.png)

##TODO

* Пока поддерживаются не все параметры представленные на основном сайте


License
-------------
* Code - GNU GPL v2 or any later version
* Data - unknown, possibly Public Domain

Commercial support
----------
Нужны исправления или улучшения для парсера РеформыЖКХ? We provide custom development and support for this software. [Contact us](http://nextgis.ru/contact/) to discuss options!

[![http://nextgis.com](http://nextgis.ru/img/nextgis.png)](http://nextgis.com)

