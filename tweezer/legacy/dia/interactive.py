#!/usr/bin/env python
#-*- coding: utf-8 -*-

from IPython.html.widgets import interactive, fixed
from IPython.display import display
from skimage import io
from skimage.filter import denoise_tv_chambolle


def edit_image(image, weight=0.1):
    new_image = denoise_tv_chambolle(image, weight)
    new_image = io.Image(new_image)
    display(new_image)
    return new_image


def denoise_interactive(image):
    newImage = interactive(edit_image, image=fixed(image), weight=(0.05, 1))
    display(newImage)
    return(newImage)
