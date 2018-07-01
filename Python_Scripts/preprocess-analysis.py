# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 14:10:51 2017

@author: 309
"""

import numpy as np # linear algebra
import dicom
import os
import scipy.ndimage
import matplotlib.pyplot as plt
from skimage import measure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import cv2
from sys import argv
import dicom
import os
import pandas as pd
import numpy as np
import cv2
import random


def load_scan(path):
    slices = []
    for s in os.listdir(path):
        if s.endswith('.dcm'):
            slices.append( dicom.read_file(path + '\\' + s) )
    #slices = [dicom.read_file(path + '\\' + s) for s in os.listdir(path)]
    slices.sort(key = lambda x: float(x.ImagePositionPatient[2]))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices
	
def preprocess(data_dir, img_px_size = 256, hm_slices = 100):
    slices = load_scan(data_dir)
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
    return np.array(slices)
    
def save_figures(slices, path):
    # save the image to .png format for the use of java interface
    save_path = path + "\\figure"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    for i, s in enumerate(slices, 1):
        cv2.imwrite(save_path + "\\" + str(i).zfill(3) + ".png", s.pixel_array)
        #plt.imshow(s.pixel_array)
        #plt.savefig(save_path + "\\" + str(i) + ".png")
    
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
    

def plot_3d1(image, save_path, threshold=-300):
    # Position the scan upright,
    # so the head of the patient would be at the top facing the camera
    p = image.transpose(2,1,0)
    verts, faces, a, b = measure.marching_cubes_lewiner(p, threshold)
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    mesh = Poly3DCollection(verts[faces], alpha=0.1)
    face_color = [0.5, 0.5, 1]
    mesh.set_facecolor(face_color)
    ax.add_collection3d(mesh)
    ax.set_xlim(0, p.shape[0])
    ax.set_ylim(0, p.shape[1])
    ax.set_zlim(0, p.shape[2])
    fig.savefig(save_path + "\\3D.png")
    #plt.show()
    
def plot_3d(image, path, threshold=-300):
    print("a")
    # Position the scan upright, 
    # so the head of the patient would be at the top facing the camera
    p = image.transpose(2,1,0)
    print("b")
    verts, faces, i, j = measure.marching_cubes(p, threshold)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    print("c")
    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    mesh = Poly3DCollection(verts[faces], alpha = 0.6)
    face_color = [0.25, 0.25, 0.85]
    mesh.set_facecolor(face_color)
    ax.add_collection3d(mesh)
    print("d")
    ax.set_xlim(0, p.shape[0])
    ax.set_ylim(0, p.shape[1])
    ax.set_zlim(0, p.shape[2])
    print("e")
    fig.savefig(path + "\\" + "plot_3D.jpg", transparent=True)

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
    
    # Pick the pixel in the avery corner to determine which label is air.
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

if __name__ == '__main__':
    INPUT_PATH = argv[1]
    #INPUT_PATH = r'F:\8.CT_Project\Kaggle-data\inputs\stage1\0a0c32c9e08cc2ea76a71649de56be6d'
    patient_id = os.path.basename(INPUT_PATH)
    IMG_PX_SIZE = 50
    HM_SLICES = 100
    # load patient sacns
    patient_scans = load_scan(INPUT_PATH)
    print("Load patients scans Finished")
    
    # create temp data path
    TEMP_DATA_PATH = INPUT_PATH + "\\TEMP_DATA"
    
    if os.path.isdir(TEMP_DATA_PATH):
        pass
    else:
        os.mkdir(TEMP_DATA_PATH)
    print("Create data path finished")
    
	# create much data path
    if os.path.isdir(TEMP_DATA_PATH + '\\muchdata'):
        pass
    else:
        os.mkdir(TEMP_DATA_PATH + '\\muchdata')
    print("Create muchdata path finished")
	
	# save the resampled file in .npy format for predict
    img_data= preprocess(INPUT_PATH, img_px_size = IMG_PX_SIZE, hm_slices = HM_SLICES)
    muchdata = img_data
    np.save(TEMP_DATA_PATH + '\\muchdata\\muchdata-{}-{}-{}.npy'.format(IMG_PX_SIZE, IMG_PX_SIZE, HM_SLICES), muchdata)
	
    # save the info to txt file
    with open(TEMP_DATA_PATH + "\\info_basic.txt","w") as f:
        f.write(patient_id)
    with open(TEMP_DATA_PATH + "\\info_DICOM.txt","w") as f:
        f.write(str(patient_scans[0]))
    
    #save patient figures
    save_figures(patient_scans, TEMP_DATA_PATH)
    print("save patient figures Finished")
    
    # plot hu and save figure
    patient_pixels = get_pixels_hu(patient_scans)
    hu_hist(patient_pixels, TEMP_DATA_PATH)
    print("Transform Hu Finished")
    '''
    # pixel resample
    pix_resampled, spacing = resample(patient_pixels, patient_scans, [1,1,1])
    np.save(TEMP_DATA_PATH + "\\resampled_data.npy", pix_resampled)
    print("Resample Finished")
    
    pix_resampled = np.load(TEMP_DATA_PATH + "\\resampled_data.npy")
    plot = False
    if plot == True:
        plot_3d1(pix_resampled, TEMP_DATA_PATH, 400)
        print("Plot 3D images finished")
     
    
    patient_pixels = normalize(patient_pixels)
    print("Normalize finished")
    patient_pixels = zero_center(patient_pixels)
    print("Zero_center finished")
    np.save(TEMP_DATA_PATH + "\\preprocessed_data.npy", patient_pixels)
    print("Preprocessed data saved.")
   
    pix_resampled = np.load(TEMP_DATA_PATH + '\\resampled_data.npy')
    
    segmented_lungs = segment_lung_mask(pix_resampled, False)
    print(segmented_lungs[0])
    print(segmented_lungs[0].shape)
    #segmented_lungs_fill = segment_lung_mask(pix_resampled, True)

    #plot_3d1(segmented_lungs, TEMP_DATA_PATH, 0)
     '''
