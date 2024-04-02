#  action_swap_stubs.py
#
# Copyright (C) Mitja Nemec
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
import pcbnew
import os
import logging
import re

try:
    from .sexpdata import loads, dumps
except:
    from sexpdata import loads, dumps


logger = logging.getLogger(__name__)

# copied from https://github.com/psychogenic/kicad-skip
def loadTree(fpath: str):
    with open(fpath, 'r') as f:
        return loads(f.read())

# copied from https://github.com/psychogenic/kicad-skip
def writeTree(fpath: str, tree):
    remove_nones(tree)
    with open(fpath, 'w') as f:
        # no way to pretty print this what the fuck?
        # lines get too long with some schems, when it's all
        # clumped into a bunch
        as_str = dumps(tree)
        for elname in ['property', 'symbol', 'wire', 'data']:
            as_str = re.sub(f'\(\s*{elname}', f'\n({elname}', as_str)
        f.write(as_str)

# copied from https://github.com/psychogenic/kicad-skip
def list_splice(target, start, delete_count=None, *items):
    """Remove existing elements and/or add new elements to a list.

    target        the target list (will be changed)
    start         index of starting position
    delete_count  number of items to remove (default: len(target) - start)
    *items        items to insert at start index

    Returns a new list of removed items (or an empty list)
    https://gist.github.com/jonbeebe/44a529fcf15d6bda118fe3cfa434edf3
    """
    if delete_count == None:
        delete_count = len(target) - start

    # store removed range in a separate list and replace with *items
    total = start + delete_count
    removed = target[start:total]
    target[start:total] = items

    return removed

# copied from https://github.com/psychogenic/kicad-skip
def remove_nones(alist):
    targets = []
    for i in range(len(alist)):
        el = alist[i]
        if el is None:
            targets.append(i)
        elif isinstance(el, list):
            remove_nones(el)

    if not len(targets):
        return
    for killme in sorted(targets, reverse=True):
        list_splice(alist, killme, 1)

    return

class Swapper:
    def __init__(self):
        pass

    def swap(self, board, pad_1, pad_2, out_sch=None):
        logger.info("Starting swap_stubs")

        # get all file paths
        pcb_file = os.path.abspath(str(board.GetFileName()))
        root_sch_file = os.path.abspath(str(board.GetFileName()).replace(".kicad_pcb", ".kicad_sch"))
        prj_folder = os.path.dirname(pcb_file)

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
        footprint = pcbnew.Cast_to_FOOTPRINT(pad_2.GetParent())
        footprint_reference = footprint.GetReference()

        logger.info("Swaping labels on pads: " + pad_nr_1 + ", " + pad_nr_2 +
                    " on fp: " + footprint_reference + " connected to: " + net_name_1 + ", " + net_name_2)

        fp_sch_file = os.path.join(prj_folder, footprint.GetSheetfile())

        if out_sch is None:
            out_sch = fp_sch_file
        logger.info(f"Schematics file to write: {out_sch}")

        # get symbol from file
        sch_raw = loadTree(fp_sch_file)

        # get the symbols
        for item in sch_raw:
            if str(item[0]) == 'symbol':
                for prop in item:
                    if prop[1] == 'Reference':
                        if prop[2] == footprint_reference:
                            sym = item
                            sym_lib_id = item[1][1]
        # get the symbol location
        for prop in sym:
            a = str(prop[0])
            if str(prop[0]) == 'at':
                sym_pos = (prop[1], prop[2])
        logger.info(f"Symbol position: {repr(sym_pos)}")

        # get lib symbol
        for item in sch_raw:
            a = str(item[0])
            if str(item[0]) == 'lib_symbols':
                for lib_sym in item[1:]:
                    if lib_sym[1] == sym_lib_id:
                        library_symbol = lib_sym

        # get pin locations
        for item in library_symbol:
            b = item
            if isinstance(item, list):
                for subitem in item:
                    if isinstance(subitem, list):
                        if str(subitem[0]) == 'pin':
                            if subitem[6][1] == pad_nr_1:
                                pin_1 = subitem
                                pin_1_loc = (subitem[3][1], subitem[3][2])
                            if subitem[6][1] == pad_nr_2:
                                pin_2 = subitem
                                pin_2_loc = (subitem[3][1], subitem[3][2])

        # calculate absolute pin positions
        pin_1_pos = [sum(x) for x in zip(sym_pos, pin_1_loc)]
        pin_2_pos = [sum(x) for x in zip(sym_pos, pin_2_loc)]
        logger.info(f"Pin positions: {repr(pin_1_pos)}, {repr(pin_2_pos)}")

        # TODO check wheather any of the pins to swap are marked as common pins in multi unit symbol

        # find matching labels
        # TODO grab any kind of labels (local, global, hierarchical) - then swap label type as needed
        # todo grab location of this data to modify it later
        net_1 = []
        net_2 = []
        net_1_indices = []
        net_2_indices = []
        for i in range(len(sch_raw)):
            item = sch_raw[i]
            item_index = i
            if isinstance(item, list):
                if str(item[0]) == 'label':
                    if item[1] == net_name_1:
                        net_1.append(item)
                        net_1_indices.append(item_index)
                    if item[1] == net_name_2:
                        net_2.append(item)
                        net_2_indices.append(item_index)

        logger.info(f"net 1 labels: {repr(net_1)}")
        logger.info(f"net 2 labels: {repr(net_2)}")

        # find closes label
        distance_max = 1000000000
        for n in net_1:
            i = net_1.index(n)
            net_pos = (n[2][1], n[2][2])
            delta = tuple(x-y for x, y in zip(pin_1_pos, net_pos))
            distance = abs(delta[0]) + abs(delta[1])
            if distance < distance_max:
                closest_net_1 = n
                net_1_index = net_1_indices[i]
                distance_max = distance
        distance_max = 1000000000
        for n in net_2:
            i = net_2.index(n)
            net_pos = (n[2][1], n[2][2])
            delta = tuple(x-y for x, y in zip(pin_2_pos, net_pos))
            distance = abs(delta[0]) + abs(delta[1])
            if distance < distance_max:
                closest_net_2 = n
                net_2_index = net_2_indices[i]
                distance_max = distance
        logger.info(f"closest label 1: {repr(closest_net_1)}")
        logger.info(f"closest label 2: {repr(closest_net_2)}")

        # TODO figure out the orientation and fix them appropriately
        # TODO add support for swapping labels on different symbols
        # TODO add support for swapping labels on different schematic pages

        # swap label positions
        closest_net_1[2], closest_net_2[2] = closest_net_2[2], closest_net_1[2]

        # save the schematics
        writeTree(out_sch, sch_raw)
        logger.info(f"Schematics written")

        # swap nets in layout
        net_1 = pad_1.GetNet()
        net_2 = pad_2.GetNet()
        pad_2.SetNet(net_1)
        pad_1.SetNet(net_2)
        logger.info("Pad nets swapped")

        return board





