#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.pal.decoder
import pyctools.components.io.dumpmetadata
import pyctools.components.pal.common
import pyctools.components.qt.qtdisplay
import pyctools.components.io.videofilereader

class Network(object):
    components = \
{   'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': "{'raw': 0, 'outframe_pool_len': 3}",
                 'pos': (420.0, 260.0)},
    'decoder': {   'class': 'pyctools.components.pal.decoder.Decoder',
                   'config': "{'yuvrgb': {'matrix': '601', "
                             "'outframe_pool_len': 3, 'range': 'studio'}, "
                             "'setlevel': {'func': '((data - pt_float(64)) "
                             "* pt_float(219.0 / 140.0)) + pt_float(16)', "
                             "'outframe_pool_len': 3}, 'demod': "
                             "{'outframe_pool_len': 3}, 'matrix': "
                             "{'outframe_pool_len': 3}, 'filterUV': "
                             "{'ydown': 1, 'xup': 1, 'yup': 1, "
                             "'outframe_pool_len': 3, 'xdown': 1}, "
                             "'filterY': {'ydown': 1, 'xup': 1, 'yup': 1, "
                             "'outframe_pool_len': 3, 'xdown': 1}}",
                   'expanded': False,
                   'pos': (170.0, 150.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'shrink': 1, 'expand': 1, "
                             "'outframe_pool_len': 3, 'title': '', "
                             "'repeat': 1, 'sync': 1, 'framerate': 50, "
                             "'stats': 1}",
                   'pos': (420.0, 150.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'type': 'Y', 'looping': 'repeat', "
                                "'16bit': 1, 'outframe_pool_len': 3, "
                                "'path': "
                                "'/home/jim/Documents/projects/pyctools-pal/coded_pal.avi'}",
                      'pos': (50.0, 150.0)},
    'resample': {   'class': 'pyctools.components.pal.common.From4Fsc',
                    'config': "{'ydown': 1, 'xup': 351, 'yup': 1, "
                              "'outframe_pool_len': 3, 'xdown': 461}",
                    'pos': (290.0, 150.0)}}
    linkages = \
{   ('decoder', 'output'): [('resample', 'input')],
    ('filereader', 'output'): [('decoder', 'input')],
    ('resample', 'output'): [('display', 'input'), ('audit', 'input')]}

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
