# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 14:12:53 2025

@author: Charlie
"""

import tkinter as tk
from tkinter import filedialog

def change_directory():
    directory = filedialog.askdirectory()
    return directory
