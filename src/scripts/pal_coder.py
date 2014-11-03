#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import logging
from pyctools.core.compound import Compound
import pyctools.components.io.videofilereader
import pyctools.components.io.videofilewriter
import pyctools.components.pal.common
import pyctools.components.qt.qtdisplay
import pyctools.components.io.dumpmetadata
import pyctools.components.pal.coder
import pyctools.components.colourspace.rgbtoyuv

class Network(object):
    def __init__(self):
        self.components = \
{   'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': '{}',
                 'pos': (550.0, 150.0)},
    'coder': {   'class': 'pyctools.components.pal.coder.Coder',
                 'config': '{}',
                 'pos': (250.0, 150.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': '{}',
                   'pos': (700.0, 150.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': '/home/jim/Videos/DVD/election_87.avi', 'looping': 'repeat'}",
                      'pos': (-200.0, 150.0)},
    'filewriter': {   'class': 'pyctools.components.io.videofilewriter.VideoFileWriter',
                      'config': "{'path': '/home/jim/Documents/projects/pyctools-pal/coded_pal.avi', '16bit': 'on', 'encoder': '-c:v ffv1 -pix_fmt gray16le'}",
                      'pos': (400.0, 150.0)},
    'resample': {   'class': 'pyctools.components.pal.common.To4Fsc',
                    'config': "{'xdown': 351, 'xup': 461}",
                    'pos': (-50.0, 150.0)},
    'rgbyuv': {   'class': 'pyctools.components.colourspace.rgbtoyuv.RGBtoYUV',
                  'config': "{'matrix': '601'}",
                  'pos': (100.0, 150.0)}}
        self.linkages = \
{   ('audit', 'output'): ('display', 'input'),
    ('coder', 'output'): ('filewriter', 'input'),
    ('filereader', 'output'): ('resample', 'input'),
    ('filewriter', 'output'): ('audit', 'input'),
    ('resample', 'output'): ('rgbyuv', 'input'),
    ('rgbyuv', 'output'): ('coder', 'input')}

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
    app = QtGui.QApplication([])

    logging.basicConfig(level=logging.DEBUG)
    comp = Network().make()
    comp.start()
    app.exec_()
    comp.stop()
    comp.join()
