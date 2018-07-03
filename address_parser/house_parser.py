#!/usr/bin/env python

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
    parser.add_argument('filename', metavar='f', help='Name for data file')

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


def add_row_to_tree(tree, row):
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


def main():
    args = parse_args()

    filename = args.filename
    data = read_csv(filename)

    tree = AddressTree()
    for row in data:
        add_row_to_tree(tree, row)

    # print(tree.tree.keys())
    print(tree)



if __name__ == "__main__":
    main()
