#  action_swap_pins.py
#
# Copyright (C) 2018 Mitja Nemec
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
from __future__ import absolute_import, division, print_function
import pcbnew
import os
import math
from operator import itemgetter
import re
import logging
import sys

logger = logging.getLogger(__name__)


def swap(board, pad_1, pad_2):
    logger.info("Starting swap_pins")

    # get all file paths
    pcb_file = os.path.abspath(str(board.GetFileName()))
    root_sch_file = os.path.abspath(str(board.GetFileName()).replace(".kicad_pcb", ".sch"))

    logger.info("main sch file is: " + root_sch_file)
    logger.info("main pcb file is: " + pcb_file)

    # get pad numbers
    pad_nr_1 = pad_1.GetPadName()
    pad_nr_2 = pad_2.GetPadName()
    net_1 = pad_1.GetNet()
    net_2 = pad_2.GetNet()
    net_name_1 = net_1.GetNetname().split('/')[-1]
    net_name_2 = net_2.GetNetname().split('/')[-1]

    # get module
    footprint = pad_2.GetParent()
    footprint_reference = footprint.GetReference()

    logger.info("Swaping pins: " + pad_nr_1 + ", " + pad_nr_2 +
                " on: " + footprint_reference + " on nets: " + net_name_1 + ", " + net_name_2)

    fp_sch_file = footprint.GetSheetfile()

    # get symbol from file

    # get the number of units

    # grab the pins

    # select only relevant pins
    relevant_pins = [(), ()]
    for pin in symbol_pins:
        if pin[2] == pad_nr_1:
            relevant_pins[0] = pin
        if pin[2] == pad_nr_2:
            relevant_pins[1] = pin

    logger.info("Relevant pins are: name: " + relevant_pins[0][1] + ", number: " + relevant_pins[0][2] + "; " +
                                   "name: " + relevant_pins[1][1] + ", number: " + relevant_pins[1][2])

    unit_1 = relevant_pins[0][9]
    unit_2 = relevant_pins[1][9]

    # check wheather any of the pins to swap are marked as common pins in multi unit symbol
    if unit_1 == "0" or unit_2 == "0":
        logger.info("Swapping common pins of multi unit symbol is not supported!\n" +
                     "If the symbol has single unit, there is an error in symbol pin definitions!")
        raise ValueError("Swapping common pins of multi unit symbol is not supported!\n" +
                         "If the symbol has single unit, there is an error in symbol pin definitions!")

    logger.info("Relevant pins are on units: " + unit_1 + ", " + unit_2)

    # get the pages of correcsponding unit
    page_1 = [x for x in relevant_sch_files if x[1] == unit_1][0][0]
    page_1_loc = [x for x in relevant_sch_files if x[1] == unit_1][0][2]
    page_2 = [x for x in relevant_sch_files if x[1] == unit_2][0][0]
    page_2_loc = [x for x in relevant_sch_files if x[1] == unit_2][0][2]

    logger.info("Unit 1 on page: " + page_1 +
                " at: " + str(page_1_loc[0]) + ", " + str(page_1_loc[1]))
    logger.info("Unit 2 on page: " + page_2 +
                " at: " + str(page_2_loc[0]) + ", " + str(page_2_loc[1]))

    # get pin locations within schematics
    pin_1_loc = (str(int(page_1_loc[0]) + int(relevant_pins[0][3])), str(int(page_1_loc[1]) - int(relevant_pins[0][4])))
    pin_2_loc = (str(int(page_2_loc[0]) + int(relevant_pins[1][3])), str(int(page_2_loc[1]) - int(relevant_pins[1][4])))

    logger.info("Pin 1 at: " + str(pin_1_loc[0]) + ", " + str(pin_1_loc[1]))
    logger.info("Pin 2 at: " + str(pin_2_loc[0]) + ", " + str(pin_2_loc[1]))

    # get pin orientation in the symbol U=3 R=0 D=1 L=2
    pin_1_rot = relevant_pins[0][6]
    pin_2_rot = relevant_pins[1][6]
    if pin_1_rot == 'R':
        pin_1_rot = '0'
    elif pin_1_rot == 'D':
        pin_1_rot = '1'
    elif pin_1_rot == 'L':
        pin_1_rot = '2'
    elif pin_1_rot == 'U':
        pin_1_rot = '3'
    if pin_2_rot == 'R':
        pin_2_rot = '0'
    elif pin_2_rot == 'D':
        pin_2_rot = '1'
    elif pin_2_rot == 'L':
        pin_2_rot = '2'
    elif pin_2_rot == 'U':
        pin_2_rot = '3'

    logger.info("Pin 1 rotation: " + pin_1_rot)
    logger.info("Pin 2 rotation: " + pin_2_rot)

    # load schematics
    with open(page_1, 'rb') as f:
        file_contents = f.read().decode('utf-8')
        shematics_1 = file_contents.split('\n')
    # parse it and find text labels at pin locations
    list_line_1 = []
    for index, line in enumerate(shematics_1):
        if line.startswith('Text '):
            line_fields = line.split()
            if line_fields[1] == 'Label' or line_fields[1] == 'GLabel' or line_fields[1] == 'HLabel':
                line_index_1 = index
                next_line_1 = shematics_1[line_index_1 + 1]
                # if label is precisely at pin location
                if line_fields[2] == pin_1_loc[0] and line_fields[3] == pin_1_loc[1]:
                    list_line_1.append((line, next_line_1, line_index_1, 0.0))
                    logger.info("Found label at pin 1")
                # or if label text matches the net name and is close enoght
                # TODO if the label does not match the net name then we have a problem
                if next_line_1.rstrip() == net_name_1:
                    label_location = (line_fields[2], line_fields[3])
                    distance = get_distance(pin_1_loc, label_location)
                    list_line_1.append((line, next_line_1, line_index_1, distance))
                    logger.info("Found label near pin 1")

    # remove duplicates
    list_line_1 = list(set(list_line_1))
    logger.info("list_line_1="+repr(list_line_1))
    # find closest label
    if len(list_line_1) == 0:
        line_1 = None
    if len(list_line_1) == 1:
        line_1 = list_line_1[0]
    if len(list_line_1) > 1:
        line_1 = min(list_line_1, key=itemgetter(3))

    with open(page_2, 'rb') as f:
        file_contents = f.read().decode('utf-8')
        shematics_2 = file_contents.split('\n')

    list_line_2 = []
    for index, line in enumerate(shematics_2):
        if line.startswith('Text '):
            line_fields = line.split()
            if line_fields[1] == 'Label' or line_fields[1] == 'GLabel' or line_fields[1] == 'HLabel':
                line_index_2 = index
                next_line_2 = shematics_2[line_index_2 + 1]
                # if label is precisely at pin location
                if line_fields[2] == pin_2_loc[0] and line_fields[3] == pin_2_loc[1]:
                    list_line_2.append((line, next_line_2, line_index_2, 0.0))
                    logger.info("Found label at pin 2")
                # or if label text matches the net name and is close enoght
                if next_line_2.rstrip() == net_name_2:
                    label_location = (line_fields[2], line_fields[3])
                    distance = get_distance(pin_2_loc, label_location)
                    list_line_2.append((line, next_line_2, line_index_2, distance))
                    logger.info("Found label near pin 2")

    # remove duplicates
    list_line_2 = list(set(list_line_2))
    logger.info("list_line_2="+repr(list_line_2))
    # find closest label
    if len(list_line_2) == 0:
        line_2 = None
    if len(list_line_2) == 1:
        line_2 = list_line_2[0]
    if len(list_line_2) > 1:
        line_2 = min(list_line_2, key=itemgetter(3))

    # swap the labels
    if line_1 is None and line_2 is None:
        logger.info("Could not find the pins connection. \nEither the pins are disconnected or they are connected through short wire segment\nand net name was overriden by some other label.")
        raise ValueError("It makes no sense in swapping two disconneted pins!")
    # if both pins are connected, just swap them
    # if pins are on the same page
    if page_1 == page_2:
        logger.info("Swapping on the same page")
        if line_1 is not None and line_2 is not None:
            logger.info("Both pins are connected")
            new_shematics = list(shematics_1)
            new_shematics[line_1[2]+1] = line_2[1]
            new_shematics[line_2[2]+1] = line_1[1]
        # otherwise you have to move the pin to new location
        elif line_1 is None:
            logger.info("Only pin 2 is connected")
            new_shematics = list(shematics_1)
            line_fields = line_2[0].split()
            line_fields[4] = pin_1_rot
            line_fields[2] = pin_1_loc[0]
            line_fields[3] = pin_1_loc[1]
            new_shematics[line_2[2]] = " ".join(line_fields) + "\n"
        elif line_2 is None:
            logger.info("Only pin 1 is connected")
            new_shematics = list(shematics_1)
            line_fields = line_1[0].split()
            line_fields[4] = pin_2_rot
            line_fields[2] = pin_2_loc[0]
            line_fields[3] = pin_2_loc[1]
            new_shematics[line_1[2]] = " ".join(line_fields) + "\n"

        logger.info("Labels swapped")

        # save schematics
        if __name__ == "__main__":
            sch_file_to_write = os.path.join(os.path.dirname(page_1),
                                             'temp_' + os.path.basename(page_1))
        else:
            sch_file_to_write = page_1
        with open(sch_file_to_write, 'wb') as f:
            f.write("\n".join(new_shematics).encode('utf-8'))
        logger.info("Saved the schematics in same file.")

    # pins are on different pages
    else:
        logger.info("Swapping on the different pages")
        # easy case, label are on both pages, just swap names
        if line_1 is not None and line_2 is not None:
            logger.info("Both pins are connected")
            new_shematics_1 = list(shematics_1)
            new_shematics_2 = list(shematics_2)
            new_shematics_1[line_1[2]+1] = line_2[1]
            new_shematics_2[line_2[2]+1] = line_1[1]
        # hard cases, cut label from one page, and paste it at the end of the other page
        elif line_1 is None:
            logger.info("Only pin 2 is connected")
            new_shematics_2 = list(shematics_2[:line_2[2]] + shematics_2[line_2[2]+2:])
            line_fields = shematics_2[line_2[2]].split()
            line_fields[4] = pin_1_rot
            line_fields[2] = pin_1_loc[0]
            line_fields[3] = pin_1_loc[1]
            new_lines = [" ".join(line_fields) + "\n", shematics_2[line_2[2]+1]]
            new_shematics_1 = list(shematics_1[:-1] + new_lines + shematics_1[-1:])
        elif line_2 is None:
            logger.info("Only pin 1 is connected")
            new_shematics_1 = list(shematics_1[:line_1[2]] + shematics_1[line_1[2]+2:])
            line_fields = shematics_1[line_1[2]].split()
            line_fields[4] = pin_2_rot
            line_fields[2] = pin_2_loc[0]
            line_fields[3] = pin_2_loc[1]
            new_lines = [" ".join(line_fields) + "\n", shematics_1[line_1[2]+1]]
            new_shematics_2 = list(shematics_2[:-1] + new_lines + shematics_2[-1:])

        logger.info("Labels swapped")

        # save schematics
        if __name__ == "__main__":
            filename1 = os.path.basename(page_1).replace(".sch", "_temp.sch")
            sch_file_to_write_1 = os.path.join(os.path.dirname(page_1), filename1)
            filename2 = os.path.basename(page_2).replace(".sch", "_temp.sch")
            sch_file_to_write_2 = os.path.join(os.path.dirname(page_2), filename2)
        else:
            sch_file_to_write_1 = page_1
            sch_file_to_write_2 = page_2
        with open(sch_file_to_write_1, 'wb') as f:
            f.write("\n".join(new_shematics_1).encode('utf-8'))
        with open(sch_file_to_write_2, 'wb') as f:
            f.write("\n".join(new_shematics_2).encode('utf-8'))
        logger.info("Saved the schematics in different files.")

    # swap nets in layout
    # Select PADa -> Properties.Copy NetName
    net_1 = pad_1.GetNet()
    net_2 = pad_2.GetNet()
    pad_2.SetNet(net_1)
    pad_1.SetNet(net_2)
    logger.info("Pad nets swapped")

    # save board
    if __name__ == "__main__":
        pcb_file_to_write = board.GetFileName().replace(".kicad_pcb", "_temp.kicad_pcb")
        pcbnew.SaveBoard(pcb_file_to_write, board)
    logger.info("Saved the layout.")



