#!/usr/bin/env python
#-*- coding: utf-8 -*-

import envoy

def run_rscript(script, script_path='/Library/Frameworks/R.framework/Resources/library/tweezR/', **kwargs):
    """
    Calls an R script

    :param script: (Str) name of the script

    :param script_path: (Path)
    """
    if script_path[-1] == '/':
        path = "".join(script_path, script)
    else:
        path = "/".join(script_path, script)

    r = envoy.run("Rscript {} ".format(path))

    return r

