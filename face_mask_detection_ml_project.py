# -*- coding: utf-8 -*-
"""Face Mask Detection ML Project FINAL

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nEYrGW6U_Ug_-YoxYsRG9PEYKAaE9g9e
"""

import numpy as np 
import pandas as pd 
import os
import matplotlib.pyplot as plt
import cv2
import matplotlib.patches as patches
import tensorflow as tf
from keras.layers import Flatten, Dense, Conv2D, MaxPooling2D, Dropout
from keras.models import Sequential
from keras.models import load_model

from google.colab import drive
drive.mount('/content/drive')

pip install mtcnn

from mtcnn.mtcnn import MTCNN

images=os.path.join("/content/drive/MyDrive/ML Project/dataset/Medical mask/Medical mask/Medical Mask/images")
annotations=os.path.join("/content/drive/MyDrive/ML Project/dataset/Medical mask/Medical mask/Medical Mask/annotations")
train=pd.read_csv(os.path.join("/content/drive/MyDrive/ML Project/dataset/train.csv"))
submission=pd.read_csv(os.path.join("/content/drive/MyDrive/ML Project/dataset/submission.csv"))

print(len(train))
train.head()

len(os.listdir(images))

a=os.listdir(images)
b=os.listdir(annotations)
a.sort()
b.sort()

print(len(b),len(a))

train_images=a[1698:]
test_images=a[:1698]

test_images[0]

img=plt.imread(os.path.join(images,test_images[324]))
plt.imshow(img)
plt.show()

img=plt.imread(os.path.join(images,train_images[56]))
plt.imshow(img)
plt.show()

options=['face_with_mask','face_no_mask']
train= train[train['classname'].isin(options)]
train.sort_values('name',axis=0,inplace=True)

bbox=[]
for i in range(len(train)):
    arr=[]
    for j in train.iloc[i][["x1",'x2','y1','y2']]:
        arr.append(j)
    bbox.append(arr)
train["bbox"]=bbox  
def get_boxes(id):
    boxes=[]
    for i in train[train["name"]==str(id)]["bbox"]:
        boxes.append(i)
    return boxes
print(get_boxes(train_images[66]))
image=train_images[66]

img=plt.imread(os.path.join(images,image))

fig,ax = plt.subplots(1)
ax.imshow(img)
boxes=get_boxes(image)
for box in boxes:
    rect = patches.Rectangle((box[0],box[1]),box[2]-box[0],box[3]-box[1],linewidth=2,edgecolor='r',facecolor='none')
    ax.add_patch(rect)
plt.show()

image=train_images[17]

img=plt.imread(os.path.join(images,image))

fig,ax = plt.subplots(1)
ax.imshow(img)
boxes=get_boxes(image)
for box in boxes:
    rect = patches.Rectangle((box[0],box[1]),box[2]-box[0],box[3]-box[1],linewidth=2,edgecolor='r',facecolor='none')
    ax.add_patch(rect)
plt.show()

plt.bar(['face_with_mask','face_no_mask'],train.classname.value_counts())

"""# Creating training data"""

img_size=50
data=[]
path='/content/drive/MyDrive/ML Project/dataset/Medical mask/Medical mask/Medical Mask/images'
def create_data():
       for i in range(len(train)):
            arr=[]
            for j in train.iloc[i]:
                   arr.append(j)
            img_array=cv2.imread(os.path.join(images,arr[0]),cv2.IMREAD_GRAYSCALE)
            crop_image = img_array[arr[2]:arr[4],arr[1]:arr[3]]
            new_img_array=cv2.resize(crop_image,(img_size,img_size))
            data.append([new_img_array,arr[5]])
create_data()

data[0][0]
plt.imshow(data[0][0])

x=[]
y=[]
for features, labels in data:
    x.append(features)
    y.append(labels)
from sklearn.preprocessing import LabelEncoder
lbl=LabelEncoder()
y=lbl.fit_transform(y)

x=np.array(x).reshape(-1,50,50,1)
x=tf.keras.utils.normalize(x,axis=1)
from keras.utils import to_categorical
y = to_categorical(y)

"""# Model Fitting"""

from keras.layers import LSTM
model=Sequential()
model.add(Conv2D(100,(3,3),input_shape=x.shape[1:],activation='relu',strides=2))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Conv2D(64,(3,3),activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Flatten())
model.add(Dense(50, activation='relu'))
model.add(Dropout(0.2))

model.add(Dense(2, activation='softmax'))

opt = tf.keras.optimizers.Adam(lr=1e-3, decay=1e-5)
model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy']) 
model.fit(x,y,epochs=30,batch_size=5)

detector=MTCNN()
img=plt.imread(os.path.join(images,test_images[516]))
face=detector.detect_faces(img)
for face in face:
        bounding_box=face['box']
        x=cv2.rectangle(img,
              (bounding_box[0], bounding_box[1]),
              (bounding_box[0]+bounding_box[2], bounding_box[1] + bounding_box[3]),
              (0,155,255),
              10)
        plt.imshow(x)

detector=MTCNN()
test_df=[]
for image in test_images:
    img=plt.imread(os.path.join(images,image))
    faces=detector.detect_faces(img)
    test=[]
    for face in faces:
        bounding_box=face['box']
        test.append([image,bounding_box])
    test_df.append(test)
test=[]
for i in test_df:
    if len(i)>0:
        if len(i)==1:
            test.append(i[0])
        else:
            for j in i:
                test.append(j)  
sub=[]
rest_image=[]
for i in test:
    sub.append(i[0])
for image in test_images:
    if image not in sub:
        rest_image.append(image) 
detector=MTCNN()
test_df_=[]
for image in rest_image:
    img=cv2.imread(os.path.join(images,image))
    faces=detector.detect_faces(img)
    test_=[]
    for face in faces:
        bounding_box=face['box']
        test_.append([image,bounding_box])
    test_df_.append(test_) 
for i in test_df_:
    if len(i)>0:
        if len(i)==1:
            test.append(i[0])
        else:
            for j in i:
                test.append(j)

negative=[]
for i in test:
    for j in i[1]:
        if j<0:
            negative.append(i)

test_data=[]
def create_test_data():
            for j in test:
                if j not in negative:
                    img=cv2.imread(os.path.join(images,j[0]),cv2.IMREAD_GRAYSCALE)
                    img=img[j[1][1]:j[1][1]+j[1][3],j[1][0]:j[1][0]+j[1][2]]
                    new_img=cv2.resize(img,(50,50))
                    new_img=new_img.reshape(-1,50,50,1)
                    predict=model.predict(new_img)
                    test_data.append([j,predict])

create_test_data()

image=[]
classname=[]
for i,j in test_data:
    classname.append(np.argmax(j))
    image.append(i)
df=pd.DataFrame(columns=['image','classname'])
df['image']=image
df['classname']=classname
df['classname']=lbl.inverse_transform(df['classname'])
image=[]
x1=[]
x2=[]
y1=[]
y2=[]
for i in df['image']:
    image.append(i[0])
    x1.append(i[1][0])
    x2.append(i[1][1])
    y1.append(i[1][2])
    y2.append(i[1][3])
df['name']=image
df['x1']=x1
df['x2']=x2
df['y1']=y1
df['y2']=y2    
df.drop(['image'],axis=1,inplace=True)

df.sort_values('name',axis=0,inplace=True,ascending=False)
df.to_csv('/content/drive/MyDrive/ML Project/dataset/submission_1.csv')

def detect_mask(path):
  img=plt.imread(os.path.join(images,path))
  plt.imshow(img)
  face=detector.detect_faces(img)
  test=[]
  for k in face:
    bounding_box=k['box']
    test.append([img,bounding_box])
  for face in face:
          bounding_box=face['box']
          x=cv2.rectangle(img,
                (bounding_box[0], bounding_box[1]),
                (bounding_box[0]+bounding_box[2], bounding_box[1] + bounding_box[3]),
                (0,155,255),
                10)
          plt.imshow(x)
  img=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
  img=img[bounding_box[1]:bounding_box[1]+bounding_box[3],bounding_box[0]:bounding_box[0]+bounding_box[2]]
  new_img=cv2.resize(img,(50,50))
  new_img=new_img.reshape(-1,50,50,1)

  predict=model.predict(new_img)
  if(np.argmax(predict[0])==0):
    print("No Mask")
  elif(np.argmax(predict[0])==1):
    print("Mask Detected")

detect_mask("/niel.jpeg")

model.save("/content/drive/MyDrive/ML Project/model.h5")