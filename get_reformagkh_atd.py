#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

#******************************************************************************
#
# get_reformagkh_atd.py
# ---------------------------------------------------------
# Grabs reformagkh.ru data on administrative division which is further used for data grabbing.
# More: https://github.com/nextgis/reformagkh
#
# Usage: 
#      usage: get_reformagkh_data-v2.py [-h] [-o ORIGINALS_FOLDER] id output_name
#      where:
#           -h           show this help message and exit
#           id           Region ID
#           output_name  Where to store the results (path to CSV file)
#            -o ORIGINALS_FOLDER  Folder to save original html files. Skip saving if empty.
# Examples:
#      python get_reformagkh_data-v2.py 2280999 data/housedata2.csv
#
# Copyright (C) 2014-2016 Maxim Dubinin (sim@gis-lab.info)
# Created: 6.04.2016
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
import re

parser = argparse.ArgumentParser()
parser.add_argument('output_name', help='Where to store the results (path to CSV file)')
parser.add_argument('-o','--originals_folder', help='Folder to save original html files. Skip saving if empty.')
args = parser.parse_args()


def console_out(text):
    #write httplib error messages to console
    time_current = datetime.datetime.now()
    timestamp = time_current.strftime('%Y-%m-%d %H:%M:%S')
    
    f_errors.write(timestamp + ': '+ text)

def urlopen_house(link,id):
    #fetch html data on a house
    numtries = 5
    timeoutvalue = 40
    
    for i in range(1,numtries+1):
        i = str(i)
        try:
            u = urllib2.urlopen(link, timeout = timeoutvalue)
        except BadStatusLine:
            console_out('BadStatusLine for ID:' + id + '.' + ' Attempt: ' + i)
            res = False
            time.sleep(3)
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                console_out('We failed to reach a server for ID:' + id + ' Reason: ' + str(e.reason) + '.' + ' Attempt: ' + i)
            elif hasattr(e, 'code'):
                console_out('The server couldn\'t fulfill the request for ID: ' + id + ' Error code: ' + str(e.code) + '.' + ' Attempt: ' + i)
            res = False
            time.sleep(3)
        except socket.timeout, e:
            console_out('Connection timed out on urlopen() for ID: ' + id + '.' + ' Attempt: ' + i)
            res = False
            time.sleep(3)
        else:
            try:
                r = u.read()
            except socket.timeout, e:
                console_out('Connection timed out on socket.read() for ID: ' + id + '.' + ' Attempt: ' + i)
                res = False
                u.close()
                time.sleep(3)
            except IncompleteRead:
                console_out('Incomplete read on socket.read() for ID: ' + id + '.' + ' Attempt: ' + i)
                res = False
                u.close()
                time.sleep(3)
            else:
                res = r
                if args.originals_folder:
                    f = open(args.originals_folder + id + ".html","wb")
                    f.write(res)
                    f.close()
                break
    return res

def extract_value(tr):
    #extract value for general attributes
    res = tr.findAll('td')[1].text.strip()
      
    return res

def extract_subvalue(tr,num):
    #extract value for general attributes
    res = tr.findAll('tr')[num].text.strip()
      
    return res

def extract_value_descr(trs,num):
    #extract value for description field
    tr = trs[num]
    res = tr.findAll('td')[0].findAll('span')[1].text.strip()

    return res

def extract_value_constr(trs,num):
    #extract value for construction features field

    #TODO deal with popup text boxes that might(?) contain more information, currently only first non-null <p> is being returned
    tr = trs[num]
    res = tr.findAll('td')[0].findAll('span')[1].text.strip()  

    return res

def extract_value_area(trs,num):
    #extract values for various living area
    tr = trs[num]

    area_live_total = tr.find('td').find('span').text.split(' - ')[1]
    trs = tr.findAll('tr')
    area_live_priv = trs[1].text.strip()
    area_live_munic = trs[3].text.strip()
    area_live_state = trs[5].text.strip()

    return area_live_total,area_live_priv,area_live_munic,area_live_state

def extract_value_heat(trs,num):
    #extract values for heat exchange
    trs = trs[num].findAll('tr')

    heat_fact = trs[1].text.strip()
    heat_norm = trs[3].text.strip()

    return heat_fact,heat_norm

def get_housedata(link,house_id,lvl1_name,lvl1_id,lvl2_name,lvl2_id):
    #process house data to get main attributes
    res = urlopen_house(link + 'view/' + house_id,house_id)
    
    if res != False:
        soup = BeautifulSoup(''.join(res),'html.parser')
        
        #print(house_id)

        address = soup.find('span', { 'class' : 'loc_name float-left width650 word-wrap-break-word' }).text.strip()
        
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
        lat,lon = soup.findAll('script')[11].text.split('\n')[3].split('[')[1].split(']')[0].split(',')

        #PASSPORT
        ##GENERAL
        divs = soup.findAll('div', { 'class' : 'numbered' })
        div0 = divs[0]
        trs = div0.findAll('tr')
        
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
        #cadno = trs[44].findAll('td')[1].text                    #12 кад номер
        energy_class = extract_value(trs[48])                    #13 Класс энергоэффективности
        blag_playground = extract_value(trs[51])                 #14 Элементы благоустройства
        blag_sport = extract_value(trs[53])                      #14 Элементы благоустройства
        blag_other = extract_value(trs[55])                      #14 Элементы благоустройства
        other = extract_value(trs[57])                           #14 Элементы благоустройства

        
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

def get_ids(link):
    
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    tables = soup.findAll('table',{ 'class' : 'col_list ' })
    if len(tables) == 0: tables = soup.findAll('table',{ 'class' : 'col_list tree' })
    lvl_ids = {}
    for table in tables:
        links = table.findAll('a')
        for link in links:
            name = link.text.strip()
            if link.has_attr('href'):
                tid = link['href'].replace('?tid=','').split('&')[0]
                link = 'http://www.reformagkh.ru/myhouse?tid='+tid
            else:
                tid = 0
                link = ''
            lvl_ids[name] = tid
    
    return lvl_ids
    
if __name__ == '__main__':
    start_link = 'https://www.reformagkh.ru/myhouse?geo=reset'
    base_link = 'https://www.reformagkh.ru/myhouse?tid='
    
    #init csv
    f_atd = open(args.output_name,'wb')
    fieldnames_data = ('LVL1_NAME','LVL2_NAME','LVL3_NAME','LVL1_TID','LVL2_TID','LVL3_TID','LVL1_LINK','LVL2_LINK','LVL3_LINK')
    fields_str = ','.join(fieldnames_data)
    f_atd.write(fields_str+'\n')
    f_atd.close()
    
    f_atd = open(args.output_name,'ab')
    
    csvwriter_atd = csv.DictWriter(f_atd, fieldnames=fieldnames_data)
    
    lvl1s = get_ids(start_link)
    
    for lvl1 in lvl1s:
        lvl1_name = lvl1
        lvll_tid = lvl1s[lvl1]
        lvl1_link = base_link + str(lvll_tid)
        lvl2_name = ''
        lvl2_tid = ''
        lvl2_link = ''
        lvl3_name = ''
        lvl3_tid = ''
        lvl3_link = ''
        
        print(lvl1_name + ', ' + lvl2_name + ', ' + lvl3_name)
        csvwriter_atd.writerow(dict(LVL1_NAME=lvl1_name.encode('utf-8'),
                            LVL2_NAME=lvl2_name.encode('utf-8'),
                            LVL3_NAME=lvl3_name.encode('utf-8'),
                            LVL1_TID=lvll_tid,
                            LVL2_TID=lvl2_tid,
                            LVL3_TID=lvl3_tid,
                            LVL1_LINK=lvl1_link,
                            LVL2_LINK=lvl2_link,
                            LVL3_LINK=lvl3_link))
    
        lvl2s = get_ids(lvl1_link)
        
        
        for lvl2 in lvl2s:
            lvl2_name = lvl2
            if lvl2s[lvl2] == 0:
                lvl2_tid = ''
                lvl2_link = ''
            else:
                lvl2_tid = lvl2s[lvl2]
                lvl2_link = base_link + str(lvl2_tid)
            lvl3_name = ''
            lvl3_tid = ''
            lvl3_link = ''
            
            print(lvl1_name + ', ' + lvl2_name + ', ' + lvl3_name)
            csvwriter_atd.writerow(dict(LVL1_NAME=lvl1_name.encode('utf-8'),
                            LVL2_NAME=lvl2_name.encode('utf-8'),
                            LVL3_NAME=lvl3_name.encode('utf-8'),
                            LVL1_TID=lvll_tid,
                            LVL2_TID=lvl2_tid,
                            LVL3_TID=lvl3_tid,
                            LVL1_LINK=lvl1_link,
                            LVL2_LINK=lvl2_link,
                            LVL3_LINK=lvl3_link))
            if lvl2_link != '':
                lvl3s = get_ids(lvl2_link)
                
                for lvl3 in lvl3s:
                    lvl3_name = lvl3
                    if lvl3s[lvl3] == 0:
                        lvl3_tid = ''
                        lvl3_link = ''
                    else:
                        lvl3_tid = lvl3s[lvl3]
                        lvl3_link = base_link + str(lvl3_tid)
                    
                    print(lvl1_name + ', ' + lvl2_name + ', ' + lvl3_name)
                    csvwriter_atd.writerow(dict(LVL1_NAME=lvl1_name.encode('utf-8'),
                                    LVL2_NAME=lvl2_name.encode('utf-8'),
                                    LVL3_NAME=lvl3_name.encode('utf-8'),
                                    LVL1_TID=lvll_tid,
                                    LVL2_TID=lvl2_tid,
                                    LVL3_TID=lvl3_tid,
                                    LVL1_LINK=lvl1_link,
                                    LVL2_LINK=lvl2_link,
                                    LVL3_LINK=lvl3_link))

    f_atd.close()
