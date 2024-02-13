import unittest
import swap_stubs
import pcbnew
import logging
import sys
import os


class TestSwapStubs(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "swap_stubs_test_project"))

    def test_first(self):
        # u101, 15, 14
        logger.info("First swap stub test")
        input_filename = 'swap_stubs_test_project.kicad_pcb'
        out_layout = input_filename.split('.')[0] + "_first" + ".kicad_pcb"
        out_sch = out_layout.replace(".kicad_pcb", "kicad_sch")

        brd = pcbnew.LoadBoard(input_filename)

        # get two pad, ner u101, 15, 14
        fp = brd.FindFootprintByReference('U101')
        pad1 = fp.FindPadByNumber(15)
        pad2 = fp.FindPadByNumber(14)

        brd = swap_stubs.swap(brd, pad1, pad2, out_sch)
        # save the board
        pcbnew.PCB_IO_MGR.Save(pcbnew.PCB_IO_MGR.KICAD_SEXP, out_layout, brd)


if __name__ == '__main__':
    file_handler = logging.FileHandler(filename='swap_stubs.log', mode='w')
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level,
                        format='%(asctime)s %(name)s %(lineno)d:%(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        handlers=handlers
                        )

    logger = logging.getLogger(__name__)
    logger.info("Plugin executed on: " + repr(sys.platform))
    logger.info("Plugin executed with python version: " + repr(sys.version))
    logger.info("KiCad build version: " + str(pcbnew.GetBuildVersion()))

    unittest.main()
