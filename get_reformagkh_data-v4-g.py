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
# Examples:
#      python get_reformagkh_data-v2.py 2280999 data/housedata2.csv -o html_orig
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
from progressbar import *
from httplib import BadStatusLine,IncompleteRead
import socket
import argparse
from collections import namedtuple
from time import sleep
import requesocks
from stem import Signal
from stem.control import Controller

parser = argparse.ArgumentParser()
parser.add_argument('id', help='Region ID')
parser.add_argument('output_name', help='Where to store the results (path to CSV file)')
parser.add_argument('-o','--overwrite', action="store_true", help='Overwite all, will write over previously downloaded files.')
parser.add_argument('-of','--originals_folder', help='Folder to save original html files. Skip saving if empty.')
args = parser.parse_args()
if args.originals_folder:
    if not args.originals_folder.endswith('\\'): args.originals_folder = args.originals_folder + '\\'
    if not os.path.exists(args.originals_folder): os.mkdir(args.originals_folder)
    
def console_out(text):
    #write httplib error messages to console
    time_current = datetime.datetime.now()
    timestamp = time_current.strftime('%Y-%m-%d %H:%M:%S')
    
    f_errors.write(timestamp + ': '+ text)

def get_content(link):
    numtries = 5
    timeoutvalue = 40
    
    for i in range(1,numtries+1):
        try:
            res = session.get(link).text
        except:
            time.sleep(3)
            res = ''
        else:
            break
    
    if res == '':
        print('Session time out')
        sys.exit() 
        
    return res
    
def urlopen_house(link,id):
    #fetch html data on a house
    
    res = get_content(link)
    if args.originals_folder:
        f = open(args.originals_folder + id + ".html","wb")
        f.write(res.encode('utf-8'))
        f.close()

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
    soup = BeautifulSoup(''.join(res), 'html.parser')
    captcha = check_captcha(soup)
    
    while captcha == True:
        res = get_content(link)
        soup = BeautifulSoup(''.join(res), 'html.parser')
        captcha = check_captcha(soup)
        change_proxy()
    
    divs = soup.findAll('div', { 'class' : 'clearfix' })
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
        soup = BeautifulSoup(''.join(res), 'html.parser')
        captcha = check_captcha(soup)
    
        while captcha == True:
            res = get_content(link + '&page=' + str(page) + '&limit=10000')
            soup = BeautifulSoup(''.join(res), 'html.parser')
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
    if captcha != None or u'Каптча' in soup.text or 'captcha' in str(soup) or len(soup)==67: 
        return True
    else:    
        return False
    
def get_housedata(link,house_id,lvl1_name,lvl1_id,lvl2_name,lvl2_id):
    #process house data to get main attributes
    
    if args.originals_folder:
        if not os.path.isfile(args.originals_folder + '/' + house_id + ".html"):
            try:
                res = urlopen_house(link + 'view/' + house_id,house_id)
            except:
                f_errors.write(link + 'view/' + house_id + '\n')
                res = False
        else:
            res = open(args.originals_folder + '/' + house_id + ".html",'rb').read()
    else:
       try:
           res = urlopen_house(link + 'view/' + house_id,house_id)
       except:
           f_errors.write(link + 'view/' + house_id + '\n')
           res = False
    
    if res != False:
        soup = BeautifulSoup(''.join(res),'html.parser')
        f_ids.write(link + 'view/' + house_id + ',' + house_id + '\n')
        
        if len(soup) > 0 and 'Time-out' not in soup.text and '502 Bad Gateway' not in soup.text: #u'Ошибка' not in soup.text

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

if __name__ == '__main__':
    session = requesocks.session()
    session.proxies = {'http':  'socks5://127.0.0.1:9150',
                       'https': 'socks5://127.0.0.1:9150'}
    try:
        session.get('http://google.com').text
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
    
    #init csv for housedata
    f_housedata_name = args.output_name   #data/housedata.csv
    f_housedata = open(f_housedata_name,'wb')
    fieldnames_data = ('LAT','LON','HOUSE_ID','ADDRESS','YEAR','LASTUPDATE','SERVICEDATE_START','SERIE','HOUSE_TYPE','CAPFOND','MGMT_COMPANY','MGMT_COMPANY_LINK','AVAR','LEVELS_MAX','LEVELS_MIN','DOORS','ROOM_COUNT','ROOM_COUNT_LIVE','ROOM_COUNT_NONLIVE','AREA','AREA_LIVE','AREA_NONLIVE','AREA_GEN','AREA_LAND','AREA_PARK','CADNO','ENERGY_CLASS','BLAG_PLAYGROUND','BLAG_SPORT','BLAG_OTHER','OTHER')
    fields_str = ','.join(fieldnames_data)
    f_housedata.write(fields_str+'\n')
    f_housedata.close()
    
    f_housedata = open(f_housedata_name,'ab')
    
    csvwriter_housedata = csv.DictWriter(f_housedata, fieldnames=fieldnames_data)
    
    regs = get_data_links(args.id)
    
    for reg in regs:
        if reg[5] != '' or len([i for i in regs if reg[4] in i]) == 1: #can't use Counter with cnt(elem[4] for elem in regs)[reg[4]] because of the progressbar
                print(reg[0].decode('utf8') + ', ' + reg[1].decode('utf8') + ', ' + reg[2].decode('utf8'))
                #get list of houses
                if reg[5] == '': 
                    houses_ids = get_house_list('http://www.reformagkh.ru/myhouse/list?tid=' + reg[4])
                else:
                    houses_ids = get_house_list('http://www.reformagkh.ru/myhouse/list?tid=' + reg[5])
                
                pbar = ProgressBar(widgets=[Bar('=', '[', ']'), ' ', Counter(), ' of ' + str(len(houses_ids)), ' ', ETA()]).start()
                pbar.maxval = len(houses_ids)
                
                i = 0
                for house_id in houses_ids:
                    i = i+1
                    res = get_housedata(house_link,str(house_id),reg[0],reg[3],reg[1],reg[4])
                    if res == False:
                        change_proxy()
                        res = get_housedata(house_link,str(house_id),reg[0],reg[3],reg[1],reg[4])
                    pbar.update(pbar.currval+1)
                pbar.finish()

    f_housedata.close()
    f_errors.close()
    f_ids.close()
