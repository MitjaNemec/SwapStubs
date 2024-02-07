#  action_swap_pins.py
#
# Copyright (C) 2024 Mitja Nemec
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

import wx
import pcbnew
import os
import logging
import sys
import math
from .error_dialog_GUI import ErrorDialogGUI


class ErrorDialog(ErrorDialogGUI):
    def SetSizeHints(self, sz1, sz2):
        # DO NOTHING
        pass

    def __init__(self, parent):
        super(ErrorDialog, self).__init__(parent)


class SwapPins(pcbnew.ActionPlugin):
    def __init__(self):
        super(SwapPins, self).__init__()

        self.frame = None

        self.name = "Swap pins"
        self.category = "Modify Drawing PCB and schematics"
        self.description = "Swap selected pins"
        self.icon_file_name = os.path.join(
            os.path.dirname(__file__), 'swap_pins_light.png')
        self.dark_icon_file_name = os.path.join(
            os.path.dirname(__file__), 'swap_pins_dark.png')

        self.debug_level = logging.INFO

        # plugin paths
        self.plugin_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        self.version_file_path = os.path.join(self.plugin_folder, 'version.txt')

        # load the plugin version
        with open(self.version_file_path) as fp:
            self.version = fp.readline()

    def defaults(self):
        pass

    def Run(self):
        # grab PCB editor frame
        self.frame = wx.FindWindowByName("PcbFrame")

        # load board
        board = pcbnew.GetBoard()

        # go to the project folder - so that log will be in proper place
        os.chdir(os.path.dirname(os.path.abspath(board.GetFileName())))

        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        file_handler = logging.FileHandler(filename='swap_pins.log', mode='w')
        handlers = [file_handler]

        # set up logger
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)s %(lineno)d:%(message)s',
                            datefmt='%m-%d %H:%M:%S',
                            handlers=handlers)
        logger = logging.getLogger(__name__)
        logger.info("Plugin executed on: " + repr(sys.platform))
        logger.info("Plugin executed with python version: " + repr(sys.version))
        logger.info("KiCad build version: " + str(pcbnew.GetBuildVersion()))
        logger.info("Plugin version: " + self.version)
        logger.info("Frame repr: " + repr(self.frame))

        sch_frame = wx.FindWindowByName("SchematicFrame")
        if sch_frame is not None:
            logger.info("Closing schematics")
            sch_frame.Close()
            return

        # check if there are precisely two pads selected
        selected_pads = [x for x in pcbnew.GetBoard().GetPads() if x.IsSelected()]
        if len(selected_pads) != 2:
            caption = 'Swap pins'
            message = "More or less than 2 pads selected. Please select exactly two pads and run the script again"
            dlg = wx.MessageDialog(self.frame, message, caption, wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            logger.info("Action plugin canceled. More or less than 2 pads selected.")
            logging.shutdown()
            return

        # are they on the same module
        pad1 = selected_pads[0]
        pad2 = selected_pads[1]
        if pad1.GetParent().GetReference() != pad2.GetParent().GetReference():
            caption = 'Swap pins'
            message = "Pads don't belong to the same footprint"
            dlg = wx.MessageDialog(self.frame, message, caption, wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            logger.info("Action plugin canceled. Selected pads don't belong to the same footprint.")
            logging.shutdown()
            return

        # swap pins
        try:
            swap_pins.swap(board, pad1, pad2)
            logging.shutdown()
        except (ValueError, LookupError) as error:
            caption = 'Swap pins'
            message = str(error)
            dlg = wx.MessageDialog(self.frame, message, caption, wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            logger.exception("Gracefully handled error while running")
            logging.shutdown()
        except Exception:
            logger.exception("Fatal error when swapping pins")
            caption = 'Swap pins'
            message = "Fatal error when swapping pins.\n"\
                    + "You can raise an issue on GiHub page.\n" \
                    + "Please attach the swap_pins.log which you should find in the project folder."
            dlg = wx.MessageDialog(self.frame, message, caption, wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            logging.shutdown()
            logging.shutdown()
            return


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self, *args, **kwargs):
        """No-op for wrapper"""
        pass
