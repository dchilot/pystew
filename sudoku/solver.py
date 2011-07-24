"""Naive Sudoku solver."""

#!/usr/bin/python

# -*- coding: utf-8 -*-

#Copyright (c) 2011 'pystew developpers'
#
#This software is provided 'as-is', without any express or implied
#warranty. In no event will the authors be held liable for any damages
#arising from the use of this software.
#
#Permission is granted to anyone to use this software for any purpose,
#including commercial applications, and to alter it and redistribute it
#freely, subject to the following restrictions:
#
#    1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
#
#    2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
#
#    3. This notice may not be removed or altered from any source
#    distribution.

#
#$Rev::               $: Revision of last commit
#$Author::            $: Author of last commit
#$Date::              $: Date of last commit

import sys
import os
path_to_more =  os.path.join(os.path.join(os.curdir, ".."), "regexp")
sys.path.insert(0, path_to_more)
import logging
import logger

from PyQt4 import QtGui
import PyQt4

class Pair(object):
    def __init__(self, x, y, custom_hash = None):
        self._x = x
        self._y = y
        if (custom_hash is None):
            self._hash = self._x * 10 + self._y
        else:
            self._hash = custom_hash

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def __hash__(self):
        return self._hash

class Grid(object):
    def __init__(self):
        self._grid = []
        for x in range(0, 9):
            line = []
            for y in range(0, 9):
                line.append(Cell(x, y, self))
            self._grid.append(line)
        self._notified = set()
        self._not_refreshed = set()
        for x in range(0, 9):
            for y in range(0, 9):
                self._not_refreshed.add(Pair(x, y))
        self._need_refresh = False

    def assert_coordinate(self, c):
        try:
            assert(c >= 0)
            assert(c < 9)
        except Exception as e:
            pass

    def get_at(self, x, y):
        self.assert_coordinate(x)
        self.assert_coordinate(y)
        return self._grid[x][y]

    def get_range(self, c):
        if (c < 3):
            return (range(0, 3), 1)
        elif (c < 6):
            return (range(3, 6), 2)
        else:
            return (range(6, 9), 3)

    def get_outer_range(self, c):
        if (c < 3):
            return (range(3, 9), 1)
        elif (c < 6):
            return (range(0, 3) + range(6, 9), 2)
        else:
            return (range(0, 6), 3)

    def _refresh(self, level = 0):
        # check for extra constraints
        regions = set()
        horizontals = set()
        verticals = set()
        for notified in self._notified:
            x = notified.get_x()
            y = notified.get_y()
            x_range, x_hash = self.get_range(x)
            y_range, y_hash = self.get_range(y)
            region_hash = x_hash * 10 + y_hash
            pair = Pair(x_range, y_range, region_hash)
            regions.add(pair)
            horizontal_hash = y * 100
            pair = Pair(range(0, 9), [y], horizontal_hash)
            horizontals.add(pair)
            vertical_hash = x * 100
            pair = Pair([x], range(0, 9), vertical_hash)
            verticals.add(pair)
        self._notified = set()

        need_refresh = False
        all = set()
        for r in regions:
            all.add(r)
        for r in horizontals:
            all.add(r)
        for r in verticals:
            all.add(r)
        for r in all:
            unsolved = set()
            solved = set()
            extra = False
            for x in r.get_x():
                for y in r.get_y():
                    cell = self.get_at(x, y)
                    if (cell.get_is_solved()):
                        solved.add(cell)
                    else:
                        unsolved.add(cell)
                        extra = True
            if (extra):
                # at least one cell is not solved
                used = set()
                for cell in solved:
                    used.add(cell.get_value())
                unused = set(range(1, 10)) - used
                logging.debug('unused = ' + str(unused))
                for needed in unused:
                    possible_users = []
                    impossible_users = []
                    for un in unsolved:
                        if (needed in un.get_possibles()):
                            possible_users.append(un)
                        else:
                            impossible_users.append(un)
                    length = len(possible_users)
                    assert(0 != length) # big problem
                    if (1 == length):
                        possible_users[0].set_value(needed)
                        need_refresh = True

        def extra_line():
            if (extra):
                # at least one cell is not solved
                unused = []
                to_remove_from_others = []
                reverse = {}
                base_used = set()
                for i in range(0, 3):
                    for cell in solved[i]:
                        base_used.add(cell.get_value())
                for i in range(0, 3):
                    t = []
                    if (len(unsolved[i]) > 0):
                        n = set(range(1, 10)) - base_used
                        remove_from_n = []
                        if (len(n) > 0):
                            for not_used_yet in n:
                                possible_cells = []
                                for free_cell in unsolved[i]:
                                    if (not_used_yet in 
                                            free_cell.get_possibles()):
                                        possible_cells.append(free_cell)
                                length = len(possible_cells)
                                if (0 == length):
                                    remove_from_n.append(not_used_yet)
                            for remove in remove_from_n:
                                n.remove(remove)
                            if (len(n) == len(unsolved[i])):
                                for only_possible_here in n:
                                    t.append(only_possible_here)
                                    need_refresh = True
                    else:
                        n = []
                    # plan to remove values that have to be used here from  
                    # the rest of the line
                    to_remove_from_others.append(t)
                    unused.append(n)
                for i in range(0, 3):
                    for j in range(0, 3):
                        if (i != j):
                            for cell in unsolved[j]:
                                for value in to_remove_from_others[i]:
                                    cell.remove(value)

        for h in horizontals:
            extra = False
            solved = []
            unsolved = []
            y = h.get_y()[0]
            for i in range(0, 3):
                s = []
                u = []
                for x in range(i * 3, (i + 1) * 3):
                    cell = self.get_at(x, y)
                    if (cell.get_is_solved()):
                        s.append(cell)
                    else:
                        u.append(cell)
                        extra = True
                solved.append(s)
                unsolved.append(u)
            extra_line()

        for v in verticals:
            extra = False
            solved = []
            unsolved = []
            x = h.get_x()[0]
            for i in range(0, 3):
                s = []
                u = []
                for y in range(i * 3, (i + 1) * 3):
                    cell = self.get_at(x, y)
                    if (cell.get_is_solved()):
                        s.append(cell)
                    else:
                        u.append(cell)
                        extra = True
                solved.append(s)
                unsolved.append(u)
            extra_line()

        if (need_refresh):
            self._refresh(level + 1)
            self._need_refresh = True

    def notify(self, x, y, value, force_refresh = False):
        self.assert_coordinate(x)
        self.assert_coordinate(y)
        pair = Pair(x, y)
        self._notified.add(pair)
        # process cells in the neighbourhood
        for cx in self.get_range(x)[0]:
            for cy in self.get_range(y)[0]:
                if ((x != cx) or (y != cy)):
                    self.get_at(cx, cy).remove(value)

        for lx in self.get_outer_range(x)[0]:
            self.get_at(lx, y).remove(value)

        for ly in self.get_outer_range(y)[0]:
            self.get_at(x, ly).remove(value)

        if (force_refresh):
            self._refresh()

    def refresh_all(self):
        self._normal = False
        self._notified = self._not_refreshed
        self._refresh()
        while (self._need_refresh):
            self._need_refresh = False
            self._refresh()

class Cell(object):
    def __init__(self, x, y, grid):
        self._possibles = set(range(1, 10))
        self._value = None
        self._label = None
        self._x = x
        self._y = y
        self._grid = grid

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_possibles(self):
        return self._possibles

    def get_is_solved(self):
        return (self._value is not None)

    def remove(self, value):
        if ((self._value is None) and (value in self._possibles)):
            logging.debug("remove %s from cell (%s, %s)" %
                (value, self._x, self._y))
            self._possibles.remove(value)
            length = len(self._possibles)
            if (1 == length):
                only = None
                for v in self._possibles:
                    only = v
                self.set_value(only)

    def set_value(self, value, force_refresh = False):
        #assert(self._value is None)
        assert(value > 0)
        assert(value <= 9)
        self._value = value
        self._possibles = [value]
        if (self._label is not None):
            self._label.setText(str(self))
        self._grid.notify(self._x, self._y, self._value, force_refresh)
        if (force_refresh):
            self._grid.refresh_all()

    def get_value(self):
        return self._value

    def set_label(self, label):
        self._label = label

    def __str__(self):
        if (self._value is None):
            return '?'
        else:
            return str(self._value)

    def __repr__(self):
        string = "_x : " + str(self._x) + " ; _y : " + str(self._y)
        string += " ; _value : " + str(self._value)
        string += " ; _possibles : " + str(self._possibles)
        return string

class Label(QtGui.QLabel):
    def __init__(self, cell):
        QtGui.QLabel.__init__(self, str(cell))
        self._cell = cell
        self._cell.set_label(self)

    def mousePressEvent(self, event):
        logging.debug("Click on cell " + repr(self._cell))
        items = PyQt4.QtCore.QStringList()
        for value in self._cell.get_possibles():
            items.append(str(value))
        text, ok = PyQt4.QtGui.QInputDialog.getItem(self, 
            'Please choose a value for cell (%s, %s)' %
                (self._cell.get_x(), self._cell.get_y()),
            'Value:', items)
        if ok:
            value = int(text)
            logging.info("self._grid.get_at(%s, %s).set_value(%s)#, True)" % 
                (self._cell.get_x(), self._cell.get_y(), value))
            self._cell.set_value(value, True)


class Sudoku(QtGui.QWidget):

    def __init__(self):
        super(Sudoku, self).__init__()

        self._labels = []
        self._grid = Grid()
        
        self.initUI()
        
    def initUI(self):

        self.setWindowTitle('Naive sudoku solver')

        grid = QtGui.QGridLayout()

        for y in range(0, 9):
            labels = []
            for x in range(0, 9):
                label = Label(self._grid.get_at(x, y))
                label.setAlignment(
                    PyQt4.QtCore.Qt.AlignHCenter | PyQt4.QtCore.Qt.AlignVCenter)
                grid.addWidget(label, y, x)
                labels.append(label)
            self._labels.append(labels)

# hard grid
#        self._grid.get_at(2, 1).set_value(5)#, True)
#        self._grid.get_at(2, 2).set_value(3)#, True)
#        self._grid.get_at(0, 3).set_value(7)#, True)
#        self._grid.get_at(1, 3).set_value(3)#, True)
#        self._grid.get_at(2, 5).set_value(9)#, True)
#        self._grid.get_at(2, 6).set_value(7)#, True)
#        self._grid.get_at(1, 7).set_value(6)#, True)
#        self._grid.get_at(0, 7).set_value(8)#, True)
#
#        self._grid.get_at(5, 0).set_value(8)#, True)
#        self._grid.get_at(5, 1).set_value(4)#, True)
#        self._grid.get_at(3, 3).set_value(2)#, True)
#        self._grid.get_at(3, 4).set_value(6)#, True)
#        self._grid.get_at(5, 4).set_value(5)#, True)
#        self._grid.get_at(5, 5).set_value(1)#, True)
#        self._grid.get_at(3, 7).set_value(9)#, True)
#        self._grid.get_at(3, 8).set_value(4)#, True)
#
#        self._grid.get_at(7, 1).set_value(3)#, True)
#        self._grid.get_at(8, 1).set_value(7)#, True)
#        self._grid.get_at(6, 2).set_value(1)#, True)
#        self._grid.get_at(6, 3).set_value(8)#, True)
#        self._grid.get_at(7, 5).set_value(4)#, True)
#        self._grid.get_at(8, 5).set_value(2)#, True)
#        self._grid.get_at(6, 6).set_value(9)#, True)
#        self._grid.get_at(6, 7).set_value(2, True)


# diabolic grid
#        self._grid.get_at(8, 4).set_value(8)#, True)
#        self._grid.get_at(6, 6).set_value(7)#, True)
#        self._grid.get_at(7, 7).set_value(8)#, True)
#        self._grid.get_at(7, 8).set_value(1)#, True)
#        self._grid.get_at(8, 7).set_value(2)#, True)
#        self._grid.get_at(4, 6).set_value(5)#, True)
#        self._grid.get_at(3, 8).set_value(2)#, True)
#        self._grid.get_at(2, 8).set_value(3)#, True)
#        self._grid.get_at(0, 8).set_value(5)#, True)
#        self._grid.get_at(1, 0).set_value(1)#, True)
#        self._grid.get_at(0, 1).set_value(9)#, True)
#        self._grid.get_at(1, 1).set_value(5)#, True)
#        self._grid.get_at(2, 2).set_value(8)#, True)
#        self._grid.get_at(4, 2).set_value(1)#, True)
#        self._grid.get_at(5, 0).set_value(8)#, True)
#        self._grid.get_at(6, 0).set_value(4)#, True)
#        self._grid.get_at(8, 0).set_value(7)#, True)
#        self._grid.get_at(1, 3).set_value(8)#, True)
#        self._grid.get_at(2, 3).set_value(2)#, True)
#        self._grid.get_at(0, 4).set_value(7)#, True)
#        self._grid.get_at(3, 4).set_value(4)#, True)
#        self._grid.get_at(5, 4).set_value(6)#, True)
#        self._grid.get_at(6, 5).set_value(6)#, True)
#        self._grid.get_at(7, 5).set_value(2, True)

# more difficult
#        self._grid.get_at(2, 0).set_value(3)#, True)
#        self._grid.get_at(1, 1).set_value(8)#, True)
#        self._grid.get_at(3, 0).set_value(2)#, True)
#        self._grid.get_at(5, 0).set_value(7)#, True)
#        self._grid.get_at(5, 1).set_value(1)#, True)
#        self._grid.get_at(4, 2).set_value(9)#, True)
#        self._grid.get_at(7, 1).set_value(4)#, True)
#        self._grid.get_at(7, 2).set_value(1)#, True)
#        self._grid.get_at(8, 2).set_value(7)#, True)
#        self._grid.get_at(6, 3).set_value(4)#, True)
#        self._grid.get_at(7, 3).set_value(8)#, True)
#        self._grid.get_at(8, 4).set_value(9)#, True)
#        self._grid.get_at(8, 5).set_value(2)#, True)
#        self._grid.get_at(7, 7).set_value(9)#, True)
#        self._grid.get_at(6, 8).set_value(5)#, True)
#        self._grid.get_at(5, 8).set_value(3)#, True)
#        self._grid.get_at(3, 8).set_value(8)#, True)
#        self._grid.get_at(3, 7).set_value(5)#, True)
#        self._grid.get_at(4, 6).set_value(2)#, True)
#        self._grid.get_at(0, 6).set_value(3)#, True)
#        self._grid.get_at(1, 6).set_value(4)#, True)
#        self._grid.get_at(1, 7).set_value(1)#, True)
#        self._grid.get_at(1, 5).set_value(3)#, True)
#        self._grid.get_at(2, 5).set_value(8)#, True)
#        self._grid.get_at(0, 4).set_value(5)#, True)
#        self._grid.get_at(0, 3).set_value(9, True)
#        # stuck ... 

# again ...
#        self._grid.get_at(0, 2).set_value(4)#, True)
#        self._grid.get_at(1, 2).set_value(3)#, True)
#        self._grid.get_at(3, 2).set_value(1)#, True)
#        self._grid.get_at(3, 1).set_value(4)#, True)
#        self._grid.get_at(5, 1).set_value(3)#, True)
#        self._grid.get_at(6, 0).set_value(5)#, True)
#        self._grid.get_at(8, 1).set_value(1)#, True)
#        self._grid.get_at(7, 2).set_value(8)#, True)
#        self._grid.get_at(1, 3).set_value(1)#, True)
#        self._grid.get_at(2, 3).set_value(7)#, True)
#        self._grid.get_at(1, 4).set_value(8)#, True)
#        self._grid.get_at(1, 6).set_value(6)#, True)
#        self._grid.get_at(0, 7).set_value(8)#, True)
#        self._grid.get_at(2, 8).set_value(9)#, True)
#        self._grid.get_at(3, 7).set_value(6)#, True)
#        self._grid.get_at(4, 8).set_value(5)#, True)
#        self._grid.get_at(5, 7).set_value(7)#, True)
#        self._grid.get_at(5, 6).set_value(2)#, True)
#        self._grid.get_at(7, 6).set_value(5)#, True)
#        self._grid.get_at(8, 6).set_value(4)#, True)
#        self._grid.get_at(7, 5).set_value(6)#, True)
#        self._grid.get_at(6, 5).set_value(7)#, True)
#        self._grid.get_at(7, 4).set_value(1)#, True)
#        self._grid.get_at(5, 3).set_value(4)#, True)
#        self._grid.get_at(4, 4).set_value(3)#, True)
#        self._grid.get_at(3, 5).set_value(8)#, True)
#        self._grid.get_at(4, 0).set_value(9, True)
#        # stuck ... 

# Medium
#        self._grid.get_at(0, 0).set_value(3)#, True)
#        self._grid.get_at(0, 1).set_value(7)#, True)
#        self._grid.get_at(1, 1).set_value(8)#, True)
#        self._grid.get_at(0, 2).set_value(6)#, True)
#        self._grid.get_at(1, 2).set_value(4)#, True)
#        self._grid.get_at(0, 3).set_value(9)#, True)
#        self._grid.get_at(1, 3).set_value(7)#, True)
#        self._grid.get_at(0, 4).set_value(5)#, True)
#        self._grid.get_at(1, 4).set_value(2)#, True)
#        self._grid.get_at(1, 5).set_value(3)#, True)
#        self._grid.get_at(0, 6).set_value(8)#, True)
#        self._grid.get_at(0, 7).set_value(2)#, True)
#        self._grid.get_at(1, 7).set_value(6)#, True)
#        self._grid.get_at(1, 8).set_value(5)#, True)
#        self._grid.get_at(4, 0).set_value(2)#, True)
#        self._grid.get_at(5, 1).set_value(1)#, True)
#        self._grid.get_at(3, 2).set_value(5)#, True)
#        self._grid.get_at(4, 4).set_value(1)#, True)
#        self._grid.get_at(4, 5).set_value(4)#, True)
#        self._grid.get_at(5, 5).set_value(5)#, True)
#        self._grid.get_at(3, 6).set_value(6)#, True)
#        self._grid.get_at(3, 7).set_value(8)#, True)
#        self._grid.get_at(5, 7).set_value(4)#, True)
#        self._grid.get_at(6, 7).set_value(1)#, True)
#        self._grid.get_at(7, 8).set_value(6)#, True)
#        self._grid.get_at(8, 6).set_value(3)#, True)
#        self._grid.get_at(7, 5).set_value(9)#, True)
#        self._grid.get_at(7, 4).set_value(3)#, True)
#        self._grid.get_at(8, 4).set_value(6)#, True)
#        self._grid.get_at(8, 2).set_value(2)#, True)
#        self._grid.get_at(6, 2).set_value(9)#, True)

# super stuck
#        self._grid.get_at(0, 0).set_value(1)#, True)
#        self._grid.get_at(1, 1).set_value(3)#, True)
#        self._grid.get_at(2, 2).set_value(9)#, True)
#        self._grid.get_at(2, 3).set_value(5)#, True)
#        self._grid.get_at(1, 4).set_value(1)#, True)
#        self._grid.get_at(0, 5).set_value(6)#, True)
#        self._grid.get_at(0, 6).set_value(3)#, True)
#        self._grid.get_at(1, 7).set_value(4)#, True)
#        self._grid.get_at(2, 8).set_value(7)#, True)
#        self._grid.get_at(6, 8).set_value(3)#, True)
#        self._grid.get_at(7, 6).set_value(1)#, True)
#        self._grid.get_at(8, 7).set_value(7)#, True)
#        self._grid.get_at(3, 3).set_value(3)#, True)
#        self._grid.get_at(4, 4).set_value(8)#, True)
#        self._grid.get_at(5, 5).set_value(4)#, True)
#        self._grid.get_at(6, 3).set_value(9)#, True)
#        self._grid.get_at(8, 4).set_value(2)#, True)
#        self._grid.get_at(6, 2).set_value(5)#, True)
#        self._grid.get_at(8, 1).set_value(8)#, True)
#        self._grid.get_at(7, 0).set_value(9)#, True)
#        self._grid.get_at(5, 0).set_value(7)#, True)
#        self._grid.get_at(4, 1).set_value(2)#, True)
#        self._grid.get_at(3, 2).set_value(6)#, True)
#        self._grid.get_at(2, 7).set_value(1)#, True)
#        # super stuck

        self.setLayout(grid)
        self.adjustSize()
        new_size = max(self.height(), self.width())
        self.resize(new_size, new_size)
        self.setMinimumSize(new_size, new_size)

app = QtGui.QApplication(sys.argv)
ex = Sudoku()
ex.show()
sys.exit(app.exec_())
