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

# load CSV file with defintions of columns in the output file
with open('template.csv', 'rb') as tmplfile:
    tmplreader = csv.reader(tmplfile, delimiter=',', quotechar='"', encoding='utf-8')
    hdr = tmplreader.next()
    srcs = tmplreader.next()

with open(args.output, 'wb') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL, encoding='utf-8')
    csvwriter.writerow(hdr)

    cur_bldg = None
    csv_row = [ None ] * len(hdr)
    while True:
        tb_row = c.fetchone()

        if tb_row is None:
            csvwriter.writerow(csv_row)
            break

        if cur_bldg != tb_row[0]:
            if cur_bldg:
                csvwriter.writerow(csv_row)
            csv_row = [ None ] * len(hdr)
            cur_bldg = tb_row[0]

        if tb_row[1] in srcs:
            #print tb_row[1], srcs.index(tb_row[1])
            csv_row[srcs.index(tb_row[1])] = re.sub(r"\n\s{36}..$",'',tb_row[4],re.M)
            #csv_row[srcs.index(tb_row[1])] = tb_row[4]
