
from collections import namedtuple

Region = namedtuple('Region', 'id formalname shortname')
Area = namedtuple('Area', 'id formalname shortname')
City = namedtuple('City', 'id formalname shortname')
Street = namedtuple('Street', 'id, formalname shortname')

class AddressItem:
    def __init__(self, item, data=None):
        self.item = item
        self.data = data

    def __eq__(self, other):
        if self.item.__class__ != other.item.__class__:
            return False
        else:
            return self.item.id == other.item.id

    def __rep__(self):
        return "AddressItem(item=%r, data=%r)" % (self.item, self.data)

    def __str__(self):
        return self.__rep__()

    def __hash__(self):
        return hash(self.__rep__())


class Address:
    def __init__(self, region, area, city, street, data=None):
        self.region = region
        self.area = area
        self.city = city
        self.street = street
        self.data = data

    def __eq__(self, other):
        if self.region !=other.region:
            return False
        if self.area != other.area:
            return False
        if self.city != other.city:
            return False
        if self.street != other.street:
            return False

        return True


    def __rep__(self):
        return "Address(region=%r, area=%r, city=%r, street=%r, data=%r)" % (self.region. self.area, self.city, self.street, self.data)

    def __str__(self):
        return self.__rep__()


class AddressTree():
    def __init__(self):
        self.tree = dict()


    def add_item(self, address):
        region = address.region
        area = address.area
        city = address.city
        street = address.street

        subtree = self.tree
        for level in [region, area, city, street]:
            try:
                subtree = subtree[level]
            except KeyError:
                subtree[level] = dict()
                subtree = subtree[level]

        subtree['data'] = address.data
        

    def __rep__(self):
        return "AddressTree(%r)" % (self.tree)

    def __str__(self):
        return self.__rep__()


if __name__ == "__main__":
    # Some examples:
    r = Region('rr', 'edf', 'fgfg')
    a = Area('gg', 'edf', 'fgfg')
    c = City('cc', 'edf', 'fgfg')
    s = Street('ss', 'edf', 'fgfg')


    adr = Address(r, a, c, s, data="New house with black walls")
    t = AddressTree()

    t.add_item(adr)
    print(t)

