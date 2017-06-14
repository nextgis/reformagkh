#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

#******************************************************************************
#
# get_reformagkh_data-v2.py
# ---------------------------------------------------------
# Grab reformagkh.ru data on buildings, put it in the CSV table.
# More: https://github.com/nextgis/reformagkh
#
# Usage:
#      usage: get_reformagkh_data-v2.py [-h] [-o ORIGINALS_FOLDER] id output_name
#      where:
#           -h           show this help message and exit
#           id           Region ID
#           -o,overwrite Overwite all, will write over previously downloaded files
#           output_name  Where to store the results (path to CSV file)
#           -of ORIGINALS_FOLDER  Folder to save original html files. Skip saving if empty.
#           --cache_only only parse cache, do not touch the web site
#           --no_tor do not use tor, connect to the site directly
#           --extractor EXTRACTOR specify which data extractor to use:
#               none -- do not use any data extractor, only read/download pages
#               original -- use data extractor from the original project (limited set of variables, default)
#               attrlist -- use data extractor and attribute list loaded from tsv file
#           --outputformat FORMAT specify output format
#               csv -- CSV (default)
#               sqlite -- sqlite database (only implemented for attrlist data extractor)
#               pg --
#           --reload_list reload list of the buildings from the site even if cache file exixts
# Examples:
#      python get_reformagkh_data-v2.py 2280999 data/housedata2.csv -o html_orig
#      python get_reformagkh_data-all.py 2291922 housedata.csv -of omsk --no_tor --cache_only
#
# to use with Anaconda do once after installing python 2.7 as py27:
#     source activate py27
#
# Copyright (C) 2014-2016 Maxim Dubinin (sim@gis-lab.info)
# Created: 18.03.2014
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
# to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#
#******************************************************************************

from bs4 import BeautifulSoup
import urllib2
import csv
#from progressbar import *
from httplib import BadStatusLine,IncompleteRead
import socket
import argparse
from collections import namedtuple
from time import sleep
import requesocks
from stem import Signal
from stem.control import Controller
# module to serialize/deserialize object on the disk
import pickle
import shutil
import datetime
import re
import editdistance
import sqlite3
import psycopg2 # TODO: must load on demand
import psycopg2.extras
import time
#from pytest import attrlist

# some installs need this
import os, glob
import sys
import random

parser = argparse.ArgumentParser()
parser.add_argument('id', help='Region (default) or house ID')
parser.add_argument('output_name', help='Where to store the results (path to output file or database URI)')
parser.add_argument('-of','--originals_folder', help='Folder to save original html files. Skip saving if empty.')
parser.add_argument('--no_tor', help='Do not use tor connection', action="store_true")
parser.add_argument('--cache_only', help='Do not connect to the web site, use only cached entries', action="store_true")
parser.add_argument('--extractor', help='Data extractor to use', default='original', choices=['original', 'attrlist', 'none'])
parser.add_argument('--parser', help='HTML Parser to use', default='html.parser', choices=['html.parser', 'lxml'])
parser.add_argument('--outputformat', help='output format', default='csv', choices=['csv', 'sqlite', 'pg'])
parser.add_argument('--outputmode', help='output mode', default='append', choices=['append', 'overwrite'])
parser.add_argument('--reload_list', help='reload list of the buildings even if cache file exixts', action="store_true")
parser.add_argument('--shuffle', help='shuffle list of the buildings', action="store_true")
parser.add_argument('--fast_check', help='do not check for captcha, etc. in cahced files', action="store_true")
parser.add_argument('--attrlist', help='The list of attributes with selectors to be extracted from HTML', default='attrlist.tsv')
parser.add_argument('--houseid', help='provided id will be understood as house_id (single page will be processed)', action="store_true")
parser.add_argument('--allfiles', help='process all files in the cache', action="store_true")
#parser.add_argument('--socks_port', help='Tor sock port to connect to', default='9150')
#parser.add_argument('--torctl_port', help='Tor control port to connect to', default='9151')
args = parser.parse_args()
dirsep = '/' if not os.name == 'nt' else '\\'

# check if arguments make sense
if args.originals_folder:
    if not args.originals_folder.endswith(dirsep): args.originals_folder = args.originals_folder + dirsep
    if not os.path.exists(args.originals_folder): os.mkdir(args.originals_folder)
    region_name = args.originals_folder[:-1]
if args.cache_only:
    if not args.originals_folder:
        print 'cache-only requested but originals folder was not specified, quitting...'
        sys.exit(-1)
    if args.reload_list:
        print '--cache_only and --reload_list cannot be used together'
        sys.exit(-1)
    if args.no_tor:
        print 'with cache_only no_tor has no effect'
    else:
        args.no_tor = True
if args.outputformat == 'sqlite' and args.extractor == 'original':
        print 'sqlite outputformat works only for attrlist data extractor'
        sys.exit(-1)
if args.extractor == 'none' and args.outputformat != 'csv':
    print 'outputformat has no effect when extractor=none'
if args.fast_check and args.extractor != 'none':
    print 'fast_check only allowed when extractor=none'
    sys.exit(5)
if args.allfiles and not args.cache_only:
    print '--allfiles imply --cache_only'
    args.cache_only = True

def console_out(text):
    #write httplib error messages to console
    time_current = datetime.datetime.now()
    timestamp = time_current.strftime('%Y-%m-%d %H:%M:%S')

    f_errors.write(timestamp + ': '+ text)

def get_content(link):
    numtries = 5
    timeoutvalue = 40

    # this function should never be called if no_cache is specified
    assert not args.cache_only

    start_time = time.time()
    if args.no_tor:
        print('Directly retrieving ' + link)
        live_url = urllib2.urlopen(link)#, timeout=300)
        res = live_url.read()
    else:
        for i in range(1,numtries+1):
            try:
                print 'TOR Retrieving', link, 'attempt', i, 'of', numtries
                res = session.get(link).text # need timeout=300 here but it does not work really
            except:
                time.sleep(3)
                res = ''
            else:
                break

    elapsed_time = time.time() - start_time
    if res:
        print 'Page', link, ' retrieved at %s' % datetime.datetime.now(), 'in', elapsed_time, 's'
    else:
        print 'Failed to retrieve', link, 'after', elapsed_time, 's'

    return res

def urlopen_house(link,id):
    #fetch html data on a house

    res = get_content(link)
    if args.originals_folder:
        f = open(args.originals_folder + id + ".html","wb")
        f.write(res.encode('utf-8'))  #writing in utf-8 causes exceptions.UnicodeDecodeError
        f.close()
        print 'Page', link, 'saved in', args.originals_folder + id + '.html size=', os.path.getsize(args.originals_folder + id + ".html")

    return res

def change_proxy():
    with Controller.from_port(port = 9151) as controller:
            controller.authenticate(password="password")
            controller.signal(Signal.NEWNYM)

def extract_value(tr):
    #extract value for general attributes
    res = tr.findAll('td')[1].text.strip()

    return res

def extract_subvalue(tr,num):
    #extract value for general attributes
    res = tr.findAll('tr')[num].text.strip()

    return res

def check_size(link):

    res = get_content(link)
    soup = BeautifulSoup(''.join(res), args.parser)
    captcha = check_captcha(soup)

    while captcha == True:
        res = get_content(link)
        soup = BeautifulSoup(''.join(res), args.parser)
        captcha = check_captcha(soup)
        change_proxy()

    divs = soup.findAll('div', { 'class' : 'clearfix' })
    # TODO: check if this is a right page
    table = divs[1].find('table', { 'class' : 'col_list' })
    size = table.findAll('td')[3].text.replace(u' ед.','').replace(' ','')

    return size

def get_house_list(link):
    size = check_size(link)
    if size == 0: size = check_size(link)

    pages = (int(size) / 10000) + 1

    houses_ids = []
    for page in range(1,pages+1):
        res = get_content(link + '&page=' + str(page) + '&limit=10000')
        soup = BeautifulSoup(''.join(res), args.parser)
        captcha = check_captcha(soup)

        while captcha == True:
            if args.no_tor:
                print "Captcha received: the limit of connections was likely exceeded, quitting"
                sys.exit(-1)
            res = get_content(link + '&page=' + str(page) + '&limit=10000')
            soup = BeautifulSoup(''.join(res), args.parser)
            captcha = check_captcha(soup)
            change_proxy()

        tds = soup.findAll('td')
        for td in tds:
            if td.find('a') is not None:
                if td.find('a').has_attr('href') and 'myhouse' in td.find('a')['href']:
                    house_id = td.find('a')['href'].split('/')[4]
                    houses_ids.append(house_id)

    return houses_ids

def get_data_links(id):
    f_atd = open('atd.csv','rb')
    csvreader = csv.reader(f_atd, delimiter=',')
    regs = []
    for row in csvreader:
        if id in row:
            r = region(row[0],row[1],row[2],row[3],row[4],row[5])
            regs.append(r)

    return regs

def check_captcha(soup):
    captcha = soup.find('form', { 'name' : 'request_limiter_captcha'})
    if captcha != None or u'Каптча' in soup.text or 'captcha' in str(soup):
        return True
    else:
        return False

def mk_cache_file_name(house_id):
    return args.originals_folder + '/' + house_id + ".html"

def invalidate_cache(house_id):
    cache_fname = mk_cache_file_name(house_id)
    if os.path.isfile(cache_fname):
        os.remove(cache_fname)

def load_bldg_page(link,house_id):
    """Loads HTML page for a spceified building either from the web or from cache
    returns the page, False on failure, and the source of the page (web, file, None for failure)"""

    if args.originals_folder:
        cache_fname = mk_cache_file_name(house_id)
        bldg_link = link + 'view/' + house_id
        if not os.path.isfile(cache_fname):
            if args.cache_only:
                print 'Cache file', cache_fname, 'does not exist, skipping...'
                res = False
                src = None
            else:
                src = 'web'
                try:
                    res = urlopen_house(bldg_link, house_id)
                except:
                    print "Error retrieving", bldg_link, ": ", sys.exc_info()[0]
                    f_errors.write(bldg_link + '\n')
                    res = False
        else:
            src = 'file'
            res = open(cache_fname,'rb').read()
            print house_id, ': loaded from cache file', cache_fname
    else:
        try:
            src = 'web'
            res = urlopen_house(bldg_link, house_id)
        except:
            f_errors.write(bldg_link + '\n')
            res = False

    return res, src

def get_housedata(link,house_id,lvl1_name,lvl1_id,lvl2_name,lvl2_id):
    """Tries hard to retrieve the page content one way or another,
    then checks for errors, changes relay if needed, etc."""

    if args.fast_check and os.path.exists(mk_cache_file_name(house_id)):
        print house_id, 'in cache, checks skipped'
        return True

    captcha_count = 0
    while True:
        res, src = load_bldg_page(link,house_id)

        if res == False:
            return False

        soup = BeautifulSoup(''.join(res),args.parser)
        f_ids.write(link + 'view/' + house_id + ',' + house_id + '\n')

        if len(soup) == 0:
            print house_id, ': 0 size html'
            if src == 'web':
                return False
            else:
                invalidate_cache(house_id)
                continue

        if 'Time-out' in soup.text:
            print house_id, ': Time out reported by server'
            return False
        if '502 Bad Gateway' in soup.text:
            print house_id, ': Bad gateway'
            return False
        if u'Ð¢ÐµÑÐ½Ð¸ÑÐµÑÐºÐ¸Ðµ ÑÐ°Ð±Ð¾ÑÑ' in soup.text:
            print house_id, ': maintenance'
            if src == 'web':
                print 'The site is in the maintenance mode, quiting...'
                sys.exit(-1)
            else:
                if args.cache_only:
                    return False
                else:
                    invalidate_cache(house_id)
                    continue

        if u'Реформа ЖКХ Ошибка' in soup.text:
            if args.cache_only:
                print house_id, ': unspecified error page in cache, skipping'
                return False
            else:
                print 'Unrecorgnized error page, the site may be mufunctioning, quitting...'
                print 'TODO: check if this error page is transient, modify code accordingly'
                print 'You may have to remove cached page for building ', house_id
                sys.exit(-1)

        if check_captcha(soup):
            if args.cache_only:
                print house_id, ': captcha page in cache, skipping'
                return False
            elif args.no_tor:
                print house_id, ': captcha received, running without tor, quitting...'
                sys.exit(2)
            else:
                invalidate_cache(house_id)
                if src == 'web':
                    print house_id, ': captcha received, invalidating cache, requesting new proxy, attempt #', captcha_count, 'sleep 60s'
                    change_proxy()
                    time.sleep( 60 )
                    captcha_count += 1
                else:
                    print house_id, ': captcha in cached file, invalidating'
                    if args.cache_only:
                        print "\tprocessing skipped because of --cahe_only"
                    else:
                        print "\trequesting page from the site"
                continue
                #return False # leave house_id unprocessed

        if args.extractor == 'original':
            return parse_house_page_original(soup)
        elif args.extractor == 'attrlist':
            return parse_house_page_attrlist(soup)
        else:
            print house_id, ': data extraction skipped'
            return True

def parse_house_page_original(soup):
    address = soup.find('span', { 'class' : 'float-left loc_name_ohl width650 word-wrap-break-word' }).text.strip()

    #GENERAL
    div = soup.find('div', { 'class' : 'fr' })
    tables = div.findAll('table')
    table0 = tables[0]
    trs = table0.findAll('tr')

    mgmt_company = trs[0].findAll('td')[1].text.strip()                  #gen8 Домом управляет
    if trs[0].findAll('td')[1].find('a'):
        mgmt_company_link = 'http://www.reformagkh.ru' + trs[0].findAll('td')[1].find('a')['href']
        mgmt_company_link = mgmt_company_link.split('?')[0]
    else:
        mgmt_company_link = ''

    table1 = tables[1]
    trs = table1.findAll('tr')
    status = '' #trs[1].findAll('td')[1].text.strip()                    #gen7 Состояние дома (куда-то исчезло в последней версии)

    table1 = tables[1]
    trs = table1.findAll('tr')
    #area = float(trs[2].findAll('td')[1].text.strip().replace(' ',''))  #gen1 Общая площадь
    #year = trs[6].findAll('td')[1].text.strip()                          #gen6 Год ввода в экспл
    lastupdate = trs[8].findAll('td')[1].text.strip()                    #gen2 Последнее изменение анкеты
    lastupdate = ' '.join(lastupdate.replace('\n','').split())
    servicedate_start = trs[10].findAll('td')[1].text.strip()            #gen3 Дата начала обслуживания дома
    servicedate_end = '' #trs[5].findAll('td')[1].text.strip()           #gen4 Плановая дата прекращения обслуживания дома

    #TODO extract lat/long coords from script
    if 'center' in soup.findAll('script')[11]:
        lat,lon = soup.findAll('script')[11].text.split('\n')[3].split('[')[1].split(']')[0].split(',')
    else:
        lat,lon = soup.findAll('script')[12].text.split('\n')[3].split('[')[1].split(']')[0].split(',')

    #PASSPORT
    ##GENERAL
    divs = soup.findAll('div', { 'class' : 'numbered' })
    div0 = divs[0]
    trs = div0.findAll('tr')
    lentrs = len(trs)
    if lentrs > 58:
        trs_offset = lentrs - 58
    else:
        trs_offset = 0

    year = extract_value(trs[3])                            #5 Год ввода в эксплуатацию
    serie = extract_value(trs[5])                            #1 Серия
    house_type = extract_value(trs[7])                       #4 Тип жилого дома
    capfond = extract_value(trs[9])                          #5 Способ формирования фонда капитального ремонта
    avar = extract_value(trs[11])                            #6 Дом признан аварийным
    levels_max = extract_subvalue(trs[12], 1)                #7 Этажность: макс
    levels_min = extract_subvalue(trs[12], 3)                #7 Этажность: мин
    doors = extract_value(trs[18])                           #9 Количество подъездов
    room_count = extract_value(trs[23])                      #10 Количество помещений
    room_count_live = extract_value(trs[26])                 #10 Количество помещений: жилых
    room_count_nonlive = extract_value(trs[28])              #10 Количество помещений: нежилых
    area = extract_value(trs[31]).replace(' ','')            #11 Общая площадь дома
    area_live = extract_value(trs[34]).replace(' ','')       #11 Общая площадь дома, жилых
    area_nonlive = extract_value(trs[36]).replace(' ','')    #11 Общая площадь дома, нежилых

    area_gen = extract_value(trs[38]).replace(' ','')        #11 Общая площадь помещений, входящих в состав общего имущества
    area_land = extract_value(trs[41]).replace(' ','')       #12 Общие сведения о земельном участке, на котором расположен многоквартирный дом
    area_park = extract_value(trs[43]).replace(' ','')       #12 Общие сведения о земельном участке, на котором расположен многоквартирный дом
    cadno = trs[44].findAll('td')[1].text                    #12 кад номер

    energy_class = extract_value(trs[48 + trs_offset])                    #13 Класс энергоэффективности
    blag_playground = extract_value(trs[51 + trs_offset])                 #14 Элементы благоустройства
    blag_sport = extract_value(trs[53 + trs_offset])                      #14 Элементы благоустройства
    blag_other = extract_value(trs[55 + trs_offset])                      #14 Элементы благоустройства
    other = extract_value(trs[57 + trs_offset])                           #14 Элементы благоустройства


    #write to output
    csvwriter_housedata.writerow(dict(LAT=lat,
                                      LON=lon,
                                      HOUSE_ID=house_id,
                                      ADDRESS=address.encode('utf-8'),
                                      YEAR=year.encode('utf-8'),
                                      LASTUPDATE=lastupdate.encode('utf-8'),
                                      SERVICEDATE_START=servicedate_start.encode('utf-8'),
                                      SERIE=serie.encode('utf-8'),
                                      HOUSE_TYPE=house_type.encode('utf-8'),
                                      CAPFOND=capfond.encode('utf-8'),
                                      MGMT_COMPANY=mgmt_company.encode('utf-8'),
                                      MGMT_COMPANY_LINK=mgmt_company_link.encode('utf-8'),
                                      AVAR=avar.encode('utf-8'),
                                      LEVELS_MAX=levels_max.encode('utf-8'),
                                      LEVELS_MIN=levels_min.encode('utf-8'),
                                      DOORS=doors.encode('utf-8'),
                                      ROOM_COUNT=room_count.encode('utf-8'),
                                      ROOM_COUNT_LIVE=room_count_live.encode('utf-8'),
                                      ROOM_COUNT_NONLIVE=room_count_nonlive.encode('utf-8'),
                                      AREA=area.encode('utf-8'),
                                      AREA_LIVE=area_live.encode('utf-8'),
                                      AREA_NONLIVE=area_nonlive.encode('utf-8'),
                                      AREA_GEN=area_gen.encode('utf-8'),
                                      AREA_LAND=area_land.encode('utf-8'),
                                      AREA_PARK=area_park.encode('utf-8'),
                                      #CADNO=cadno.encode('utf-8'),
                                      ENERGY_CLASS=energy_class.encode('utf-8'),
                                      BLAG_PLAYGROUND=blag_playground.encode('utf-8'),
                                      BLAG_SPORT=blag_sport.encode('utf-8'),
                                      BLAG_OTHER=blag_other.encode('utf-8'),
                                      OTHER=other.encode('utf-8')))
    return True

def write_house_attribute(result_set):
    if args.outputformat == 'csv':
        csvwriter_housedata.writerow(result_set)
    elif args.outputformat == 'sqlite':
        result_set['ATTR_NAME'] = result_set['ATTR_NAME'].decode('utf-8') if result_set['ATTR_NAME'] else None
        result_set['FOUND_NAME'] = result_set['FOUND_NAME'].decode('utf-8') if result_set['FOUND_NAME'] else None
        result_set['VALUE'] = result_set['VALUE'].decode('utf-8') if result_set['VALUE'] else None
        sqcur.execute("insert into attrvals values (" + fieldnames_phld + ")", [ result_set[k] for k in fieldnames_data])
    else: # outputformat == 'pg'
        psycopg2.extras.execute_values(pgcur, pgquery, [[result_set[k] for k in fieldnames_data]], template=None)

def parse_house_page_attrlist(soup):
    """Parses a house page using attrlist information"""

    # lat lon extractions
    latlon_re = r'center: \[(\d+\.\d+),\s*(\d+\.\d+)\],'
    latlon_match = re.search(latlon_re, soup.findAll('script')[11].text)
    if not latlon_match:
        latlon_match = re.search(latlon_re, soup.findAll('script')[12].text)
    if latlon_match:
        lat,lon = latlon_match.group(1),latlon_match.group(2)
    else:
        lat,lon = 'Not Found','Not Found'
        print '\tlat,lon was not found'

    write_house_attribute(dict(REGION=region_name,HOUSE_ID=house_id,ATTR_NAME='lat',FOUND_NAME='lat',ED_DIST=0,VALUE=lat))
    write_house_attribute(dict(REGION=region_name,HOUSE_ID=house_id,ATTR_NAME='lon',FOUND_NAME='lon',ED_DIST=0,VALUE=lon))

    # create output variable name from the section names
    sect_attrs = ['section-rus', 'subsection-rus', 'attribute-rus', 'subattribute-rus', 'subsubattribute-rus']
    cur_sect = dict.fromkeys(sect_attrs)

    for row in attrlist:

        # update section attributes
        for attr in sect_attrs:
            if row[attr]:
                cur_sect[attr] = row[attr]
                for i in range(sect_attrs.index(attr)+1,len(sect_attrs)-1):
                    cur_sect[sect_attrs[i]] = None
            expected_attr_name = row[attr] or expected_attr_name # expected attr string is set to the last section name

        if row['Selector Code for Name']:
            attr_name = '->'.join([ cur_sect[attr] for attr in sect_attrs if cur_sect[attr] ])
            fixed_selector_code_name = re.sub('nth-child', 'nth-of-type', row['Selector Code for Name']) # this is needed because bs does not support nth-child
            fixed_selector_code_value = re.sub('nth-child', 'nth-of-type', row['Selector Code for Value'])
            #fixed_selector_code_name = row['Selector Code for Name']
            #fixed_selector_code_value = row['Selector Code for Value']
            #print attr_name, '==>', row['Selector Code for Name'], '==>', fixed_selector_code_name

            result_name = soup.select(fixed_selector_code_name)

            if result_name:
                found_attr_name = result_name[0].text.strip().encode('utf-8')

                # value extraction
                result_value = soup.select(fixed_selector_code_value)

                found_attr_value = result_value[0].text.strip().encode('utf-8') if result_value else 'not found'

                result_set = dict(REGION=region_name,
                                  HOUSE_ID=house_id,
                                  ATTR_NAME=attr_name,
                                  FOUND_NAME=found_attr_name,
                                  ED_DIST=editdistance.eval(expected_attr_name,found_attr_name),
                                  VALUE=found_attr_value)
            else: # not found
                result_set = dict(REGION=region_name,
                                  HOUSE_ID=house_id,
                                  ATTR_NAME=attr_name,
                                  FOUND_NAME=None,
                                  ED_DIST=None,
                                  VALUE=None)

            write_house_attribute(result_set)

        if args.outputformat in ('sqlite', 'pg'):
            conn.commit()

def load_attrlist():
    """Loads the list of attributes and their id string from a CSV file."""

    attrlist_fh = open(args.attrlist, 'rU')
    attrlist_reader = csv.reader(attrlist_fh, delimiter='\t')
    attrlist = []
    ignorecols = [] # columns to be ignored
    attrnames = [] # names of the attributes from the 2nd row
    c=0
    for row in attrlist_reader:
        c += 1
        if c == 3:
            attrnames = [ s.strip(' ') for s in row ]
            # ignore columns with no names
            ignorecols = [ i for i,x in enumerate(attrnames) if not x ] # list of columns with no names
            attrnames = [i for j, i in enumerate(attrnames) if j not in ignorecols] # now remove ignore elements
            #print ':'.join(attrnames)
        elif c > 3:
            row = [i for j, i in enumerate(row) if j not in ignorecols] # remove ignore columns
            attrlist.append(dict(zip( attrnames, [ s.strip(' ').replace('\n', '') for s in row ] )))

    # TODO: create output table column name

    return attrlist

def out_of_the_way(file_name):
    if os.path.isfile(file_name):
        bfile_name = file_name + '.{:%Y-%m-%dT%H.%M.%S}'.format(datetime.datetime.now())
        print('file backed up to ' + bfile_name)
        shutil.move(file_name, bfile_name)

if __name__ == '__main__':
    if not args.no_tor:
        print 'Establishing tor connection to socks5://127.0.0.1:9150...'
        session = requesocks.session()
        session.proxies = {'http':  'socks5://127.0.0.1:9150',
                           'https': 'socks5://127.0.0.1:9150'}
        try:
            print 'Tor connection established, testing duckduckgo.com'
            session.get('http://duckduckgo.com').text
            print 'Connected to Tor network!'
        except:
            print('Tor isn\'t running or not configured properly')
            sys.exit(1)

    tid = args.id #2280999
    lvl1_link = 'http://www.reformagkh.ru/myhouse?tid=' + tid #+ '&sort=alphabet&item=mkd'
    house_link = 'http://www.reformagkh.ru/myhouse/profile/'
    #house_id = 8625429

    region = namedtuple('reg', 'lvl1name lvl2name lvl3name lvl1tid lvl2tid lvl3tid')

    #init errors.log
    f_errors = open('errors.txt','wb')
    f_ids = open('ids.txt','wb')

    # data extractor intialization
    if args.extractor == 'original':
        #init csv for housedata
        fieldnames_data = ('LAT','LON','HOUSE_ID','ADDRESS','YEAR','LASTUPDATE','SERVICEDATE_START','SERIE','HOUSE_TYPE','CAPFOND','MGMT_COMPANY','MGMT_COMPANY_LINK','AVAR','LEVELS_MAX','LEVELS_MIN','DOORS','ROOM_COUNT','ROOM_COUNT_LIVE','ROOM_COUNT_NONLIVE','AREA','AREA_LIVE','AREA_NONLIVE','AREA_GEN','AREA_LAND','AREA_PARK','CADNO','ENERGY_CLASS','BLAG_PLAYGROUND','BLAG_SPORT','BLAG_OTHER','OTHER')

    elif args.extractor == 'attrlist':
        # load csv file with attribute descriptions
        attrlist = load_attrlist()
        fieldnames_data = ('REGION', 'HOUSE_ID','ATTR_NAME','FOUND_NAME','ED_DIST','VALUE')
        fieldnames_type = ('TEXT', 'TEXT','TEXT','TEXT','INTEGER','TEXT')
        fieldnames_phld = ', '.join([ ':' + s for s in fieldnames_data]) #placeholder for sqlite

    # create an output file housedata.csv with the requested field names
    if args.extractor != 'none':
        f_housedata_name = args.output_name   #data/housedata.csv
        if args.outputmode == 'overwrite':
            out_of_the_way(f_housedata_name)
        if args.outputformat == 'csv':
            if args.outputmode == 'overwrite':
                f_housedata = open(f_housedata_name,'wb')
                fields_str = ','.join(fieldnames_data)
                f_housedata.write(fields_str+'\n')
                f_housedata.close()
        elif args.outputformat == 'sqlite': # sqlite format for attrlist data extractor
            conn = sqlite3.connect(f_housedata_name)
            sqcur = conn.cursor()
            sqcur.execute('create table if not exists attrvals(' + ', '.join([ s+' '+t for s,t in zip(fieldnames_data, fieldnames_type)]) + ', primary key(HOUSE_ID, ATTR_NAME) )')
            conn.commit()
        else: # args.outputformat == 'pg':
            try:
                conn = psycopg2.connect(args.output_name)
                pgcur = conn.cursor()
                pgquery = 'insert into attrvals_all(region, house_id, attr_name, found_name, ed_dist, value) values %s'
            except psycopg2.Error as e:
                print 'Failed to open database connection to', args.output_name, e
                sys.exit(6)

        if args.outputformat == 'csv':
            f_housedata = open(f_housedata_name,'ab')
            csvwriter_housedata = csv.DictWriter(f_housedata, fieldnames=fieldnames_data)

    if args.houseid:
        res = get_housedata(house_link,str(args.id),None,None,None,None)
        if res == False:
            print 'Building data was not retrieved for id=', args.id
    elif args.allfiles:
        for f in glob.glob(args.originals_folder + '/*.html'):
            mtch = re.search(r'(\d{7})\.html$', f)
            if mtch:
                house_id = mtch.group(1)
                print 'Processing cached file', f, 'id', house_id
                res = get_housedata(house_link,str(house_id),None,None,None,None)
                if res == False:
                    print 'Building data was not retrieved for id=', house_id
            else:
                print 'No house_id in ', f
    else:
        regs = get_data_links(args.id)

        for reg in regs:
            if reg[5] != '' or len([i for i in regs if reg[4] in i]) == 1: #can't use Counter with cnt(elem[4] for elem in regs)[reg[4]] because of the progressbar
                print 'Region: ', reg[0], ',', reg[1], ',', reg[2]
                # get list of houses
                tid = reg[5] if reg[5] else reg[4]
                print 'Effective tid:', tid
                house_ids_fname = args.originals_folder + dirsep + 'house_ids-' + str(tid) + '.pickle'

                if args.reload_list and os.path.isfile(house_ids_fname):
                    out_of_the_way(house_ids_fname)

                if os.path.isfile(house_ids_fname):
                    print 'Loading cached house_ids from ', house_ids_fname
                    f_house_ids = open(house_ids_fname, 'rb')
                    houses_ids = pickle.load(f_house_ids)
                    f_house_ids.close()
                elif args.cache_only:
                    print 'No cached house_ids for requested tid', house_ids_fname
                    sys.exit(3)
                else:
                    print 'Retrieve house ids from the site'
                    houses_ids = get_house_list('http://www.reformagkh.ru/myhouse/list?tid=' + tid)

                    # save IDs in a file making a copy of an existing file
                    print 'Saving house_ids to ', house_ids_fname
                    f_house_ids = open(house_ids_fname, 'wb')
                    pickle.dump(houses_ids, f_house_ids)
                    f_house_ids.close()

                #pbar = ProgressBar(widgets=[Bar('=', '[', ']'), ' ', Counter(), ' of ' + str(len(houses_ids)), ' ', ETA()]).start()
                #pbar.maxval = len(houses_ids)

                print len(houses_ids),'house_ids will be processed'
                if args.shuffle:
                    random.shuffle(houses_ids)
                i = 0
                for house_id in houses_ids:
                    i = i+1
                    print i, '\tProcessing house_id', house_id
                    res = get_housedata(house_link,str(house_id),reg[0],reg[3],reg[1],reg[4])
                    if res == False:
                        print 'Building data was not retrieved for id=', house_id
                    #pbar.update(pbar.currval+1)
                print 'Processed', i, 'house_ids'
                #pbar.finish()

    if args.extractor == 'original':
        f_housedata.close()
    f_errors.close()
    f_ids.close()
