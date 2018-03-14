#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.io.videofilereader
import pyctools.components.qt.qtdisplay
import pyctools.components.io.dumpmetadata
import pyctools.components.pal.coder
import pyctools.components.io.videofilewriter
import pyctools.components.pal.common

class Network(object):
    components = \
{   'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': "{'outframe_pool_len': 3, 'raw': 0}",
                 'pos': (110.0, 60.0)},
    'coder': {   'class': 'pyctools.components.pal.coder.Coder',
                 'config': "{'matrix': {'outframe_pool_len': 3}, 'rgbyuv': "
                           "{'matrix': '601', 'range': 'studio', "
                           "'outframe_pool_len': 5}, 'assemble': "
                           "{'outframe_pool_len': 3, 'func': '(((data1 + "
                           'data2) - pt_float(16.0)) * pt_float(140.0 / '
                           "219.0)) + pt_float(64.0)'}, 'prefilter': "
                           "{'xup': 1, 'outframe_pool_len': 3, 'ydown': 1, "
                           "'xdown': 1, 'yup': 1}, 'modulator': "
                           "{'outframe_pool_len': 3}}",
                 'expanded': False,
                 'pos': (-30.0, -50.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'framerate': 40, 'title': '', 'expand': 1, "
                             "'stats': 0, 'repeat': 1, 'outframe_pool_len': "
                             "3, 'sync': 1, 'shrink': 1}",
                   'pos': (110.0, -50.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'type': 'RGB', 'outframe_pool_len': 3, "
                                "'looping': 'off', '16bit': 0, 'path': "
                                "'/home/jim/Videos/test_seqs/mobcal.avi'}",
                      'pos': (-270.0, -50.0)},
    'filewriter': {   'class': 'pyctools.components.io.videofilewriter.VideoFileWriter',
                      'config': "{'16bit': 1, 'outframe_pool_len': 3, "
                                "'encoder': '-c:v ffv1 -pix_fmt gray16le', "
                                "'fps': 25, 'path': "
                                "'/home/jim/Documents/projects/pyctools-pal/coded_pal.avi'}",
                      'pos': (110.0, -160.0)},
    'resample': {   'class': 'pyctools.components.pal.common.To4Fsc',
                    'config': "{'xup': 461, 'outframe_pool_len': 3, "
                              "'ydown': 1, 'xdown': 351, 'yup': 1}",
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
    parser = argparse.ArgumentParser()
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
