from tweezer.dia.andor_calibration import factor_andor
from tkinter import *
from tkinter.filedialog import askopenfilename


#Keep the root window from appearing
Tk().withdraw()
#Show an "Open" dialog box and return the path to the selected file
image = askopenfilename()

factor_andor(image)
