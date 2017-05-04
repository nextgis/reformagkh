#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

#
# converts sqlites database into CSV format using given specification
#

import argparse
import unicodecsv as csv
import sqlite3
import re

parser = argparse.ArgumentParser()
parser.add_argument('input', help='sqlite file for import')
parser.add_argument('output', help='CSV file for output')
args = parser.parse_args()

conn = sqlite3.connect(args.input)
c = conn.cursor()
c.execute('SELECT * FROM attrvals')

nodata_values = [u'Не заполнено', u'Не присвоен', u'Нет данных', u'-', u'Не определен', u'не присвоен', u'данные отсутствуют', u'не определен', u'без номера', u'не определён']

# load CSV file with defintions of columns in the output file
with open('template.csv', 'rb') as tmplfile:
    tmplreader = csv.reader(tmplfile, delimiter=',', quotechar='"', encoding='utf-8')
    hdr = tmplreader.next()
    srcs = tmplreader.next()

def record_csv():
    global csv_row
    csv_row[hdr.index('LatLong')] = "%s,%s" % (lat, lon)
    csvwriter.writerow(csv_row)
    csv_row = [ None ] * len(hdr)

with open(args.output, 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL, encoding='utf-8')
    csvwriter.writerow(hdr)

    cur_bldg = None
    csv_row = [ None ] * len(hdr)

    while True:
        tb_row = c.fetchone()

        # the last database row
        if tb_row is None:
            record_csv()
            break

        if cur_bldg != tb_row[0]:
            if cur_bldg:
                record_csv()
            cur_bldg = tb_row[0]

        # known rows
        if tb_row[1] in srcs:
            try:
                # do nothing if values is in nodata values
                nodata_values.index(tb_row[4])
            except ValueError:
                # remove gabage from the end of some strings
                csv_row[srcs.index(tb_row[1])] = re.sub(r"\n\s{36}..$",'',tb_row[4],re.M)

        # special rows
        if tb_row[1] == 'lon':
            lon = tb_row[4]
        if tb_row[1] == 'lat':
            lat = tb_row[4]
