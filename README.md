reformagkh
==========
Данные с сайта Реформа ЖКХ (http://www.reformagkh.ru) по многоквартирным жилым домам всех регионов РФ и инструмент для их получения/обновления.

**Внимание! Мы не поддерживаем этот набор скриптов и скорее всего они у вас не заработают. Если вам нужны данные - вам сюда: http://data.nextgis.com** Перечень полей (расширяемый) можно увидеть ![здесь](https://docs.google.com/spreadsheets/d/1FvqhdJF5IcQ9hbI_OD2JWdIjimnH_9RIvgjMrJigSg4/edit#gid=1154089007).

## Что это?
* Скрипт-граббер, сохраняет данные в формате CSV и оригиналы страниц.
* Данные выкачанные для Москвы, Омска, Санкт-Петербурга, Екатеринбурга, Владивостока (32, 31, 25, 10, 4 тыс. домов).

## Как запускать

1. Находим идентификатор региона, который нужно скачать. Это может быть любой из уровней, скачиваться будут в т.ч. все подуровни. Идентификатор можно взять или в ![atd.csv](https://github.com/nextgis/reformagkh/blob/master/atd.csv) или непосредственно из ссылки (tid) вида `https://www.reformagkh.ru/myhouse?tid=2208192`.
2. Убеждаемся, что рядом со скриптом присутствует файл atd.csv (его можно либо скачать тут же, либо сделать самому запустив другой скрипт `get_reformagkh_atd.py`)
3. Выполняем шаги 1-4 [отсюда](http://answer-42.livejournal.com/136795.html) 
4. Запускаем скрипт.

ND: Для работы скрипта, кроме Python 2.7.x нужен модуль ![progressbar](https://pypi.python.org/pypi/progressbar)

```bash
pip install progressbar
```

```bash
python get_reformagkh_myhouse.py 2280999 data/housedata.csv -of html
```

![Example3](/img/running.png)

## Таблица с результатами (фрагмент)
![Example1](/img/table.png)

## Веб-карта с результатами
Демо: http://maxim.nextgis.com/resource/644/display
![Example2](/img/map.png)

## TODO

* Поддерживаются не все параметры представленные на основном сайте


License
-------
* Code - GNU GPL v2 or any later version
* Data - unknown, possibly Public Domain

Коммерческая поддержка
----------------------
Нужны исправления или улучшения для парсера РеформыЖКХ? Нужна выгрузка данных? [Свяжитесь с нами](http://nextgis.ru/contact/)!

[![http://nextgis.com](http://nextgis.ru/img/nextgis.png)](http://nextgis.com)

