import cv2
import math
import os
import glob
from openpyxl import Workbook
from timeit import default_timer as timer
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset", "Celeb-DF")

# Get all video files
youtube_real_videos = sorted(glob.glob(os.path.join(DATASET_DIR, "YouTube-real", "*.mp4")))
celeb_real_videos = sorted(glob.glob(os.path.join(DATASET_DIR, "Celeb-real", "*.mp4")))
celeb_synthesis_videos = sorted(glob.glob(os.path.join(DATASET_DIR, "Celeb-synthesis", "*.mp4")))

# Combine all videos
all_videos = youtube_real_videos + celeb_real_videos + celeb_synthesis_videos

book = Workbook()
sheet = book.active
sheetCount=1
M=0
i=1
while(i <= len(all_videos)):
    start= timer()              
    videoFile = all_videos[i-1]
    video_name = os.path.splitext(os.path.basename(videoFile))[0]
    os.makedirs(os.path.join(BASE_DIR, "ExtractFrams", video_name), exist_ok=True)
    imagesFolder = os.path.join(BASE_DIR, "ExtractFrams", video_name)
    cap = cv2.VideoCapture(videoFile)
    frameRate = cap.get(5) #frame rate
    while(cap.isOpened()):
        frameId = cap.get(1) #current frame number
        #print(frameId)
        ret, frame = cap.read()
        if (ret != True):
            break
        if (frameId % 1 == 0):
            filename = imagesFolder + "/image_" +  str(int(frameId)) + ".jpg"
            cv2.imwrite(filename, frame)
        M=frameId    
    cap.release()
    end = timer()
    print ("Done!")
    print("Total Number of Frames for "+video_name+"=  "+ str(int(M+1)))
    print("Time taken:" ,   int(end-start) ,         "  seconds")
    print("----------------------------------------------------")
    sheet['A'+str(int(sheetCount))] = ("All Frames "+video_name)
    sheet['B'+str(int(sheetCount))] = (str(int(M+1)))
    sheet['K'+str(sheetCount)] = (int(end-start)) 
    book.save(os.path.join(BASE_DIR, "Result.xlsx"))
    i+=1
    sheetCount+=1
