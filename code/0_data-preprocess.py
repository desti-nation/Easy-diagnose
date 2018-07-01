# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 23:50:01 2017

@author: 309

data preprocess
"""

import dicom
import os
import pandas as pd
import numpy as np
import cv2
import random

# load CT scans (in *.dcm format) for one patient
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


#first_patient = load_scan(INPUT_FOLDER + '\\' + patients[0])
#first_patient_pixels = get_pixels_hu(first_patient)

    #print(scans[0].PixelSpacing)


def hu_hist(patient_pixels, save_path):
    #cv2.calcHist([patient_pixels[0]], [0], None, [3500], [-1500, 2500]) Error
    plt.hist(patient_pixels.flatten(), bins=80, color='c')
    plt.xlabel("Hounsfield Units (HU)")
    plt.ylabel("Frequency")
    plt.savefig(save_path + "\\hu_hist.png")  


def resample(image, scan, new_spacing=[1,1,1]):
    # Determine current pixel spacing
    spacing = np.array([scan[0].SliceThickness] + scan[0].PixelSpacing, dtype=np.float32)

    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor

    image = scipy.ndimage.interpolation.zoom(image, real_resize_factor, mode='nearest')
   
    return image, new_spacing

def preprocess(patient, data_dir, labels_df, img_px_size = 256, hm_slices = 100):
    label = labels_df.get_value(patient, 'cancer')
    if label == 0:
        label = [0, 1]
    elif label == 1:
        label = [1, 0]
    path = data_dir + '\\' + patient #病人id文件夹
    slices = load_scan(path)
    # resize
    slices = [ cv2.resize(np.array(each_slice.pixel_array), (img_px_size, img_px_size)) for each_slice in slices ]

    dis = len(slices) - hm_slices
    if dis > 0:
        slices = random.sample(slices, hm_slices)
    elif dis < 0:
        insert_indexes = range(0, len(slices))
        insert_indexes = random.sample(insert_indexes, abs(dis))
        for i in insert_indexes:
            slices.insert(i, slices[i])
    return np.array(slices), np.array(label)

if __name__ == '__main__':
    IMG_PX_SIZE = 50
    HM_SLICES = 100 # how many slices
    
    data_dir = r'F:\8.CT_Project\Kaggle-data\inputs\stage1'
    patients = os.listdir(data_dir)
    labels_df = pd.read_csv(r'F:\8.CT_Project\Kaggle-data\inputs\stage1_labels.csv', index_col = 0)
    
    much_data = []
    num_patients = len(patients)
    print(num_patients)

    for num, patient in enumerate(patients, 1):  
        try:
            img_data, label = preprocess(patient, data_dir, labels_df, img_px_size = IMG_PX_SIZE, hm_slices = HM_SLICES)
            much_data.append([img_data, label])
            print(str(num))
        # get rid of the key_error(without label) data and AttributeError(Dataset does not have attribute 'ImagePositionPatient') data
        except:
            pass
        if num % 100 == 0 or num == num_patients:
            print('This is the ', num, 'th patient.')
            np.save('.\\muchdata\\{}-muchdata-{}-{}-{}.npy'.format(str(num).zfill(4), IMG_PX_SIZE, IMG_PX_SIZE, HM_SLICES), much_data)
            much_data = []

        