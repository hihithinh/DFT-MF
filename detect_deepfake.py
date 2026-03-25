import cv2
import tensorflow as tf
import numpy as np

CATEGORIES = ["Real", "Fake"]

def prepare(filepath):
    IMG_SIZE = 50
    img_array = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    normalized = new_array / 255.0  # Normalize like training
    return normalized.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

# Load trained model
model = tf.keras.models.load_model("trained_models/CNN_CelebDF_20260325_144921_final.h5")

import matplotlib.pyplot as plt
import openpyxl
import glob
import sys
import os
from timeit import default_timer as timer
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMG_SIZE =500
sheetCount=1

# Get all video folders from CroppedMouth
cropped_mouth_dir = os.path.join(BASE_DIR, "CroppedMouth")
video_folders = sorted([d for d in os.listdir(cropped_mouth_dir) if os.path.isdir(os.path.join(cropped_mouth_dir, d))])

y=1
while(y <= len(video_folders)):
    start= timer()
    book = openpyxl.load_workbook(os.path.join(BASE_DIR, 'Result.xlsx'))
    sheet = book.active
    Result=" "
    CountReal=0
    CountFake=0         
    RealArry=[]
    
    video_name = video_folders[y-1]
    faces_folder_path = os.path.join(BASE_DIR, "CroppedMouth", video_name)
    numberImage=len(glob.glob(os.path.join(faces_folder_path, "*.jpg")))
    print("Total number of Images in RF "+str(int(y))+ "=  "+ str(int(numberImage))) 
    i=0
    while(i <=(numberImage-1)):
        datatest =(faces_folder_path+"/Real"+str(int(i))+".jpg")
        prediction = model.predict([prepare((datatest))], verbose=0)
        # Model outputs probability (0=Real, 1=Fake)
        pred_value = prediction[0][0]
        if pred_value < 0.5:  # Real
            str_label='RealVideo'
            RealArry.append(str(int(i)))
            CountReal+=1
        else:  # Fake
            str_label='FakeVideo'
            CountFake+=1
        
        
        plt.title(str_label)
    
        img_array = cv2.imread(datatest)
    
        new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
        plt.imshow(img_array, cmap='gray')
        plt.tight_layout()
        #plt.show()#------------------
        i+=1
    
    if (CountFake > 50  or (i/2)< CountFake)  :
        print ("Done!")
        print("This video is Fake  " )
        Result=" "+ "This video is Fake "
   
    else:
        print ("Done!")
        print("This video is Real " )
        Result=" "+ "This video is Real "
    
    print("The Number of Real Image = "+ " "+str(int(CountReal)))
    print("The Number of Fake Image = "+ " "+str(int(CountFake)))
    sheet['F'+str(int(sheetCount))] = ("Real Image "+video_name)
    sheet['G'+str(int(sheetCount))] = (str(int(CountReal)))
    sheet['H'+str(int(sheetCount))] = ("Fake Image "+video_name)
    sheet['I'+str(int(sheetCount))] = (str(int(CountFake)))
    
    sheet['J'+str(int(sheetCount))] = (Result)     
    end = timer()
    sheet['M'+str(sheetCount)] = (int(end-start)) 
    book.save(os.path.join(BASE_DIR, "Result.xlsx"))
    sheetCount+=1
    print("                                                    ")
    print("Time taken:" ,   int(end-start) ,         "  seconds")
    print("                                                    ")
    #print (RealArry)
    print("----------------------------------------------------")
    y+=1
