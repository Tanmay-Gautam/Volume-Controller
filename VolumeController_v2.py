import cv2 
import mediapipe as mp
from math import hypot, ceil
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np 
import time
from HandDetectorModule import HandDetectorModule
from splashScreen import splashScreen
from tkinter import *

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands 
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
detector = HandDetectorModule()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

currentVolume = volume.GetMasterVolumeLevel()
volMin,volMax = volume.GetVolumeRange()[:2]
vol = 0
volBar = 400
volPer = 0
area = 0
blackColor = (23, 23, 23)
whiteColor = (235, 235, 235)
# primaryColor = (28, 28, 102) r g b - b g r
primaryColor = (255, 28, 28)
pTime = 0
senstivity = 150
detector = HandDetectorModule()

splashScreen()

while True:
    is_volume_changing = False
    success,img = cap.read()

    detector.process(img)
    lmList = detector.get_landmarks(img)
    
    if lmList != []:
        # getting the coordinates of index finger tip and the thumb tip
        x1,y1 = lmList[4][1],lmList[4][2]
        x2,y2 = lmList[8][1],lmList[8][2]

        # drawing the circles and lines on the image
        cv2.circle(img,(x1,y1),4,primaryColor,cv2.FILLED)
        cv2.circle(img,(x2,y2),4,primaryColor,cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),primaryColor,3)

        length = hypot(x2-x1,y2-y1) # getting the length of the line

        # calculating the Volume and the percentage of the volume
        vol = np.interp(length,[25,senstivity],[volMin,volMax])
        volBar = np.interp(length,[25,senstivity],[400,150])
        volPer = np.interp(length,[25,senstivity],[0,100])

        # adding the smoothness so volume changes are not abrupt and changes are gradual (changes from 10 to 20 to 30 and so on... at last 100%)
        smoothness = 10
        volPer = smoothness * round(volPer/smoothness)

        # detect for thumb up, on thumb up start the if statement for changing the volume and on thumb down stop the if statement for changing the volume
        is_thumb_up = detector.is_thumb_up()
        if is_thumb_up:
            # if pinky finger is down, run the if statement for changing the volume.
            # if thumb down is detected, stop the if statement for changing the volume and break the loop

            is_pinky_down = detector.fingersUp()[3]
            is_thumb_down = detector.is_thumb_down()

            if not is_pinky_down:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                is_volume_changing = True
                if is_thumb_down:
                    break

    img = cv2.flip(img,1)

    # drawing
    cv2.rectangle(img, (50, 150), (85, 400), blackColor, 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), whiteColor, cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, primaryColor, 3)
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    if cVol % 10 == 9:
        cVol += 1
    cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, primaryColor, 3)

    # put a text on the image to show is the volume is changing or not
    if is_volume_changing:
        cv2.putText(img, 'Volume Changing', (40, 100), cv2.FONT_HERSHEY_COMPLEX,
                    1, (0, 255, 0), 3)
    else:
        cv2.putText(img, 'Volume Not Changing', (40, 100), cv2.FONT_HERSHEY_COMPLEX,
                    1, (0, 0, 255), 3)

    # Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, primaryColor, 3)
        
    cv2.imshow('AI Volume Controller',img)
    if cv2.waitKey(1) & 0xff==ord('q'):
        break