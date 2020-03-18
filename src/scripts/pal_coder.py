#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
import sys

from PyQt5 import QtCore, QtWidgets

from pyctools.core.compound import Compound
import pyctools.components.io.dumpmetadata
import pyctools.components.io.videofilereader2
import pyctools.components.io.videofilewriter2
import pyctools.components.pal.coder
import pyctools.components.pal.common
import pyctools.components.qt.qtdisplay

class ComponentNetwork(Compound):
    positions = {'audit': (110.0, 60.0),
                 'coder': (-20.0, -50.0),
                 'display': (110.0, -50.0),
                 'filereader': (-280.0, -50.0),
                 'filewriter': (110.0, -160.0),
                 'resample': (-150.0, -50.0)}
    expanded = {'coder': False, 'resample': False}
    user_config = {
        'filewriter': {'input': 'Y',
                       'path': '/home/jim/Documents/projects/pyctools/pyctools-pal/coded_pal.y16',
                       'pix_fmt': 'gray16le'},
        'filereader': {'format': 'RGB',
                       'noaudit': True,
                       'path': '/home/jim/Videos/test_seqs/mobcal.avi'},
        }


    def __init__(self):
        super(ComponentNetwork, self).__init__(
            filewriter = pyctools.components.io.videofilewriter2.VideoFileWriter2(),
            audit = pyctools.components.io.dumpmetadata.DumpMetadata(),
            coder = pyctools.components.pal.coder.Coder(),
            display = pyctools.components.qt.qtdisplay.QtDisplay(),
            resample = pyctools.components.pal.common.To4Fsc(),
            filereader = pyctools.components.io.videofilereader2.VideoFileReader2(),
            linkages = {('coder', 'output'): [('filewriter', 'input_Y_RGB'),
                                              ('display', 'input'),
                                              ('audit', 'input')],
                        ('filereader', 'output_Y_RGB'): [('resample', 'input')],
                        ('resample', 'output'): [('coder', 'input')]}
            )

if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = QtWidgets.QApplication(sys.argv)

    comp = ComponentNetwork()
    comp.set_config(comp.user_config)
    cnf = comp.get_config()
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cnf.parser_add(parser)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='increase verbosity of log messages')
    args = parser.parse_args()
    logging.basicConfig(level=logging.ERROR - (args.verbose * 10))
    del args.verbose
    cnf.parser_set(args)
    comp.set_config(cnf)
    comp.start()
    app.exec_()

    comp.stop()
    comp.join()
