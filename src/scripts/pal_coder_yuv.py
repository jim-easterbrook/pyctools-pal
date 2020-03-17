#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
import sys

from PyQt5 import QtCore, QtWidgets

from pyctools.core.compound import Compound
import pyctools.components.io.dumpmetadata
import pyctools.components.io.rawfilewriter
import pyctools.components.io.videofilereader2
import pyctools.components.pal.coder
import pyctools.components.qt.qtdisplay

class ComponentNetwork(Compound):
    positions = {'audit': (110.0, 60.0),
                 'coder': (-50.0, -50.0),
                 'display': (110.0, -50.0),
                 'reader': (-220.0, -50.0),
                 'writer': (110.0, -160.0)}
    expanded = {'coder': False}
    user_config = {
        'writer': {'fourcc': 'Y16',
                   'path': '/home/jim/Documents/projects/pyctools/pyctools-pal/coded_pal.y16'},
        'reader': {'noaudit': True,
                   'path': '/home/jim/Documents/projects/pyctools/pyctools-pal/BBC_pal/circ_newpat_component.mov'},
        }


    def __init__(self):
        super(ComponentNetwork, self).__init__(
            audit = pyctools.components.io.dumpmetadata.DumpMetadata(),
            display = pyctools.components.qt.qtdisplay.QtDisplay(),
            writer = pyctools.components.io.rawfilewriter.RawFileWriter(),
            coder = pyctools.components.pal.coder.CoderCore(),
            reader = pyctools.components.io.videofilereader2.VideoFileReader2(),
            linkages = {('coder', 'output'): [('display', 'input'),
                                              ('writer', 'input_Y_RGB'),
                                              ('audit', 'input')],
                        ('reader', 'output_UV'): [('coder', 'input_UV')],
                        ('reader', 'output_Y_RGB'): [('coder', 'input_Y')]}
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
