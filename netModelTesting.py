from __future__ import absolute_import
from __future__ import print_function
import numpy as np
import random
from keras.datasets import mnist
from keras.models import Sequential, Model
from keras.layers import Input, Flatten, Dense, Dropout, Lambda, Conv2D,MaxPooling2D, Concatenate
from keras.optimizers import RMSprop
from keras import backend as K
import dataGenerator
import auxfunctions

numClasses = 8

input_shape=(30,30,3)

#Funcion que define la red siamesa
def createBaseNetwork(input_shape):

    input = Input(shape=input_shape)
    print(input)
    #x = Flatten()(input)
    x = Conv2D(96, (11, 11), activation='relu',name='conv1')(input)
    x = MaxPooling2D((3, 3), strides=(2, 2), name='pool1')(x)
    #LRN1 (investigar)
    x = Conv2D(384, (5,5), activation='relu',name='conv2')(x)
    x = MaxPooling2D((3, 3), strides=(2, 2), name='pool2')(x)
    #LRN2 (investigar)
    x = Conv2D(384, (3, 3), activation='relu',name='conv3')(x)
    x = Conv2D(384, (3, 3), activation='relu', name='conv4')(x)
    x = Conv2D(256, (3, 3), activation='relu', name='conv5')(x)
    x = MaxPooling2D((3, 3), strides=(2, 2), name='pool3')(x)
    x = Flatten()(x)
    x= Dense(4096,activation='relu',name='fc1')(x)

    return Model(input, x)

#---------------------------------------------------------------------------------
def getSiameseNetWork(input_shape,numClasses):
    base_network = createBaseNetwork(input_shape)

    input_a = Input(shape=input_shape)
    input_b = Input(shape=input_shape)

    #Reuso de la instancia para compartir los pesos
    left = base_network(input_a)
    right = base_network(input_b)

    #Concatenar con la red siamesa y generar capas adicionales
    outLayers=Concatenate(axis=-1)([left,right])
    outLayers=Dense(4096, activation='relu', name='fc2')(outLayers)
    outLayers=Dense(4096, activation='relu', name='fc3')(outLayers)
    outLayers=Dense(8, activation='relu', name='fc4')(outLayers)
    outLayers=Dense(numClasses, activation='softmax', name='predictions')(outLayers)

    model = Model([input_a, input_b], outLayers)

    return model

#----------------------------------------------------------------------------------------
    
model=getSiameseNetWork(input_shape,numClasses)

#Obtencion de la lista de tuplas con las rutas de las imagenes
imgList=auxfunctions.loadimgspath('./dataset')

params = {'dim': (30,30),
          'batch_size': 5,
          'n_classes': 8,
          'n_channels': 3,
          'shuffle': True}

ID_List=[1,2,3,4,5]

training_generator=dataGenerator.DataGenerator(imgList,ID_List,**params)

model.compile(loss='categorical_crossentropy',
            optimizer='adam',
            metrics=['acc'])


model.fit_generator(generator=training_generator)