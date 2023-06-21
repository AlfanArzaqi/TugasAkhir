import cv2
import mediapipe as mp
import numpy as np
import os
import datetime
import time 
import pandas as pd
from PIL import Image

def GetFileName():
        x = datetime.datetime.now()
        s = x.strftime('%Y-%m-%d-%H%M%S%f')
        return s
def CreateDir(path):
    ls = [];
    head_tail = os.path.split(path)
    ls.append(path)
    while len(head_tail[1])>0:
        head_tail = os.path.split(path)
        path = head_tail[0]
        ls.append(path)
        head_tail = os.path.split(path)   
    for i in range(len(ls)-2,-1,-1):
        print(ls[i])
        sf =ls[i]
        isExist = os.path.exists(sf)
        if not isExist:
            os.makedirs(sf)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

NoKamera = 0
timeStart = time.time() 
timeNow = time.time()  
frameRate = 10
counter = 0
maxCounter = 10
sNamaDirektori = GetFileName() 

sDirektoriData = "D:\\DATA\\SEMESTER 7\\PRATA\\Dataset\\"+sNamaDirektori 
CreateDir(sDirektoriData )

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue
  
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    h,w,_ = image.shape
    black_image = np.zeros((h, w, 3), dtype = "uint8")

    handlandmark = []
    listimage = []
    listimage_left = []
    listimage_right = []
    mergeimage = []
    handsType = []
    cropped = np.zeros((128,128,3), dtype="uint8")
    cropped_left = np.zeros((128,128,3), dtype="uint8")
    cropped_right = np.zeros((128,128,3), dtype="uint8")
    resized = Image.fromarray(cropped, 'RGB')
    resized_left = Image.fromarray(cropped_left, 'RGB')
    resized_right = Image.fromarray(cropped_right, 'RGB')

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      
    results_hand = hands.process(image)
    mergeImage = [2]     
    
    if results_hand.multi_hand_landmarks != None:
        print (len (results_hand.multi_hand_landmarks))
        for hand_landmarks in results.multi_hand_landmarks:
          hand_coor = np.zeros([21,3])
          for i in range(21):
               hand_coor[i,0]=hand_landmarks.landmark[i].x*w;
               hand_coor[i,1]=hand_landmarks.landmark[i].y*h;
               hand_coor[i,2]=hand_landmarks.landmark[i].z;
          
          handlandmark.append(hand_coor)
          
          minx_hand = min(hand_coor[:,0]) - 20
          miny_hand = min(hand_coor[:,1]) - 20
          
          maxx_hand = max(hand_coor[:,0]) + 20
          maxy_hand = max(hand_coor[:,1]) + 20
          
          mp_drawing.draw_landmarks(
                black_image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
            
          mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
          
          # cv2.rectangle (image, (int (minx_hand), int (miny_hand)), (int (maxx_hand), int (maxy_hand)), (0,0,0), 2)
          cv2.rectangle (black_image, (int (minx_hand), int (miny_hand)), (int (maxx_hand), int (maxy_hand)), (0,0,0), 2)
          
          if (int (minx_hand) < 0) :
              minx_hand = 0
          elif (int (miny_hand) < 0):
              miny_hand = 0
          elif (int (maxx_hand) < 0):
              maxx_hand = 0
          elif (int (maxy_hand) < 0):
              maxy_hand = 0
          
          cropped = black_image[int (miny_hand):int (maxy_hand), int (minx_hand):int (maxx_hand)]
          fliped = cv2.flip(cropped, 1)
          resized = cv2.resize(fliped,(128, 128))
          
          for hand_handedness in results.multi_handedness:
            handType = hand_handedness.classification[0].label
            handsType.append(handType)
            
        for handType in zip (handsType) :
            if handType == 'Right' :
                cv2.rectangle (image, (int (minx_hand), int (miny_hand)), (int (maxx_hand), int (maxy_hand)), (255,0,0), 2)
            elif handType == 'Left' :
                cv2.rectangle (image, (int (minx_hand), int (miny_hand)), (int (maxx_hand), int (maxy_hand)), (0,0,0), 2)
        
        mergeImage = np.hstack(mergeImage)
                
        timeNow = time.time()  
        if timeNow - timeStart > 1 / frameRate :
            if len (handlandmark) == 2 :
                counter = counter + 1
                jumlahTangan = len(handlandmark)
                sfc =sDirektoriData+"\\"+ "testing" +str(counter)
                nd =np.array([jumlahTangan])
                # np.savetxt(sfc+".num", nd, delimiter=',')
                timeStart = timeNow
                filename=sfc+".png"
                cv2.imwrite(sfc + ".png", mergeImage)
            # for i in range (jumlahTangan):
            #     sf = sfc+"_"+str(i)
            #     np.savetxt(sf+".txt", handlandmark[i], delimiter=',')
            
      
    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
    cv2.imshow('MediaPipe', cv2.flip(black_image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()