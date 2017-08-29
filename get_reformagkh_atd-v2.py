#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

#******************************************************************************
# get_reformagkh_atd.py
# ---------------------------------------------------------
# Grabs reformagkh.ru data on administrative division which is further used for data grabbing.
# More: https://github.com/nextgis/reformagkh
#
# Usage: 
#      usage: get_reformagkh_atd.py [-h] [-o ORIGINALS_FOLDER] output_name
#      where:
#           -h           show this help message and exit
#           output_name  Where to store the results (path to CSV file)
#            -of ORIGINALS_FOLDER  Folder to save original html files. Skip saving if empty.
# Examples:
#      python get_reformagkh_atd.py -o data_orig data/atd.csv
#
# Copyright (C) 2014-2017 Maxim Dubinin (maxim.dubinin@nextgis.com)
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
import socket
import argparse
import re
import requesocks
from stem import Signal
from stem.control import Controller

parser = argparse.ArgumentParser()
parser.add_argument('output_name', help='Where to store the results (path to CSV file)')
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
    
def get_ids(link):

    res = get_content(link)
    soup = BeautifulSoup(''.join(res), 'html.parser')
    captcha = check_captcha(soup)
    
    while captcha == True:
        res = get_content(link)
        soup = BeautifulSoup(''.join(res), 'html.parser')
        captcha = check_captcha(soup)
        change_proxy()
    
    if args.originals_folder:
        name = link.split('=')[1]
        f = open(args.originals_folder + name + ".html","wb")
        f.write(res.encode('utf-8'))
        f.close()
    
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
    
def check_captcha(soup):
    captcha = soup.find('form', { 'name' : 'request_limiter_captcha'})    
    if captcha != None or u'Каптча' in soup.text or 'captcha' in str(soup): 
        return True
    else:
        return False
        
def change_proxy():
    with Controller.from_port(port = 9151) as controller:
            controller.authenticate(password="password")
            controller.signal(Signal.NEWNYM)
    
if __name__ == '__main__':
    session = requesocks.session()
    session.proxies = {'http':  'socks5://127.0.0.1:9150',
                       'https': 'socks5://127.0.0.1:9150'}
    try:
        session.get('http://google.com').text
    except:
        print('Tor isn\'t running or not configured properly. Read README.md')
        sys.exit(1)

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
