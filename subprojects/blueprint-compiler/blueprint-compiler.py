#!/usr/bin/env python3

# blueprint-compiler.py
#
# Copyright 2021 James Westman <james@jwestman.net>
#
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import os
import sys

# These variables should be set by meson. If they aren't, we're running
# uninstalled, and we might have to guess some values.
version = "@VERSION@"
module_path = r"@MODULE_PATH@"
libdir = r"@LIBDIR@"

if version == "\u0040VERSION@":
    version = "uninstalled"
    libdir = None
else:
    # If Meson set the configuration values, insert the module path it set
    sys.path.insert(0, module_path)

from blueprintcompiler import main

if __name__ == "__main__":
    main.main(version, libdir)
