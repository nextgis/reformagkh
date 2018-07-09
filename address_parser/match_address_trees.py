#!/usr/bin/env python
# encoding: utf-8


"""
    Адресная часть - любая часть адреса, начиная с верхнего уровня и
        заканчивая некоторым уровнем. Например: Республика-Район-НаселенныйПункт,
         или Республика-район.
    Адресные части считаются одинаковыми, если:
     * совпадают названия всех уровней адресной части.

    В реальности названия, полученные из разных источников, могут отличаться.
    Цель - сопоставить адреса разных адресных деревьев.

    Логика сопоставления:
        Сравниваются верхние уровни деревьев. Ищем среди них разные варианты
            совпадений, каждой паре соответствий ставится некое число - оценка
            схожести, получаем матрицу оценок (N^2 пар, но матрица
            выйдет симметричная, поэтому на самом деле оценок меньше).
            Из всех возможных матриц выбираем ту, для которой суммарная схожесть
            будет выше, чем для остальных. Принимаем это за рабочую гипотезу.
        Спускаемся на уровень ниже, повторяем процедуру.

        В итоге имеем набор матриц, их сумма - общая оценка качества. Возможно,
            на каком-то шаге придется вернуться к предыдущему уровню и выбрать
            иное соответствие на этом уровне, которое в итоге даст улучшенное
            суммарную оценку по всему дерву.
    """


import argparse

from address import (
    Region, Area, City, Street, House,
    AddressItem, Address,
    AddressTree
)

def parse_args():
    parser = argparse.ArgumentParser(description="Match two address trees")
    parser.add_argument('tree1', help='Name of the first tree file')
    parser.add_argument('tree2', help='Name of the second tree file')

    args = parser.parse_args()

    return args



def main():
    args = parse_args()

    tree1 = args.tree1
    tree2 = args.tree2

    # This is very dangerouse. Use it for your files only!
    t1 = open(tree1).read()
    t1 = eval(t1)

    t2 = open(tree2).read()
    t2 = eval(t2)

    for a1 in t1.get_address_items():
        for a2 in t2.get_address_items():
            print(a1.distance(a2), a1, a2)
        print('')


if __name__ == "__main__":
    main()
