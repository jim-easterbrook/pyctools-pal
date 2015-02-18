Pyctools-PAL
============

PAL coding and decoding with Pyctools.

This uses `Pyctools <https://github.com/jim-easterbrook/pyctools>`_ to simulate a PAL coder and two decoders.
PAL is the colour system used for analogue television in (most of) western Europe and many other parts of the world.
It is still of some interest because of its use in TV archives.
(And it presents some interesting technical problems.)

This project also demonstrates how to extend Pyctools.
It can be copied (and renamed!) to use as a base for your own extensions.

Requirements
------------

* `Pyctools <https://github.com/jim-easterbrook/pyctools>`_ and its requirements.

Installation
------------

Use of Pyctools-PAL requires easy access to the source files, so installation with ``pip`` is not really appropriate.
You should clone the GitHub repository, or download and extract a zip or tar.gz archive from the GitHub releases page, and then use ``setup.py`` to install the PAL components::

  git clone https://github.com/jim-easterbrook/pyctools-pal.git
  cd pyctools-pal
  python setup.py build
  sudo python setup.py install

Use
---

The ``src/scripts`` directory contains a PAL coder, normal PAL decoder and 2D `Transform PAL Decoder <http://www.jim-easterbrook.me.uk/pal/>`_ that can be loaded into the Pyctools graph editor.
Start with the coder so you can generate a PAL file to use with the decoders.
Before running either script you need to configure the file reader and/or writer components' ``path`` values.

Licence
-------

| Pyctools-PAL - PAL coding and decoding with Pyctools.
| http://github.com/jim-easterbrook/pyctools-pal
| Copyright (C) 2014-15  Jim Easterbrook  jim@jim-easterbrook.me.uk

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.
