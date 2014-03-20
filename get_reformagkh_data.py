#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# get_reformagkh_data.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Grab reformagkh.ru data on buildings.
# Created: 18.03.2014
# Usage example: python get_reformagkh_data.py
# ---------------------------------------------------------------------------

from bs4 import BeautifulSoup
import urllib2
import csv
from progressbar import *


def console_out(text):
    time_current = datetime.datetime.now()
    timestamp = time_current.strftime('%Y-%m-%d %H:%M:%S')
    
    f_errors.write(timestamp + ": "+ text)

def urlopen_house(link,id):
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

def get_housedata(link,house_id,lvl1_name,lvl1_id,lvl2_name,lvl2_id):
    res = urlopen_house(link + "/view/" + house_id,house_id)
    
    if res != False:
        soup = BeautifulSoup(''.join(res))
        
        address = soup.find("div", { "class" : "border-block" }).find("h1").find("span").text
        mkdtables = soup.findAll("table", { "class" : "mkd-table" })
        
        
        #GENERAL - mkd-table1,2
        mkdtable = mkdtables[0]
        trs = mkdtable.findAll("tr")

        area = trs[0].findAll("td")[1].text                              #gen1
        area_live = trs[3].findAll("td")[1].text                         #gen2
        area_nonlive = trs[3].findAll("td")[1].text                      #gen3
        area_general = trs[3].findAll("td")[1].text                      #gen4

        mkdtable = mkdtables[1]
        trs = mkdtable.findAll("tr")

        cad_no = trs[0].findAll("td")[1].text                            #gen5
        year = trs[1].findAll("td")[1].text                              #gen6
        status = trs[2].findAll("td")[1].text                            #gen7
        mgmt_company = trs[3].findAll("td")[1].text                      #gen8
        if trs[3].findAll("td")[1].find("a"):
            mgmt_company_link = "http://www.reformagkh.ru" + trs[3].findAll("td")[1].find("a")['href']  #gen5
        else:
            mgmt_company_link = ""
        
        
        #PASSPORT - mkd-table3
        ##GENERAL
        mkdtable = mkdtables[2]
        trs = mkdtable.findAll("tr")

        serie = trs[0].findAll("td")[2].text                            #1
        descript = trs[2].findAll("td")[1].text.strip()                 #2
        house_name = trs[3].findAll("td")[2].text                       #3
        house_type = trs[4].findAll("td")[2].text                       #4
        year2 = trs[5].findAll("td")[2].text                            #5
        wall_mat = trs[6].findAll("td")[2].text                         #6
        perekr_type = trs[7].findAll("td")[2].text                      #7
        levels = trs[8].findAll("td")[2].text                           #8
        doors = trs[9].findAll("td")[2].text                            #9
        elevators = trs[10].findAll("td")[2].text                       #10
        area2 = trs[11].findAll("td")[2].text                           #11
        area_live_total = trs[12].findAll("td")[2].text                 #12
        area_live_priv = trs[13].findAll("td")[2].text                  #12
        area_live_munic = trs[14].findAll("td")[2].text                 #12
        area_live_state = trs[15].findAll("td")[2].text                 #12
        area_nonlive2 = trs[16].findAll("td")[2].text                   #13
        area_uch = trs[17].findAll("td")[2].text                        #14
        area_near = trs[18].findAll("td")[2].text                       #15
        no_inventory = trs[19].findAll("td")[2].text                    #16
        cad_no2 = trs[20].findAll("td")[2].text                         #17
        apts = trs[21].findAll("td")[2].text                            #18
        people = trs[22].findAll("td")[2].text                          #19
        accounts = trs[23].findAll("td")[2].text                        #20
        constr_feat = trs[25].findAll("td")[1].text.strip()             #21
        heat_fact = trs[27].findAll("td")[2].text                       #21
        heat_norm = trs[28].findAll("td")[2].text                       #21
        energy_class = trs[29].findAll("td")[2].text                    #22
        energy_audit_date = trs[30].findAll("td")[2].text               #23
        privat_date = trs[31].findAll("td")[2].text                     #24
        
        statstable = soup.find("table", { "class" : "statistic" })
        trs = statstable.findAll("tr")

        wear_tot = trs[0].findAll("td")[1].text.strip()                  #stat1
        wear_fundament = trs[1].findAll("td")[1].text.strip()            #stat2
        wear_walls = trs[2].findAll("td")[1].text.strip()                #stat3
        wear_perekr = trs[3].findAll("td")[1].text.strip()               #stat4
        state = soup.find("div", { "class" : "block-title" }).find('span').text  #stat4
        
        ##CONSTRUCTION - mkd-table4
        
        ##NETWORKS - mkd-table5
        
        ##ELEVATORS
        
        #MANAGEMENT
        #res = urllib2.urlopen(link + "/management/" + house_id)
        #soup = BeautifulSoup(''.join(res))
        
        #FINANCE
        #res = urllib2.urlopen(link + "/finance/" + house_id)
        #soup = BeautifulSoup(''.join(res))
        
        #write to output
        csvwriter_housedata.writerow(dict(HOUSE_ID=house_id.encode("utf-8"),
                                          ADDRESS=address.encode("utf-8"),
                                          AREA=area.encode("utf-8"),
                                          AREA_LIVE=area_live.encode("utf-8"),
                                          AREA_NONLIVE=area_nonlive.encode("utf-8"),
                                          AREA_GENERAL=area_general.encode("utf-8"),
                                          CAD_NO=cad_no.encode("utf-8"),
                                          YEAR=year.encode("utf-8"),
                                          STATUS=status.encode("utf-8"),
                                          MGMT_COMPANY=mgmt_company.encode("utf-8"),
                                          MGMT_COMPANY_LINK=mgmt_company_link.encode("utf-8"),
                                          SERIE=serie.encode("utf-8"),
                                          DESCRIPT=descript.encode("utf-8"),
                                          HOUSE_NAME=house_name.encode("utf-8"),
                                          HOUSE_TYPE=house_type.encode("utf-8"),
                                          YEAR2=year2.encode("utf-8"),
                                          WALL_MAT=wall_mat.encode("utf-8"),
                                          PEREKR_TYPE=perekr_type.encode("utf-8"),
                                          LEVELS=levels.encode("utf-8"),
                                          DOORS=doors.encode("utf-8"),
                                          ELEVATORS=elevators.encode("utf-8"),
                                          AREA2=area2.encode("utf-8"),
                                          AREA_LIVE_TOTAL=area_live_total.encode("utf-8"),
                                          AREA_LIVE_PRIV=area_live_priv.encode("utf-8"),
                                          AREA_LIVE_MUNIC=area_live_munic.encode("utf-8"),
                                          AREA_LIVE_STATE=area_live_state.encode("utf-8"),
                                          AREA_NONLIVE2=area_nonlive2.encode("utf-8"),
                                          AREA_UCH=area_uch.encode("utf-8"),
                                          AREA_NEAR=area_near.encode("utf-8"),
                                          NO_INVENTORY=no_inventory.encode("utf-8"),
                                          CAD_NO2=cad_no2.encode("utf-8"),
                                          APTS=apts.encode("utf-8"),
                                          PEOPLE=people.encode("utf-8"),
                                          ACCOUNTS=accounts.encode("utf-8"),
                                          HEAT_FACT=heat_fact.encode("utf-8"),
                                          HEAT_NORM=heat_norm.encode("utf-8"),
                                          ENERGY_CLASS=energy_class.encode("utf-8"),
                                          ENERGY_AUDIT_DATE=energy_audit_date.encode("utf-8"),
                                          PRIVAT_DATE=privat_date.encode("utf-8"),
                                          WEAR_TOT=wear_tot.encode("utf-8"),
                                          WEAR_FUNDAMENT=wear_fundament.encode("utf-8"),
                                          WEAR_WALLS=wear_walls.encode("utf-8"),
                                          WEAR_PEREKR=wear_perekr.encode("utf-8"),
                                          STATE=state.encode("utf-8"),
                                          LVL1_NAME=lvl1_name.encode("utf-8"),
                                          LVL1_ID=lvl1_id,
                                          LVL1_LINK="http://www.reformagkh.ru/myhouse?tid=" + lvl1_id,
                                          LVL2_NAME=lvl2_name.encode("utf-8"),
                                          LVL2_ID=lvl2_id,
                                          LVL2_LINK="http://www.reformagkh.ru/myhouse/list?tid=" + lvl2_id,))

def get_lvl1_ids(link):
    
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    locations = soup.findAll("td",{ "class" : "location" })
    lvl1_ids = {}
    for loc in locations:
        name = loc.find("a").text.strip()
        id = loc.find("a")['id'].replace("element_","")
        lvl1_ids[name] = id
    
    return lvl1_ids

def get_lvl2_ids(link):
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    locations = soup.findAll("td",{ "class" : "location" })
    lvl2_ids = {}
    for loc in locations:
        if loc.find("a"):
            name = loc.find("a").text.strip()
            id = loc.find("a")['id'].replace("element_","")
            lvl2_ids[name] = id
    
    return lvl2_ids

def get_house_list(link):
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    houses_ids = []
    houses = soup.findAll("td",{"class":"name"})
    for house in houses:
        house_id = house.find("a")['href'].split("/")[3]
        houses_ids.append(house_id)
    
    return houses_ids
    
if __name__ == '__main__':
    lvl1_link = "http://www.reformagkh.ru/myhouse?tid=2280999&sort=alphabet&item=mkd"
    house_link = "http://www.reformagkh.ru/myhouse/"
    #house_id = 8625429
    
    #init errors.log
    f_errors = open("errors.txt","wb")
    
    #init csv for housedata
    f_housedata = open("data/housedata.csv","wb")
    fieldnames_data = ("HOUSE_ID","ADDRESS","AREA","AREA_LIVE","AREA_NONLIVE","AREA_GENERAL","CAD_NO","YEAR","STATUS","MGMT_COMPANY","MGMT_COMPANY_LINK","SERIE","DESCRIPT","HOUSE_NAME","HOUSE_TYPE","YEAR2","WALL_MAT","PEREKR_TYPE","LEVELS","DOORS","ELEVATORS","AREA2","AREA_LIVE_TOTAL","AREA_LIVE_PRIV","AREA_LIVE_MUNIC","AREA_LIVE_STATE","AREA_NONLIVE2","AREA_UCH","AREA_NEAR","NO_INVENTORY","CAD_NO2","APTS","PEOPLE","ACCOUNTS","HEAT_FACT","HEAT_NORM","ENERGY_CLASS","ENERGY_AUDIT_DATE","PRIVAT_DATE","WEAR_TOT","WEAR_FUNDAMENT","WEAR_WALLS","WEAR_PEREKR","STATE","LVL1_NAME","LVL1_ID","LVL1_LINK","LVL2_NAME","LVL2_ID","LVL2_LINK")
    fields_str = ",".join(fieldnames_data)
    f_housedata.write(fields_str)
    f_housedata.close()
    
    f_housedata = open("data/housedata.csv","ab")
    
    
    csvwriter_housedata = csv.DictWriter(f_housedata, fieldnames=fieldnames_data)
    
    lvl1_ids = get_lvl1_ids(lvl1_link)
    for lvl1_name in lvl1_ids:
        lvl2_ids = get_lvl2_ids("http://www.reformagkh.ru/myhouse?tid=" + lvl1_ids[lvl1_name])
        
        for lvl2_name in lvl2_ids:
            print lvl2_name
            #get list of houses
            houses_ids = get_house_list("http://www.reformagkh.ru/myhouse/list?tid=" + lvl2_ids[lvl2_name] + "&page=no")
            
            pbar = ProgressBar(widgets=[Bar('=', '[', ']'), ' ', Counter(), " of " + str(len(houses_ids)), ' ', ETA()]).start()
            pbar.maxval = len(houses_ids)
            
            i = 0
            for house_id in houses_ids:
                i = i+1
                res = get_housedata(house_link,str(house_id),lvl1_name,lvl1_ids[lvl1_name],lvl2_name,lvl2_ids[lvl2_name])
                pbar.update(pbar.currval+1)
            pbar.finish()

    f_housedata.close()
    f_errors.close()