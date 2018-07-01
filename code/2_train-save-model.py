# -*- coding: utf-8 -*-
"""
Created on Sun Dec 24 21:24:11 2017

@author: 309
"""

import model_structure
import numpy as np
import os 
import pickle

# load muchdata

path = r'C:\CT_Project\muchdata2'
data_file = os.listdir(path)
muchdata = np.array([])

for f in data_file:
    if muchdata.shape[0] == 0:
        muchdata = np.load(path + '\\' + f)
        # np.vstack( (muchdata, np.load(path + '\\' + f)) )
    else:
        muchdata = np.vstack((muchdata, np.load(path + '\\' + f)))

print('shape of muchdata', muchdata.shape)

for x in muchdata:
    print(x[0].shape)

train_data = np.array([x[0] for x in muchdata[:-200]])
train_data = np.reshape(train_data, (train_data.shape[0], 1, 100, 50, 50))
train_label = np.array([x[1] for x in muchdata[:-200]])
print('shape of train_data:', train_data.shape)
print('shape of train_label:', train_label.shape)

val_data = np.array([x[0] for x in muchdata[-200:]])
val_data = np.reshape(val_data, (val_data.shape[0], 1, 100, 50, 50))
val_label = np.vstack(x[1] for x in muchdata[-200:])

print('val_data:', val_data.shape)
print('val_label:', val_label.shape)

'''

val_data = np.array([x[0].reshape(1, x[0].shape[0], x[0].shape[1], x[0].shape[2]) for x in muchdata[-200:-100]])
#val_data.reshape(val_data.shape[0], 100, 256, 256, 1)
val_label = np.array([x[1] for x in muchdata[-200:-100]])


test_data = np.array(x[0] for x in muchdata[-100:])
test_data.reshape(test_data.shape[0], 1, 100, 256, 256)
test_data = np.array(x[1] for x in muchdata[-100:])
'''
model = model_structure.model
history = model.fit(train_data, 
                  train_label,
                  epochs = 5, 
                  batch_size = 10, 
                  validation_data = (val_data, val_label))

with open('history_dict', 'wb') as f:
    pickle.dump(history.history, f)
model.save('my_model.h5')
print('model saved')

'''

# Plot the accurancy and loss
import matplotlib.pyplot as plt

history = pickle.load( open('history_dict', 'rb') )

accuracy = history['acc']
val_accuracy = history['val_acc']
loss = history['loss']
val_loss = history['val_loss']
epochs = range(len(accuracy))
plt.plot(epochs, accuracy, 'bo', label = 'Training accuracy')
plt.plot(epochs, val_accuracy, 'b', label = 'Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend()

plt.figure()
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.show()

'''