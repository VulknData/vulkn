# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import os
import importlib
import inspect
import glob
from importlib import util


def load_library(ltype, basepath):
    modules = {}
    for f in filter(lambda x: not x.endswith('/__init__.py'), glob.glob(f'{basepath}/{ltype}/*.py')):
        module_name = f'{ltype}.' + os.path.basename(f)[0:-3]
        module_spec = importlib.util.spec_from_file_location(module_name, f)
        module = util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        for o in inspect.getmembers(module):
            if ((inspect.isfunction(o[1]) or inspect.isclass(o[1])) 
                    and o[1].__module__ == module_name and not o[0].startswith('_')):
                modules[o[0]] = o[1]
    return modules


def show():
    l = []
    for k in vectors.keys():
        l.append({'type': 'Vector Function', 'name': k})
    for k in extensions.keys():
        l.append({'type': 'SQL Extension', 'name': k})
    for k in udfs.keys():
        l.append({'type': 'User Defined Function', 'name': k})
    return l
    

vectors = load_library('vector', os.path.dirname(os.path.abspath(__file__)))
extensions = load_library('extensions', os.path.dirname(os.path.abspath(__file__)))
udfs = load_library('udfs', os.path.dirname(os.path.abspath(__file__)))
