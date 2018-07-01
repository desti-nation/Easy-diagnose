# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 16:45:28 2018

@author: 309
"""


import dicom
import os
import pandas as pd
import numpy as np
#np.set_printoptions(threshold=np.inf)  
import cv2
import random
import scipy.ndimage
import matplotlib.pyplot as plt
from skimage import measure

def load_scan(path):
    slices = []
    for s in os.listdir(path):
        if s.endswith('.dcm'):
            slices.append( dicom.read_file(path + '\\' + s) )
    slices.sort(key = lambda x: float(x.ImagePositionPatient[2]))
    slices = slices[20:-20] # delete 20 slices in the head and tail which contain less useful information and reduce the data volume
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices
    
def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])
    # Convert to int16 (from sometimes int16), 
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)

    # Set outside-of-scan pixels to 0
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0
    
    # Convert to Hounsfield units (HU)
    for slice_number in range(len(slices)):
        
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope
        
        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)
            
        image[slice_number] += np.int16(intercept)
    
    return np.array(image, dtype=np.int16)
    
def normalize(image):
    image = (image - MIN_BOUND) / (MAX_BOUND - MIN_BOUND)
    image[image>1] = 1.
    image[image<0] = 0.
    return image
    
if __name__ == '__main__':
    IMG_PX_SIZE = 50
    HM_SLICES = 100 # how many slices
    
    data_dir = r'F:\8.CT_Project\Kaggle-data\inputs\stage1'
    patients = os.listdir(data_dir)
    patients.sort()

    
    for num, patient in enumerate(patients[:1], 1):  
        try:
            print('begin')
            img_data, label = preprocess(patient, data_dir, labels_df, img_px_size = IMG_PX_SIZE, hm_slices = HM_SLICES)
        # get rid of the key_error(without label) data and AttributeError(Dataset does not have attribute 'ImagePositionPatient') data
        except Exception as e:
            print(e)
        if num % 100 == 0 or num == num_patients:
            print('This is the ', num, 'th patient.')
            np.save('.\\muchdata\\{}-muchdata-{}-{}-{}.npy'.format(str(num).zfill(4), IMG_PX_SIZE, IMG_PX_SIZE, HM_SLICES), much_data)
            much_data = []
    


