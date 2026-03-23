from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import sys
import os
import glob
import openpyxl
from timeit import default_timer as timer
import time
import face_recognition
import cv2
from datetime import datetime
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
book = openpyxl.load_workbook(os.path.join(BASE_DIR, 'Result.xlsx'))
sheet = book.active
sheetCount=1
predictor_path = os.path.join(BASE_DIR, "shape_predictor_68_face_landmarks.dat")

def get_lip_height(lip):
    """Calculate average height of lip"""
    sum=0
    for i in [2,3,4]:
        # distance between two near points up and down
        distance = math.sqrt( (lip[i][0] - lip[12-i][0])**2 +
                              (lip[i][1] - lip[12-i][1])**2   )
        sum += distance
    return sum / 3

def get_mouth_height(top_lip, bottom_lip):
    sum=0
    for i in [8,9,10]:
        # distance between two near points up and down
        distance = math.sqrt( (top_lip[i][0] - bottom_lip[18-i][0])**2 + 
                              (top_lip[i][1] - bottom_lip[18-i][1])**2   )
        sum += distance
    return sum / 3

def is_mouth_open(face_landmarks):
    top_lip = face_landmarks['top_lip']
    bottom_lip = face_landmarks['bottom_lip']

    top_lip_height = get_lip_height(top_lip)
    bottom_lip_height = get_lip_height(bottom_lip)
    mouth_height = get_mouth_height(top_lip, bottom_lip)
    
    # if mouth is open more than lip height * ratio, return true.
    ratio = 0.4
    # Debug: uncomment to see detailed mouth metrics
    # print('Mouth metrics - Top: %.2f, Bottom: %.2f, Height: %.2f, Threshold: %.2f' 
    #       % (top_lip_height, bottom_lip_height, mouth_height, min(top_lip_height, bottom_lip_height) * ratio))
    if mouth_height > min(top_lip_height, bottom_lip_height) * ratio:
        return True
    else:
        return False

def Crooped_mouth(frame):
    # Ask the detector to find the bounding boxes of each face. The 1 in the
    # second argument indicates that we should upsample the image 1 time. This
    # will make everything bigger and allow us to detect more faces.
        dets = detector(frame, 1)
        #print("Number of faces detected: {}".format(len(dets)))#----------------------
        for k, d in enumerate(dets):
            #print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
            #k, d.left(), d.top(), d.right(), d.bottom()))#-------------------------
        # Get the landmarks/parts for the face in box d.
            shape = predictor(frame, d)     
        # The next lines of code just get the coordinates for the mouth
        # and crop the mouth from the image.This part can probably be optimised
        # by taking only the outer most points.
            xmouthpoints = [shape.part(x).x for x in range(48,67)]
            ymouthpoints = [shape.part(x).y for x in range(48,67)]
            maxx = max(xmouthpoints)
            minx = min(xmouthpoints)
            maxy = max(ymouthpoints)
            miny = min(ymouthpoints) 
        # to show the mouth properly pad both sides
            pad = 10
        # basename gets the name of the file with it's extension
        # splitext splits the extension and the filename
        # This does not consider the condition when there are multiple faces in each image.
        # if there are then it just overwrites each image and show only the last image.       
        #filename = os.path.splitext(os.path.basename(f))[0]

            mouth =frame[miny-pad:maxy+pad,minx-pad:maxx+pad]
            crop_image = frame[miny-pad:maxy+pad,minx-pad:maxx+pad]
            Final_image = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)
            return Final_image

# Get all video folders from ExtractFrams
extract_frams_dir = os.path.join(BASE_DIR, "ExtractFrams")
video_folders = sorted([d for d in os.listdir(extract_frams_dir) if os.path.isdir(os.path.join(extract_frams_dir, d))])

print(f"Found {len(video_folders)} video folders to process")
print("=" * 60)

i=1
while(i <= len(video_folders)):
    start= timer()
    video_name = video_folders[i-1]
    faces_folder_path = os.path.join(BASE_DIR, "ExtractFrams", video_name)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)
    os.makedirs(os.path.join(BASE_DIR, "CroppedMouth", video_name), exist_ok=True)
    imagesFolder = os.path.join(BASE_DIR, "CroppedMouth", video_name)

    print(f"[{i}/{len(video_folders)}] Processing video: {video_name}")
    
    # Count total frames
    total_frames = len(glob.glob(os.path.join(faces_folder_path, "*.jpg")))
    print(f"  Found {total_frames} frames to analyze")
    
    M = 0
    processed_frames = 0
    for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
        processed_frames += 1
        
        # Load a sample picture and learn how to recognize it.
        peter_image = face_recognition.load_image_file(f) # replace peter.jpg with you're own image !!
        # Grab a single frame of video
        frame = peter_image
        # Find all the faces and face enqcodings in the frame of video
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame,face_locations)
        face_landmarks_list = face_recognition.face_landmarks(frame)
        
        # Show progress every 25 frames
        if processed_frames % 25 == 0:
            progress = (processed_frames / total_frames) * 100
            print(f"  Progress: {processed_frames}/{total_frames} ({progress:.1f}%) - Open mouth frames: {M}")
        
        # Check if faces found
        if len(face_locations) == 0:
            continue
            
        # Loop through each face in this frame of video
        for (top, right, bottom, left), face_encoding, face_landmarks in zip(face_locations, face_encodings, face_landmarks_list):
            # Display text for mouth open / close
            ret_mouth_open = is_mouth_open(face_landmarks)
            if ret_mouth_open is True:
                # Draw a box around the face
                text = 'Mouth is open'
                cv2.putText(frame, text, (left-50, top - 50), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)
                #cv2.imshow('Frame', frame)
                cropped = Crooped_mouth(frame)
                filename =os.path.splitext(imagesFolder+"/Real")[0]#str(int(i))
                cv2.imwrite(filename+str(int(M))+'.jpg',cropped)
                #time.sleep()
                M+=1
                
                # Log every 10th open mouth frame to show activity
                if M % 10 == 0:
                    print(f"    Found open mouth frame #{M}")
                
            else:
                text = 'Mouth is close'
                cv2.putText(frame, text, (left-50, top - 50), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255,0, 0), 1)
                continue
    end = timer()        
    print(f"  Completed! Found {M} open mouth frames out of {processed_frames} total frames")
    print(f"  Success rate: {(M/processed_frames*100):.1f}%")
    print(f"  Time taken: {int(end-start)} seconds")
    print(f"  Processing speed: {processed_frames/(end-start):.1f} frames/second")
    
    # Update Excel sheet
    sheet['C'+str(int(sheetCount))] = ("Open mouth frames "+video_name)
    sheet['D'+str(int(sheetCount))] = (str(int(M)))
    sheet['L'+str(int(sheetCount))] = (int(end-start)) 
    book.save(os.path.join(BASE_DIR, "Result.xlsx"))
    print("-" * 60)
    sheetCount+=1
    i += 1

print("=" * 60)
print("All videos processed successfully!")
print(f"Results saved to: {os.path.join(BASE_DIR, 'Result.xlsx')}")
print(f"Cropped mouth images saved to: {os.path.join(BASE_DIR, 'CroppedMouth')}")
print("=" * 60)
