#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.pal.decoder
import pyctools.components.qt.qtdisplay
import pyctools.components.io.videofilereader
import pyctools.components.io.dumpmetadata

class Network(object):
    def __init__(self):
        self.components = \
{   'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': '{}',
                 'pos': (350.0, 150.0)},
    'decoder': {   'class': 'pyctools.components.pal.decoder.Decoder',
                   'config': '{}',
                   'pos': (200.0, 150.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': '{}',
                   'pos': (500.0, 150.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': '/home/jim/Documents/projects/pyctools-pal/coded_pal.avi', '16bit': 'on', 'type': 'Y', 'looping': 'repeat'}",
                      'pos': (50.0, 150.0)}}
        self.linkages = \
{   ('audit', 'output'): ('display', 'input'),
    ('decoder', 'output'): ('audit', 'input'),
    ('filereader', 'output'): ('decoder', 'input')}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])()
            cnf = comps[name].get_config()
            for key, value in eval(component['config']).items():
                cnf[key] = value
            comps[name].set_config(cnf)
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    from PyQt4 import QtGui
    from PyQt4.QtCore import Qt
    QtGui.QApplication.setAttribute(Qt.AA_X11InitThreads)
    app = QtGui.QApplication([])

    logging.basicConfig(level=logging.DEBUG)
    comp = Network().make()
    cnf = comp.get_config()
    parser = argparse.ArgumentParser()
    cnf.parser_add(parser)
    args = parser.parse_args()
    cnf.parser_set(args)
    comp.set_config(cnf)
    comp.start()
    app.exec_()
    comp.stop()
    comp.join()
