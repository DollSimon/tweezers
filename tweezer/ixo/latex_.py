#!/usr/bin/env python
#-*- coding: utf-8 -*-

import envoy

###############################################################################
## PyTeX related functions
###############################################################################
def compile_pytex_file(pytex_file='pytex_template.tex'):
    """
    Compile a [PythonTex](https://github.com/gpoore/pythontex) file into

    :param pytex_file: (.tex file) A pytexDescription

    """
    pdflatex_call = envoy.run("pdflatex -interaction=batchmode {}".format(pytex_file))
    pytex_call = envoy.run("pythontex.py {}".format(pytex_file))
    pdflatex_call = envoy.run("pdflatex -interaction=batchmode {}".format(pytex_file))

    return pytex_call, pdflatex_call
