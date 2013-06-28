#!/usr/bin/env python
#-*- coding: utf-8 -*-

import numpy as np
from matplotlib import rc
from matplotlib.pyplot import figure, axes, plot, xlabel, ylabel, title, \
     grid, savefig, show, close

from tweezer.core.polymer import ExtensibleWormLikeChain
# from tweezer.cli import InterpretUserInput

def matplotlib_example():
    rc('text', usetex=True)
    rc('font', family='serif')
    figure(1, figsize=(6,4))
    ax = axes([0.1, 0.1, 0.8, 0.7])
    t = np.arange(0.0, 1.0+0.01, 0.01)
    s = np.cos(2*2*np.pi*t)+2
    plot(t, s)

    xlabel(r'\textbf{time (s)}')
    ylabel(r'\textit{voltage (mV)}',fontsize=16)
    title(r"\TeX\ is Number $\displaystyle\sum_{n=1}^\infty\frac{-e^{i\pi}}{2^n}$!",
          fontsize=16, color='r')
    grid(True)
    savefig('tex_demo')
    show()


def plot_extensible_worm_like_chain():
    wlc = ExtensibleWormLikeChain(1000)
    try:
        fig = wlc.plot_example()
    except (KeyboardInterrupt, SystemExit), err:
        close(fig)
        raise err

