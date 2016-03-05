#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

#******************************************************************************
#
# get_reformagkh_data.py
# ---------------------------------------------------------
# Grab reformagkh.ru data on buildings, put it in the CSV table.
# More: https://github.com/nextgis/reformagkh
#
# Usage: 
#      usage: get_reformagkh_data.py [-h] id output_name
#      where:
#           -h           show this help message and exit
#           id           Region ID
#           output_name  Where to store the results (path to CSV file)
# Examples:
#      python get_reformagkh_data.py 2280999 data/housedata2.csv
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
import re

parser = argparse.ArgumentParser()
parser.add_argument('id', help='Region ID')
parser.add_argument('output_name', help='Where to store the results (path to CSV file)')
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
                break
    
    return res

def extract_value(trs,num):
    #extract value for general attributes
    tr = trs[num]
    res = tr.findAll('td')[1].text.strip()
      
    return res

def extract_subvalue(trs,num1,num2):
    #extract value for general attributes
    tr = trs[num1]

    res = trs[12].findAll('tr')[num2].text.strip()
      
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
        soup = BeautifulSoup(''.join(res))
        
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
        year = trs[6].findAll('td')[1].text.strip()                          #gen6 Год ввода в экспл
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
        
        year2 = extract_value(trs, 3)                            #5 Год ввода в эксплуатацию
        serie = extract_value(trs, 5)                            #1 Серия
        house_type = extract_value(trs, 7)                       #4 Тип жилого дома
        capfond = extract_value(trs, 9)                          #5 Способ формирования фонда капитального ремонта
        avar = extract_value(trs, 11)                               #6 Дом признан аварийным
        levels_max = extract_subvalue(trs, 12, 1)                     #7 Этажность: макс
        levels_min = extract_subvalue(trs, 12, 3)                     #7 Этажность: макс
        doors = extract_value(trs, 18)                                #9 Количество подъездов
        room_count = extract_value(trs, 23)                           #10 Количество помещений
        room_count_live = extract_value(trs, 26)                      #10 Количество помещений: жилых
        room_count_nonlive = extract_value(trs, 28)                   #10 Количество помещений: нежилых
        area = extract_value(trs, 31).replace(' ','')          #11 Общая площадь дома
        area_live = extract_value(trs, 34).replace(' ','')     #11 Общая площадь дома, жилых
        area_nonlive = extract_value(trs, 36).replace(' ','')  #11 Общая площадь дома, нежилых

        try:
            area_gen = extract_value(trs, 38).replace(' ','')      #11 Общая площадь помещений, входящих в состав общего имущества
        except:
            area_gen = extract_value(trs, 38)

        area_land = extract_value(trs, 41).replace(' ','')     #12 Общие сведения о земельном участке, на котором расположен многоквартирный дом
        area_park = extract_value(trs, 43).replace(' ','')     #12 Общие сведения о земельном участке, на котором расположен многоквартирный дом
        cadno = trs[44].findAll('td')[1].text                         #12 кад номер
        energy_class = extract_value(trs, 48)                         #13 Класс энергоэффективности
        blag_playground = extract_value(trs, 51)                      #14 Элементы благоустройства
        blag_sport = extract_value(trs, 53)                           #14 Элементы благоустройства
        blag_other = extract_value(trs, 55)                           #14 Элементы благоустройства
        other = extract_value(trs, 57)                                #14 Элементы благоустройства

        
        #write to output
        csvwriter_housedata.writerow(dict(LAT=lat,
                                          LON=lon,
                                          HOUSE_ID=house_id,
                                          ADDRESS=address.encode('utf-8'),
                                          YEAR2=year2.encode('utf-8'),
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
                                          CADNO=cadno.encode('utf-8'),
                                          ENERGY_CLASS=energy_class.encode('utf-8'),
                                          BLAG_PLAYGROUND=blag_playground.encode('utf-8'),
                                          BLAG_SPORT=blag_sport.encode('utf-8'),
                                          BLAG_OTHER=blag_other.encode('utf-8'),
                                          OTHER=other.encode('utf-8')))

def get_lvl1_ids(link):
    
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    trs = soup.findAll('tr',{ 'class' : 'left' })
    
    
    lvl1_ids = {}
    for tr in trs:
        loc = tr.findAll('td')[1]
        if loc.find('a'):
            name_loc = loc.find('a').text.strip()
            id_loc = loc.find('a')['href'].replace('?tid=','').split('&')[0]
            lvl1_ids[name_loc] = id_loc
    
    
    
    
    #small city with 1 level
    if len(lvl1_ids)==0:
        tid=link.replace('tid=','!').split('!')[1]
        lvl1_ids[tid]=tid

    return lvl1_ids

def get_lvl2_ids(link):
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    trs = soup.findAll('tr',{ 'class' : 'left' })
    
    lvl2_ids = {}
    for tr in trs:
        loc = tr.findAll('td')[1]
        if loc.find('a'):
            name_loc = loc.find('a').text.strip()
            if loc.find('a').has_attr('href'):
                id_loc = loc.find('a')['href'].replace('?tid=','').split('&')[0]
                lvl2_ids[name_loc] = id_loc
    
    if len(lvl2_ids)==0:
        tid=link.replace('tid=','!').split('!')[1]
        lvl2_ids[tid]=tid
    
    return lvl2_ids

def get_house_list(link):
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    houses_ids = []
    tds = soup.findAll('td')
    for td in tds:
        if td.find('a') is not None:
            if td.find('a').has_attr('href') and 'myhouse' in td.find('a')['href']:
                house_id = td.find('a')['href'].split('/')[4]
                houses_ids.append(house_id)
    
    return houses_ids
    
if __name__ == '__main__':
    tid = args.id #2280999
    lvl1_link = 'http://www.reformagkh.ru/myhouse?tid=' + tid #+ '&sort=alphabet&item=mkd'
    house_link = 'http://www.reformagkh.ru/myhouse/profile/'
    #house_id = 8625429
    
    #init errors.log
    f_errors = open('errors.txt','wb')
    
    #init csv for housedata
    f_housedata_name = args.output_name   #data/housedata.csv
    f_housedata = open(f_housedata_name,'wb')
    fieldnames_data = ('LAT','LON','HOUSE_ID','ADDRESS','YEAR2','LASTUPDATE','SERVICEDATE_START','SERIE','HOUSE_TYPE','CAPFOND','MGMT_COMPANY','MGMT_COMPANY_LINK','AVAR','LEVELS_MAX','LEVELS_MIN','DOORS','ROOM_COUNT','ROOM_COUNT_LIVE','ROOM_COUNT_NONLIVE','AREA','AREA_LIVE','AREA_NONLIVE','AREA_GEN','AREA_LAND','AREA_PARK','CADNO','ENERGY_CLASS','BLAG_PLAYGROUND','BLAG_SPORT','BLAG_OTHER','OTHER')
    fields_str = ','.join(fieldnames_data)
    f_housedata.write(fields_str+'\n')
    f_housedata.close()
    
    f_housedata = open(f_housedata_name,'ab')
    
    
    csvwriter_housedata = csv.DictWriter(f_housedata, fieldnames=fieldnames_data)
    
    lvl1_ids = get_lvl1_ids(lvl1_link)
    for lvl1_name in lvl1_ids:
        lvl2_ids = get_lvl2_ids('http://www.reformagkh.ru/myhouse?tid=' + lvl1_ids[lvl1_name])
        
        for lvl2_name in lvl2_ids:
            print lvl2_name
            #get list of houses
            houses_ids = get_house_list('http://www.reformagkh.ru/myhouse/list?tid=' + lvl2_ids[lvl2_name] + '&limit=100000')
            
            pbar = ProgressBar(widgets=[Bar('=', '[', ']'), ' ', Counter(), ' of ' + str(len(houses_ids)), ' ', ETA()]).start()
            pbar.maxval = len(houses_ids)
            
            i = 0
            for house_id in houses_ids:
                i = i+1
                res = get_housedata(house_link,str(house_id),lvl1_name,lvl1_ids[lvl1_name],lvl2_name,lvl2_ids[lvl2_name])
                pbar.update(pbar.currval+1)
            pbar.finish()

    f_housedata.close()
    f_errors.close()
