
from collections import namedtuple

from Levenshtein import distance


Region = namedtuple('Region', 'id formalname shortname')
Area = namedtuple('Area', 'id formalname shortname')
City = namedtuple('City', 'id formalname shortname')
Street = namedtuple('Street', 'id, formalname shortname')
House = namedtuple('House', 'id, number building block letter address')

class AddressItem:
    def __init__(self, item, data=None):
        self.item = item
        self.data = data

    def get_item_parts(self):
        parts = [s for s in self.item]
        return parts


    def distance(self, other):
        p1 = self.get_item_parts()
        p2 = other.get_item_parts()
        # drop Id:
        p1 = p1[1: ]
        p2 = p2[1: ]

        dists = []
        for i in range(len(p1)):
            s1 = p1[i] if p1[i] != "" else None
            s2 = p2[i] if p2[i] != "" else None
            if (s1 is not None) and (s2 is not None):
                dists.append(float(distance(s1, s2))/max(len(s1), len(s2)))

        return dists



    def __eq__(self, other):
        if self.item.__class__ != other.item.__class__:
            return False
        else:
            return self.item.id == other.item.id

    def __repr__(self):
        return 'AddressItem(item={item!r}, data={data!r})'.format(item=self.item, data=self.data)

    def __hash__(self):
        return hash(self.__repr__())


class Address:
    def __init__(self, region, area, city, street, house, data=None):
        self.region = region
        self.area = area
        self.city = city
        self.street = street
        self.house = house
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
        if self.house != other.house:
            return False

        return True


    def __repr__(self):
        return "Address(region={self.region!r}, area={self.area!r}, city={self.city!r}, street={self.street!r}, house={self.house!r}, data={self.data!r})"



class AddressTree():
    def __init__(self, tree=None):
        if tree is None:
            self.tree = dict()
        else:
            assert isinstance(tree, {}.__class__)
            self.tree = tree


    def add_item(self, address):
        region = address.region
        area = address.area
        city = address.city
        street = address.street
        house = address.house

        subtree = self.tree
        for level in [region, area, city, street, house]:
            try:
                subtree = subtree[level]
            except KeyError:
                subtree[level] = dict()
                subtree = subtree[level]

        subtree['data'] = address.data


    def __repr__(self):
        return "AddressTree(tree=%r)" % (self.tree)


if __name__ == "__main__":
    # Some examples:
    r = AddressItem(Region('rr', 'edf', 'fgfg'))
    a = AddressItem(Area('gg', 'edf', 'fgfg'))
    c = AddressItem(City('cc', 'edf', 'fgfg'))
    s = AddressItem(Street('ss', 'edf', 'fgfg'))
    h = AddressItem(Street('hh', 'edf', 'fgfg'))

    s1 = eval(repr(s))

    adr = Address(r, a, c, s, h, data="New house with black walls")
    t = AddressTree()

    t.add_item(adr)
    print(t)

    t1 = eval(repr(t))

    print(t1)

