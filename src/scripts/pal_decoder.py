#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
import sys

from PyQt5 import QtCore, QtWidgets

from pyctools.core.compound import Compound
import pyctools.components.io.dumpmetadata
import pyctools.components.io.videofilereader
import pyctools.components.pal.common
import pyctools.components.pal.decoder
import pyctools.components.qt.qtdisplay

class Network(object):
    components = \
{   'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': '{}',
                 'pos': (420.0, 260.0)},
    'decoder': {   'class': 'pyctools.components.pal.decoder.Decoder',
                   'config': "{'setlevel': {'func': '(data - pt_float(64)) * "
                             "pt_float(255.0 / 140.0)'}, 'filterY': {'resize': "
                             "{}, 'fildes': {'frequency': '0.0,  0.215, 0.22, "
                             "0.23, 0.25, 0.27, 0.28,  0.285, 0.5', 'gain': "
                             "'1.0,  1.0,   0.8,  0.0,  0.0,  0.0,  0.8,   "
                             "1.0,   1.0', 'weight': '0.01, 0.01,  0.01, 0.1,  "
                             "1.0,  0.1,  0.005, 0.005, 0.01', 'aperture': "
                             "13}}, 'yuvrgb': {'matrix': '601'}, 'matrix': {}, "
                             "'demod': {}, 'filterUV': {'resize': {}, "
                             "'filgen': {'xaperture': 12, 'xcut': 22}}}",
                   'expanded': False,
                   'pos': (160.0, 150.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'stats': True}",
                   'pos': (420.0, 150.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': "
                                "'/home/jim/Documents/projects/pyctools/pyctools-pal/coded_pal.avi', "
                                "'looping': 'repeat', 'type': 'Y', '16bit': "
                                "True, 'noaudit': True, 'zperiod': 4}",
                      'pos': (30.0, 150.0)},
    'resample': {   'class': 'pyctools.components.pal.common.From4Fsc',
                    'config': "{'resize': {'xup': 351, 'xdown': 461}, "
                              "'filgen': {'xup': 351, 'xdown': 461, "
                              "'xaperture': 12}}",
                    'expanded': False,
                    'pos': (290.0, 150.0)}}
    linkages = \
{   ('decoder', 'output'): [('resample', 'input')],
    ('filereader', 'output'): [('decoder', 'input')],
    ('resample', 'output'): [('audit', 'input'), ('display', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = QtWidgets.QApplication(sys.argv)

    comp = Network().make()
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
