from tweezer.dia.ccd_calibration import factor_collection
from tkinter import *
from tkinter.filedialog import askopenfilename

#Opens a popup to select the directory

#Keeps the root window from appearing
Tk().withdraw()
#Shows an "Open" dialog box and return the path to the selected file
collectionPath = askopenfilename()

factor_collection(collectionPath)
