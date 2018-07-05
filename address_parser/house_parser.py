#!/usr/bin/env python
# encoding: utf-8

"""
Parse addresses, construct adress tree:
> house_parser.py export-reestrmkd-16-20180701.csv
"""

import argparse

from collections import namedtuple
from csv import DictReader

from address import (
    Region, Area, City, Street, House,
    AddressItem, Address,
    AddressTree
)

def parse_args():
    parser = argparse.ArgumentParser(description="Parse reformagkh.ru house data")
    parser.add_argument('filename', help='Name for data file')
    parser.add_argument('format', choices=['reforma', 'osm'], help='Format of data file')

    args = parser.parse_args()
    
    return args

def read_csv(filename):
    data = []
    tree = dict()
    with open(filename) as csvfile:
        reader = DictReader(csvfile, delimiter=';')
        for row in reader:
            data.append(row)

    return data


def add_reforma_row_to_tree(tree, row):
    region = Region(id=row['region_id'], formalname=row['formalname_region'], shortname=row['shortname_region'])
    area = Area(id=row['area_id'], formalname=row['formalname_area'], shortname=row['shortname_area'])
    city = City(id=row['city_id'], formalname=row['formalname_city'], shortname=row['shortname_city'])
    street = Street(id=row['street_id'], formalname=row['formalname_street'], shortname=row['shortname_street'])
    house = House(id=row['houseguid'], number=row['house_number'], building=row['building'], block=row['block'], letter=row['letter'], address=row['address'])

    region = AddressItem(region)
    area = AddressItem(area)
    city = AddressItem(city)
    street = AddressItem(street)

    address = Address(region, area, city, street, house, data=row)

    tree.add_item(address)


def add_osm_row_to_tree(tree, row):
    """Example of a row of osm data file: 

        fid
        BUILDING
        A_STRT
        A_SBRB
        A_HSNMBR
        B_LEVELS
        NAME
        NAME_1
        NAME_EN
        NAME_RU
        PLACE
        A_CNTR
        A_RGN
        A_DSTRCT
        A_PSTCD
        xcoord
        ycoord

        1
        yes
        улица Ленина

        69

        Наш
        Васильево
        Vasilyevo
        Васильево
        village
        RU
        Татарстан
        Зеленодольский район
        422530
        48.6504681
        55.8315631


    """
    region = Region(id=None, formalname=row['A_RGN'], shortname=None)
    area = Area(id=None, formalname=row['A_DSTRCT'], shortname=None)
    city = City(id=None, formalname=row['NAME'], shortname=None)
    street = Street(id=None, formalname=row['A_STRT'], shortname=None)
    house = House(id=None, number=row['A_HSNMBR'], building=None, block=None, letter=None, address=None)

    region = AddressItem(region)
    area = AddressItem(area)
    city = AddressItem(city)
    street = AddressItem(street)

    address = Address(region, area, city, street, house, data=row)

    tree.add_item(address)



def main():
    args = parse_args()

    filename = args.filename

    fmt = args.format
    if fmt == 'reforma':
        add_row_to_tree = add_reforma_row_to_tree
    elif fmt == 'osm':
        add_row_to_tree = add_osm_row_to_tree
    else:
        raise ValueError('Unknown data file format: %s', (format, ))

    data = read_csv(filename)

    tree = AddressTree()
    for row in data:
        add_row_to_tree(tree, row)

    # print(tree.tree.keys())
    print(tree)



if __name__ == "__main__":
    main()
