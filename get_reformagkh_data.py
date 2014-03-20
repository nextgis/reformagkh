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
    mkdtable = mkdtables[0]
    trs = mkdtable.findAll("table")
    
    #GENERAL - mkd-table1,2
    
    area = maininfo
    area_live = NULL
    area_nonlive = NULL
    area_general = NULL
    cad_no = NULL
    year = 2004
    status = NULL
    mgmt_company = ""
    mgmt_company_link = ""
    
    
    #PASSPORT - mkd-table3
    ##GENERAL
    serie = NULL
    descript = NULL
    name = NULL
    type = NULL
    year2 = NULL
    wall_mat = NULL
    perekr_type = NULL
    levels = NULL
    doors = NULL
    elevators = NULL
    area2 = NULL
    area_live_total = NULL
    area_live_priv = NULL
    area_live_munic = NULL
    area_live_state = NULL
    area_nonlive = NULL
    area_uch = NULL
    area_near = NULL
    no_inventory = NULL
    cad_no2 = NULL
    apts = NULL
    people = NULL
    accounts = NULL
    constr_feat = NULL
    heat_fact = NULL
    heat_norm = NULL
    energy_class = NULL
    energy_audit_date = NULL
    privat_date = NULL
    
    wear_tot = NULL
    wear_fundament = NULL
    wear_walls = NULL
    wear_perekr = NULL
    state = NULL
    
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
    csvwriter_housedata.writerow(dict(HOUSE_ID=house_id,
                                      ADDRESS=address,
                                      NAME=name.encode("utf-8"),
                                      RANK=rank.encode("utf-8"),
                                      ADR=adr.encode("utf-8"),
                                      PHONE=phone,
                                      PHONE_ADD=phone_add,
                                      OFFSET=offset))


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
    fieldnames_data = ("MAN_ID","NAME","IMG","ADR","RANK","PHONE","PHONE_ADD","OFFSET")
    csvwriter_housedata = csv.DictWriter(f_housedata, fieldnames=fieldnames_data)
    
    res = get_housedata(link,house_id)

    f_housedata.close()
