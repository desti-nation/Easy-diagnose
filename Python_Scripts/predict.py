# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 14:33:48 2017

@author: 309
"""
from keras.models import load_model
import numpy as np
import os
from sys import argv

if __name__ == '__main__':
    INPUT_PATH = argv[1]
    model_path = argv[2]
    TEMP_DATA_PATH = INPUT_PATH + "\\TEMP_DATA"
    data_path = TEMP_DATA_PATH + "\\muchdata"
    data_file = os.listdir(data_path)
    muchdata = np.load(data_path + '\\' + data_file[0])
    test_data = np.reshape(muchdata, (1, 1, 100, 50, 50))
    model = load_model(model_path)
    print(model)

    pre = model.predict(test_data)
    index= np.argmax(pre)
    
    with open(TEMP_DATA_PATH + "\\result.txt","w") as f:
        f.write(str(index) + '\n')
        f.write(str(round(pre[0][index]*100)) + ' %')