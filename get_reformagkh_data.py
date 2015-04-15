#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# get_reformagkh_data.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Grab reformagkh.ru data on buildings, put it in the CSV table.
# Created: 18.03.2014
# Usage example: python get_reformagkh_data.py
# ---------------------------------------------------------------------------

from bs4 import BeautifulSoup
import urllib2
import csv
from progressbar import *
from httplib import BadStatusLine,IncompleteRead
import socket


def console_out(text):
    #write httplib error messages to console
    time_current = datetime.datetime.now()
    timestamp = time_current.strftime('%Y-%m-%d %H:%M:%S')
    
    f_errors.write(timestamp + ": "+ text)

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
  res = tr.findAll("td")[1].text.strip()
      
  return res

def extract_value_descr(trs,num):
  #extract value for description field
  tr = trs[num]
  res = tr.findAll("td")[0].findAll("span")[1].text.strip()

  return res

def extract_value_constr(trs,num):
  #extract value for construction features field

  #TODO deal with popup text boxes that might(?) contain more information, currently only first non-null <p> is being returned
  tr = trs[num]
  res = tr.findAll("td")[0].text.strip()  

  return res

def extract_value_area(trs,num):
  #extract values for various living area
  tr = trs[num]
  
  area_live_total = tr.find("td").find("span").text.split(" - ")[1]
  trs = tr.findAll("tr")
  area_live_priv = trs[1].text.strip()
  area_live_munic = trs[3].text.strip()
  area_live_state = trs[5].text.strip()

  return area_live_total,area_live_priv,area_live_munic,area_live_state

def extract_value_heat(trs,num):
  #extract values for heat exchange
  trs = trs[num].findAll("tr")

  heat_fact = trs[1].text.strip()
  heat_norm = trs[3].text.strip()

  return heat_fact,heat_norm

def get_housedata(link,house_id,lvl1_name,lvl1_id,lvl2_name,lvl2_id):
    #process house data to get main attributes
    res = urlopen_house(link + "view/" + house_id,house_id)
    
    if res != False:
        soup = BeautifulSoup(''.join(res))
        
        address = soup.find("div", { "class" : "loc_name float-left width650 word-wrap-break-word" }).text.strip()
        
        #GENERAL
        div = soup.find("div", { "class" : "fr" })
        tables = div.findAll("table")
        table0 = tables[0]
        trs = table0.findAll("tr")

        mgmt_company = trs[0].findAll("td")[1].text.strip()              #gen8 Домом управляет
        if trs[0].findAll("td")[1].find("a"):
            mgmt_company_link = "http://www.reformagkh.ru" + trs[0].findAll("td")[1].find("a")['href']
        else:
            mgmt_company_link = ""

        status = trs[1].findAll("td")[1].text.strip()                    #gen7 Состояние дома

        table2 = tables[2]
        trs = table2.findAll("tr")
        area = trs[1].findAll("td")[1].text.strip()                      #gen1 Общая площадь
        cad_no = trs[3].findAll("td")[1].text.strip()                    #gen5 Кадастровый номер
        year = trs[5].findAll("td")[1].text.strip()                      #gen6 Год ввода в экспл

        table3 = tables[3]
        trs = table3.findAll("tr")        
        lastupdate = trs[1].findAll("td")[1].text.strip()                #gen2 Последнее изменение анкеты
        servicedate_start = trs[3].findAll("td")[1].text.strip()         #gen3 Дата начала обслуживания дома
        servicedate_end = trs[5].findAll("td")[1].text.strip()           #gen4 Плановая дата прекращения обслуживания дома

        #TODO extract lat/long coords

        #PASSPORT
        ##GENERAL
        divs = soup.findAll("div", { "class" : "numbered" })
        div0 = divs[0]
        trs = div0.findAll("tr")

        serie = extract_value(trs, 1)                            #1 Серия
        descript = extract_value_descr(trs, 2)                   #2 Описание местоположения
        house_name = extract_value(trs, 4)                       #3 Индивидуальное наименование дома
        house_type = extract_value(trs, 6)                       #4 Тип жилого дома
        year2 = extract_value(trs, 8)                            #5 Год ввода в эксплуатацию
        wall_mat = extract_value(trs, 10)                        #6 Материал стен
        perekr_type = extract_value(trs, 12)                     #7 Тип перекрытий
        levels = extract_value(trs, 14)                          #8 Этажность
        doors = extract_value(trs, 16)                           #9 Количество подъездов
        elevators = extract_value(trs, 18)                       #10 Количество лифтов
        area2 = extract_value(trs, 20)                           #11 Общая площадь
        area_live_total,area_live_priv,area_live_munic,area_live_state = extract_value_area(trs, 21)        #12 Площадь жилых помещений
        area_nonlive2 = extract_value(trs, 29)                   #13 Площадь нежилых помещений
        area_uch = extract_value(trs, 31)                        #14 Площадь участка
        area_near = extract_value(trs, 33)                       #15 Площадь придомовой территории
        no_inventory = extract_value(trs, 35)                    #16 Инвентарный номер
        cad_no2 = extract_value(trs, 37)                         #17 Кадастровый номер участка
        apts = extract_value(trs, 39)                            #18 Количество квартир
        people = extract_value(trs, 41)                          #19 Количество жителей
        accounts = extract_value(trs, 43)                        #20 Количество лицевых счетов
        constr_feat = extract_value_constr(trs,44)               #21 Конструктивные особенности дома
        heat_fact,heat_norm = extract_value_heat(trs,45)         #22 Удельная тепловая характеристика здания
        energy_class = extract_value(trs, 51)                    #23 Класс энергоэффективности
        energy_audit_date = extract_value(trs, 53)               #24 Дата проведения энергетического аудита
        privat_date = extract_value(trs, 55)                     #25 Дата начала приватизации
        
        div_sub = soup.find("div", { "class" : "rating_block fr w475" })
        table = div_sub.find("table")
        trs = div_sub.findAll("tr")

        wear_tot = extract_value(trs,1)                          #stat1 Общая степень износа
        wear_fundament = extract_value(trs,3)                    #stat2 Степень износа фундамента
        wear_walls = extract_value(trs,5)                        #stat3 Степень износа несущих стен
        wear_perekr = extract_value(trs,7)                       #stat4 Степень износа перекрытий
        state = ""                                                 #stat5 TODO, тут был общий статус, возможно его больше нет, надо проверить
        
        ##CONSTRUCTION

        ###Facade
        div1 = divs[1]
        trs = div1.findAll("tr")

        facade_area_tot = extract_value(trs,1)                   #1
        facade_area_sht = extract_value(trs,3)                   #2
        facade_area_unsht = extract_value(trs,5)                 #3
        facade_area_panel = extract_value(trs,7)                 #4
        facade_area_plit = extract_value(trs,9)                  #5
        facade_area_side = extract_value(trs,11)                  #6
        facade_area_wood = extract_value(trs,13)                  #7
        facadewarm_area_sht = extract_value(trs,15)               #8
        facadewarm_area_plit = extract_value(trs,17)              #9
        facadewarm_area_side = extract_value(trs,19)              #10
        facade_area_otmost = extract_value(trs,21)                #11
        facade_garea_glassw = extract_value(trs,23)               #12
        facade_garea_glassp = extract_value(trs,25)               #13
        facade_iarea_glassw = extract_value(trs,27)               #14
        facade_iarea_glassp = extract_value(trs,29)               #15
        facade_area_door_met = extract_value(trs,31)              #16
        facade_area_door_oth = extract_value(trs,33)              #17
        facade_capfix_year = extract_value(trs,35)                #18

        ###Roof
        div2 = divs[2]
        trs = div2.findAll("tr")

        roof_area_tot = extract_value(trs,1)                     #19
        roof_area_shif = extract_value(trs,3)                    #20
        roof_area_met = extract_value(trs,5)                     #21
        roof_area_oth = extract_value(trs,7)                     #22
        roof_area_flat = extract_value(trs,9)                    #23
        roof_capfix_year = extract_value(trs,11)                  #24
        
        ###Basement
        div3 = divs[3]
        trs = div3.findAll("tr")

        base_descr = extract_value(trs,1)                        #25
        base_area = extract_value(trs,3)                         #26
        base_capfix_year = extract_value(trs,5)                  #27

        ###Public areas
        div4 = divs[4]
        trs = div4.findAll("tr")

        publ_area = extract_value(trs,1)                         #28
        publ_capfix_year = extract_value(trs,3)                  #29

        ###Trash
        div5 = divs[5]
        trs = div5.findAll("tr")

        trash_num = extract_value(trs,1)                         #30
        trash_capfix_year = extract_value(trs,3)                 #31

        ##UTILITIES
        
        ###heating
        
        ###hot water
        
        ###cold water
        
        ###sewage
        
        ###electricity
        
        ###gas
        
        
        ##ELEVATORS
        
        #MANAGEMENT
        #res = urllib2.urlopen(link + "/management/" + house_id)
        #soup = BeautifulSoup(''.join(res))
        
        #FINANCE
        #res = urllib2.urlopen(link + "/finance/" + house_id)
        #soup = BeautifulSoup(''.join(res))
        
        #write to output
        csvwriter_housedata.writerow(dict(HOUSE_ID=house_id,
                                          ADDRESS=address.encode("utf-8"),
                                          AREA=area.encode("utf-8"),
                                          CAD_NO=cad_no.encode("utf-8"),
                                          YEAR=year.encode("utf-8"),
                                          STATUS=status.encode("utf-8"),
                                          MGMT_COMPANY=mgmt_company.encode("utf-8"),
                                          MGMT_COMPANY_LINK=mgmt_company_link.encode("utf-8"),
                                          LASTUPDATE=lastupdate.encode("utf-8"),
                                          SERVICEDATE_START=servicedate_start.encode("utf-8"),
                                          SERVICEDATE_END=servicedate_end.encode("utf-8"),
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
                                          CONSTR_FEAT=constr_feat.encode("utf-8"),
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
                                          FACADE_AREA_TOT=facade_area_tot.encode("utf-8"),
                                          FACADE_AREA_SHT=facade_area_sht.encode("utf-8"),
                                          FACADE_AREA_UNSHT=facade_area_unsht.encode("utf-8"),
                                          FACADE_AREA_PANEL=facade_area_panel.encode("utf-8"),
                                          FACADE_AREA_PLIT=facade_area_plit.encode("utf-8"),
                                          FACADE_AREA_SIDE=facade_area_side.encode("utf-8"),
                                          FACADE_AREA_WOOD=facade_area_wood.encode("utf-8"),
                                          FACADEWARM_AREA_SHT=facadewarm_area_sht.encode("utf-8"),
                                          FACADEWARM_AREA_PLIT=facadewarm_area_plit.encode("utf-8"),
                                          FACADEWARM_AREA_SIDE=facadewarm_area_side.encode("utf-8"),
                                          FACADE_AREA_OTMOST=facade_area_otmost.encode("utf-8"),
                                          FACADE_GAREA_GLASSW=facade_garea_glassw.encode("utf-8"),
                                          FACADE_GAREA_GLASSP=facade_garea_glassp.encode("utf-8"),
                                          FACADE_IAREA_GLASSW=facade_iarea_glassw.encode("utf-8"),
                                          FACADE_IAREA_GLASSP=facade_iarea_glassp.encode("utf-8"),
                                          FACADE_AREA_DOOR_MET=facade_area_door_met.encode("utf-8"),
                                          FACADE_AREA_DOOR_OTH=facade_area_door_oth.encode("utf-8"),
                                          FACADE_CAPFIX_YEAR=facade_capfix_year.encode("utf-8"),
                                          ROOF_AREA_TOT=roof_area_tot.encode("utf-8"),
                                          ROOF_AREA_SHIF=roof_area_shif.encode("utf-8"),
                                          ROOF_AREA_MET=roof_area_met.encode("utf-8"),
                                          ROOF_AREA_OTH=roof_area_oth.encode("utf-8"),
                                          ROOF_AREA_FLAT=roof_area_flat.encode("utf-8"),
                                          ROOF_CAPFIX_YEAR=roof_capfix_year.encode("utf-8"),
                                          BASE_DESCR=base_descr.encode("utf-8"),
                                          BASE_AREA=base_area.encode("utf-8"),
                                          BASE_CAPFIX_YEAR=base_capfix_year.encode("utf-8"),
                                          PUBL_AREA=publ_area.encode("utf-8"),
                                          PUBL_CAPFIX_YEAR=publ_capfix_year.encode("utf-8"),
                                          TRASH_NUM=trash_num.encode("utf-8"),
                                          TRASH_CAPFIX_YEAR=trash_capfix_year.encode("utf-8"),
                                          LVL1_NAME=lvl1_name.encode("utf-8"),
                                          LVL1_ID=lvl1_id,
                                          LVL1_LINK="http://www.reformagkh.ru/myhouse?tid=" + lvl1_id,
                                          LVL2_NAME=lvl2_name.encode("utf-8"),
                                          LVL2_ID=lvl2_id,
                                          LVL2_LINK="http://www.reformagkh.ru/myhouse/list?tid=" + lvl2_id,
                                          HOUSE_LINK="http://www.reformagkh.ru/myhouse/view/" + house_id))

def get_lvl1_ids(link):
    
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    trs = soup.findAll("tr",{ "class" : "left" })
    
    lvl1_ids = {}
    for tr in trs:
        loc = tr.findAll("td")[1]
        if loc.find("a"):
            name_loc = loc.find("a").text.strip()
            id_loc = loc.find("a")['href'].replace("?tid=","")
            lvl1_ids[name_loc] = id_loc
    
    return lvl1_ids

def get_lvl2_ids(link):
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    trs = soup.findAll("tr",{ "class" : "left" })
    
    lvl2_ids = {}
    for tr in trs:
        loc = tr.findAll("td")[1]
        if loc.find("a"):
            name_loc = loc.find("a").text.strip()
            if loc.find("a").has_attr('href'):
                id_loc = loc.find("a")['href'].replace("?tid=","")
                lvl2_ids[name_loc] = id_loc
    
    return lvl2_ids

def get_house_list(link):
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    houses_ids = []
    tds = soup.findAll("td")
    for td in tds:
        if td.find("a") is not None:
            if td.find("a").has_attr("href") and 'myhouse' in td.find("a")['href']:
                house_id = td.find("a")['href'].split("/")[3]
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
    fieldnames_data = ("HOUSE_ID","ADDRESS","AREA","CAD_NO","YEAR","STATUS","MGMT_COMPANY","MGMT_COMPANY_LINK","LASTUPDATE","SERVICEDATE_START","SERVICEDATE_END","SERIE","DESCRIPT","HOUSE_NAME","HOUSE_TYPE","YEAR2","WALL_MAT","PEREKR_TYPE","LEVELS","DOORS","ELEVATORS","AREA2","AREA_LIVE_TOTAL","AREA_LIVE_PRIV","AREA_LIVE_MUNIC","AREA_LIVE_STATE","AREA_NONLIVE2","AREA_UCH","AREA_NEAR","NO_INVENTORY","CAD_NO2","APTS","PEOPLE","ACCOUNTS","CONSTR_FEAT","HEAT_FACT","HEAT_NORM","ENERGY_CLASS","ENERGY_AUDIT_DATE","PRIVAT_DATE","WEAR_TOT","WEAR_FUNDAMENT","WEAR_WALLS","WEAR_PEREKR","STATE","FACADE_AREA_TOT","FACADE_AREA_SHT","FACADE_AREA_UNSHT","FACADE_AREA_PANEL","FACADE_AREA_PLIT","FACADE_AREA_SIDE","FACADE_AREA_WOOD","FACADEWARM_AREA_SHT","FACADEWARM_AREA_PLIT","FACADEWARM_AREA_SIDE","FACADE_AREA_OTMOST","FACADE_GAREA_GLASSW","FACADE_GAREA_GLASSP","FACADE_IAREA_GLASSW","FACADE_IAREA_GLASSP","FACADE_AREA_DOOR_MET","FACADE_AREA_DOOR_OTH","FACADE_CAPFIX_YEAR","ROOF_AREA_TOT","ROOF_AREA_SHIF","ROOF_AREA_MET","ROOF_AREA_OTH","ROOF_AREA_FLAT","ROOF_CAPFIX_YEAR","BASE_DESCR","BASE_AREA","BASE_CAPFIX_YEAR","PUBL_AREA","PUBL_CAPFIX_YEAR","TRASH_NUM","TRASH_CAPFIX_YEAR","LVL1_NAME","LVL1_ID","LVL1_LINK","LVL2_NAME","LVL2_ID","LVL2_LINK","HOUSE_LINK")
    fields_str = ",".join(fieldnames_data)
    f_housedata.write(fields_str+'\n')
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