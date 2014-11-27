#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.qt.qtdisplay
import pyctools.components.io.videofilewriter
import pyctools.components.pal.common
import pyctools.components.io.videofilereader
import pyctools.components.pal.coder
import pyctools.components.io.dumpmetadata

class Network(object):
    def __init__(self):
        self.components = \
{   'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': '{}',
                 'pos': (300.0, -50.0)},
    'coder': {   'class': 'pyctools.components.pal.coder.Coder',
                 'config': '{}',
                 'pos': (0.0, -50.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'framerate': 40}",
                   'pos': (450.0, -50.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': '/home/jim/Videos/test_seqs/mobcal.avi'}",
                      'pos': (-300.0, -50.0)},
    'filewriter': {   'class': 'pyctools.components.io.videofilewriter.VideoFileWriter',
                      'config': "{'path': '/home/jim/Documents/projects/pyctools-pal/coded_pal.avi', '16bit': 'on', 'encoder': '-c:v ffv1 -pix_fmt gray16le'}",
                      'pos': (150.0, -50.0)},
    'resample': {   'class': 'pyctools.components.pal.common.To4Fsc',
                    'config': "{'xdown': 351, 'xup': 461}",
                    'pos': (-150.0, -50.0)}}
        self.linkages = \
{   ('audit', 'output'): ('display', 'input'),
    ('coder', 'output'): ('filewriter', 'input'),
    ('filereader', 'output'): ('resample', 'input'),
    ('filewriter', 'output'): ('audit', 'input'),
    ('resample', 'output'): ('coder', 'input')}

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
