#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.pal.common
import pyctools.components.pal.decoder
import pyctools.components.io.videofilereader
import pyctools.components.io.dumpmetadata
import pyctools.components.qt.qtdisplay

class Network(object):
    components = \
{   'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': '{}',
                 'pos': (500.0, 150.0)},
    'decoder': {   'class': 'pyctools.components.pal.decoder.Decoder',
                   'config': '{}',
                   'pos': (200.0, 150.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'stats': True, 'framerate': 50}",
                   'pos': (650.0, 150.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'16bit': True, 'path': "
                                "'/home/jim/Documents/projects/pyctools-pal/coded_pal.avi', "
                                "'type': 'Y', 'looping': 'repeat'}",
                      'pos': (50.0, 150.0)},
    'resample': {   'class': 'pyctools.components.pal.common.From4Fsc',
                    'config': "{'xdown': 461, 'xup': 351}",
                    'pos': (350.0, 150.0)}}
    linkages = \
{   ('audit', 'output'): [('display', 'input')],
    ('decoder', 'output'): [('resample', 'input')],
    ('filereader', 'output'): [('decoder', 'input')],
    ('resample', 'output'): [('audit', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    from pyctools.core.qt import Qt, QtWidgets
    QtWidgets.QApplication.setAttribute(Qt.AA_X11InitThreads)
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
