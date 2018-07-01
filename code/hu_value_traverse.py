# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 22:08:05 2018

@author: 309
"""

import dicom
import os
import pandas as pd
import numpy as np
np.set_printoptions(threshold=np.inf)  
import cv2
import random
import scipy.ndimage
import matplotlib.pyplot as plt
from skimage import measure

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


def hu_hist(patient_pixels, save_path):
    #cv2.calcHist([patient_pixels[0]], [0], None, [3500], [-1500, 2500]) Error
    plt.hist(patient_pixels.flatten(), bins=80, color='c')
    plt.xlabel("Hounsfield Units (HU)")
    plt.ylabel("Frequency")
    plt.savefig(save_path + "\\hu_hist.png")

def largest_label_volume(im, bg=-1):
    vals, counts = np.unique(im, return_counts=True)

    counts = counts[vals != bg]
    vals = vals[vals != bg]

    if len(counts) > 0:
        return vals[np.argmax(counts)]
    else:
        return None

def segment_lung_mask(image, fill_lung_structures=True):
    
    # not actually binary, but 1 and 2. 
    # 0 is treated as background, which we do not want
    binary_image = np.array(image > -320, dtype=np.int8)+1
    labels = measure.label(binary_image)
    
    # Pick the pixel in the very corner to determine which label is air.
    #   Improvement: Pick multiple background labels from around the patient
    #   More resistant to "trays" on which the patient lays cutting the air 
    #   around the person in half
    background_label = labels[0,0,0]
    
    #Fill the air around the person
    binary_image[background_label == labels] = 2
    
    
    # Method of filling the lung structures (that is superior to something like 
    # morphological closing)
    if fill_lung_structures:
        # For every slice we determine the largest solid structure
        for i, axial_slice in enumerate(binary_image):
            axial_slice = axial_slice - 1
            labeling = measure.label(axial_slice)
            l_max = largest_label_volume(labeling, bg=0)
            
            if l_max is not None: #This slice contains some lung
                binary_image[i][labeling != l_max] = 1

    
    binary_image -= 1 #Make the image actual binary
    binary_image = 1-binary_image # Invert it, lungs are now 1
    
    # Remove other air pockets insided body
    labels = measure.label(binary_image, background=0)
    l_max = largest_label_volume(labels, bg=0)
    if l_max is not None: # There are air pockets
        binary_image[labels != l_max] = 0
 
    return binary_image


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
    

def normalize(image):
    MIN_BOUND = -1000.0
    MAX_BOUND = 400.0
    image = (image - MIN_BOUND) / (MAX_BOUND - MIN_BOUND)
    image[image>1] = 1.
    image[image<0] = 0.
    return image



def zero_center(image):
    PIXEL_MEAN = 0.25
    image = image - PIXEL_MEAN
    return image

def preprocess(patient, data_dir, labels_df, img_px_size = 256, hm_slices = 100):
    label = labels_df.get_value(patient, 'cancer')
    if label == 0:
        label = [0, 1]
    elif label == 1:
        label = [1, 0]
    path = data_dir + '\\' + patient #病人id文件夹
    slices = load_scan(path)
    slices = get_pixels_hu(slices)
    slices = [normalize(s) for s in slices]
    slices = [zero_center(s) for s in slices]
    # resize
    slices = [ cv2.resize(np.array(s), (img_px_size, img_px_size)) for s in slices ]

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
    patients.sort()
    
    labels_df = pd.read_csv(r'F:\8.CT_Project\Kaggle-data\inputs\stage1_labels.csv', index_col = 0)
    
    much_data = []
    num_patients = len(patients)
    print(num_patients)
    print('ready.')

    for num, patient in enumerate(patients, 1):  
        try:
            img_data, label = preprocess(patient, data_dir, labels_df, img_px_size = IMG_PX_SIZE, hm_slices = HM_SLICES)
            much_data.append([img_data, label])
            print(num)
        # get rid of the key_error(without label) data and AttributeError(Dataset does not have attribute 'ImagePositionPatient') data
        except Exception as e:
            print(e)
        if num % 100 == 0 or num == num_patients:
            print('This is the ', num, 'th patient.')
            np.save('.\\muchdata2\\{}-muchdata-{}-{}-{}.npy'.format(str(num).zfill(4), IMG_PX_SIZE, IMG_PX_SIZE, HM_SLICES), much_data)
            much_data = []