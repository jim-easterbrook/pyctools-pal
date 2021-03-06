#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
import sys

from PyQt5 import QtCore, QtWidgets

from pyctools.core.compound import Compound
import pyctools.components.deinterlace.weston3field
import pyctools.components.io.dumpmetadata
import pyctools.components.io.videofilereader2
import pyctools.components.pal.common
import pyctools.components.pal.decoder
import pyctools.components.qt.qtdisplay

class ComponentNetwork(Compound):
    positions = {'audit': (420.0, 260.0),
                 'decoder': (160.0, 150.0),
                 'deint': (420.0, 150.0),
                 'display': (550.0, 150.0),
                 'filereader': (30.0, 150.0),
                 'resample': (290.0, 150.0)}
    expanded = {'decoder': False, 'resample': False}
    user_config = {
        'display': {'framerate': 50, 'stats': True, 'title': 'Simple PAL'},
        'filereader': {'format': 'Y',
                       'looping': 'repeat',
                       'noaudit': True,
                       'path': '/home/jim/Documents/projects/pyctools/pyctools-pal/coded_pal.y16',
                       'zperiod': 4},
        }


    def __init__(self):
        super(ComponentNetwork, self).__init__(
            audit = pyctools.components.io.dumpmetadata.DumpMetadata(),
            decoder = pyctools.components.pal.decoder.Decoder(),
            deint = pyctools.components.deinterlace.weston3field.Weston3Field(),
            display = pyctools.components.qt.qtdisplay.QtDisplay(),
            resample = pyctools.components.pal.common.From4Fsc(),
            filereader = pyctools.components.io.videofilereader2.VideoFileReader2(),
            linkages = {('decoder', 'output'): [('resample', 'input')],
                        ('deint', 'output'): [('display', 'input')],
                        ('filereader', 'output_Y_RGB'): [('decoder', 'input')],
                        ('resample', 'output'): [('audit', 'input'),
                                                 ('deint', 'input')]}
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
