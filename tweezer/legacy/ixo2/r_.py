#!/usr/bin/env python
#-*- coding: utf-8 -*-

import envoy


R_LIB_DIR = '/Library/Frameworks/R.framework/Resources/library/tweezR/'


def run_rscript(script, script_path=R_LIB_DIR, **kwargs):
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


## [Making Matplotlib look like ggplot2](http://messymind.net/)
