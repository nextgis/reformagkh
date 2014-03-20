#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# grab-policemen-v2.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Grab mvd.ru data on local policemen, creates two tables linked by unique id, policemen and addresses they cover.
# Created: 10.03.2014
# Usage example: python grab-policemen-v2.py 45000000000
# ---------------------------------------------------------------------------

from bs4 import BeautifulSoup
import urllib2
import csv

def get_housedata(link,house_id):
    
    res = urllib2.urlopen(link + "/view/" + house_id)
    soup = BeautifulSoup(''.join(res.read()))
    
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
    mgmt_company_link = "http://www.reformagkh.ru" + trs[3].findAll("td")[1].find("a")['href']  #gen5
    
    
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
    res = urllib2.urlopen(link + "/management/" + house_id)
    soup = BeautifulSoup(''.join(res.read()))
    
    #FINANCE
    res = urllib2.urlopen(link + "/finance/" + house_id)
    soup = BeautifulSoup(''.join(res.read()))
    
    #write to output
    csvwriter_housedata.writerow(dict(HOUSE_ID=cad_no.encode("utf-8"),
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
                                      STATE=state.encode("utf-8")))

def get_addr(div,man_id):
    lis = div.find("ul").findAll("li")
    for li in lis:

        addrsrc = li.text

        csvwriter_addrsrc.writerow(dict(MAN_ID=man_id,
                        ADDR=addrsrc.encode("utf-8")))

        addrs = addrsrc.split(",")
        city = addrs[0].replace(u" (г)","")
        street = addrs[1].split(" (")[0]
        del addrs[0]
        del addrs[0]

        if len(addrs) > 0:
            for addr in addrs:
                res_addr = city + "," + street + "," + addr
                csvwriter_addr.writerow(dict(MAN_ID=man_id,
                        ADDR=res_addr.encode("utf-8")))
        else:
            res_addr = city + "," + street
            csvwriter_addr.writerow(dict(MAN_ID=man_id,
                        ADDR=res_addr.encode("utf-8")))   

def get_photo(photo_url,man_id):
    try:
        u = urllib2.urlopen(photo_url)
    except urllib2.URLError, e:
        
        get_photo_status = False
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    else:
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading photo: %s Kb: %s" % (man_id, file_size/1024)
        f = open("photos/" + str(man_id) + ".jpg","wb")
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,

        f.close()
        get_photo_status = True
    return get_photo_status

if __name__ == '__main__':
    link = "http://www.reformagkh.ru/myhouse/"
    house_id = 8625429

    #init csv for housedata
    f_housedata = open("data/housedata.csv","wb")
    fieldnames_data = ("HOUSE_ID","ADDRESS","AREA","AREA_LIVE","AREA_NONLIVE","AREA_GENERAL","CAD_NO","YEAR","STATUS","MGMT_COMPANY","MGMT_COMPANY_LINK","SERIE","DESCRIPT","HOUSE_NAME","HOUSE_TYPE","YEAR2","WALL_MAT","PEREKR_TYPE","LEVELS","DOORS","ELEVATORS","AREA2","AREA_LIVE_TOTAL","AREA_LIVE_PRIV","AREA_LIVE_MUNIC","AREA_LIVE_STATE","AREA_NONLIVE2","AREA_UCH","AREA_NEAR","NO_INVENTORY","CAD_NO2","APTS","PEOPLE","ACCOUNTS","HEAT_FACT","HEAT_NORM","ENERGY_CLASS","ENERGY_AUDIT_DATE","PRIVAT_DATE","WEAR_TOT","WEAR_FUNDAMENT","WEAR_WALLS","WEAR_PEREKR","STATE")
    csvwriter_housedata = csv.DictWriter(f_housedata, fieldnames=fieldnames_data)
    
    res = get_housedata(link,str(house_id))

    f_housedata.close()
