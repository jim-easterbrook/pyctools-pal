#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.io.dumpmetadata
import pyctools.components.io.videofilereader
import pyctools.components.io.videofilewriter
import pyctools.components.pal.coder
import pyctools.components.pal.common
import pyctools.components.qt.qtdisplay

class Network(object):
    components = \
{   'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': '{}',
                 'pos': (110.0, 60.0)},
    'coder': {   'class': 'pyctools.components.pal.coder.Coder',
                 'config': "{'modulator': {}, 'assemble': {'func': "
                           "'(((data1 + data2) - pt_float(16.0)) * "
                           "pt_float(140.0 / 219.0)) + pt_float(64.0)'}, "
                           "'rgbyuv': {'matrix': '601', "
                           "'outframe_pool_len': 5}, 'matrix': {}, "
                           "'prefilter': {}, 'postfilter': {'resize': {}, "
                           "'fildes': {'frequency': '0.0, 0.307, 0.317, "
                           "0.346, 0.356, 0.5', 'gain': '     1.0, 1.0,   "
                           "1.0,   0.0,   0.0,   0.0', 'weight': '   1.0, "
                           "1.0,   0.0,   0.0,   1.0,   1.0', 'aperture': "
                           '17}}}',
                 'expanded': False,
                 'pos': (-30.0, -50.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'framerate': 40}",
                   'pos': (110.0, -50.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': "
                                "'/home/jim/Videos/test_seqs/mobcal.avi'}",
                      'pos': (-270.0, -50.0)},
    'filewriter': {   'class': 'pyctools.components.io.videofilewriter.VideoFileWriter',
                      'config': "{'path': "
                                "'/home/jim/Documents/projects/pyctools-pal/coded_pal.avi', "
                                "'encoder': '-c:v ffv1 -pix_fmt gray16le', "
                                "'16bit': 1}",
                      'pos': (110.0, -160.0)},
    'resample': {   'class': 'pyctools.components.pal.common.To4Fsc',
                    'config': "{'resize': {'xup': 461, 'xdown': 351}, "
                              "'filgen': {'xup': 461, 'xdown': 351, "
                              "'xaperture': 12}}",
                    'expanded': False,
                    'pos': (-150.0, -50.0)}}
    linkages = \
{   ('coder', 'output'): [   ('filewriter', 'input'),
                             ('audit', 'input'),
                             ('display', 'input')],
    ('filereader', 'output'): [('resample', 'input')],
    ('resample', 'output'): [('coder', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    from PyQt5 import QtCore, QtWidgets
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = QtWidgets.QApplication([])

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
