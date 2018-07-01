# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 10:41:15 2017

@author: 309
"""

from keras.layers import Dense, MaxPool3D, Conv3D, Dropout, Flatten, InputLayer
from keras.initializers import Constant
from keras.layers.normalization import BatchNormalization
from keras.models import Sequential
from keras import backend as K

pix_size = 50

K.set_image_data_format("channels_first")

model = Sequential()
model.add(InputLayer(input_shape = (1, 100, pix_size, pix_size)))

model.add(BatchNormalization())

model.add(Conv3D(64, 
                 (3, 3, 3), 
                 bias_initializer = Constant(0.01), 
                 kernel_initializer = 'random_uniform'))
model.add(MaxPool3D())
model.add(Dropout(0.3))

model.add(Conv3D(32, 
                 (3, 3, 3), 
                 bias_initializer = Constant(0.01), 
                 kernel_initializer = 'random_uniform'))
model.add(MaxPool3D())
model.add(Dropout(0.3))

model.add(Conv3D(16, 
                 (3, 3, 3), 
                 bias_initializer = Constant(0.01), 
                 kernel_initializer = 'random_uniform'))
model.add(MaxPool3D())
model.add(Dropout(0.3))

#model.add(Dropout(0.5))
model.add(Flatten())

model.add(Dense(2, 
		  activation = 'softmax',
		  kernel_initializer='random_uniform'))

model.compile(loss = 'categorical_crossentropy',
              optimizer = 'adam', 
              metrics = ['accuracy'])

print(model.summary())

print('model loaded')


