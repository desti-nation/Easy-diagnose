# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 20:10:19 2017

@author: 309
"""

import numpy as np
import os 

path = '.\\muchdata'
data_file = os.listdir(path)
print(data_file)
muchdata = []
for f in data_file:
    muchdata.append(np.load(path + '\\' + f))
