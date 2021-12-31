import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
import time

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

currentVolume = volume.GetMasterVolumeLevel()
volMin, volMax = volume.GetVolumeRange()[:2]
vol = 0
volBar = 400
volPer = 0
area = 0
blackColor = (23, 23, 23)
whiteColor = (235, 235, 235)
# primaryColor = (28, 28, 102) r g b - b g r
primaryColor = (255, 28, 28)
pTime = 0
senstivity = 125

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    lmList = []
    if results.multi_hand_landmarks:
        for handlandmark in results.multi_hand_landmarks:
            for id, lm in enumerate(handlandmark.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
            mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

    if lmList != []:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        # print(x1,y1,x2,y2)
        print(lmList[8])
        # print(lmList[8])

        cv2.circle(img, (x1, y1), 4, primaryColor, cv2.FILLED)
        cv2.circle(img, (x2, y2), 4, primaryColor, cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), primaryColor, 3)

        # A bar that shows system volume percentage

        length = hypot(x2 - x1, y2 - y1)

        vol = np.interp(length, [25, senstivity], [volMin, volMax])
        volBar = np.interp(length, [25, senstivity], [400, 150])
        volPer = np.interp(length, [25, senstivity], [0, 100])

        smoothness = 10
        volPer = smoothness * round(volPer / smoothness)
        print(volPer)

        # check if landmark 20 coords greater than landmark 17 coords
        if lmList[20][1] > lmList[17][1]:
            volume.SetMasterVolumeLevelScalar(volPer / 100, None)
            currentVolume = volume.GetMasterVolumeLevel()

    img = cv2.flip(img, 1)

    # drawing
    cv2.rectangle(img, (50, 150), (85, 400), blackColor, 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), whiteColor, cv2.FILLED)
    cv2.putText(
        img, f"{int(volPer)} %", (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, primaryColor, 3
    )
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(
        img,
        f"Vol Set: {int(cVol)}",
        (400, 50),
        cv2.FONT_HERSHEY_COMPLEX,
        1,
        primaryColor,
        3,
    )

    # Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(
        img, f"FPS: {int(fps)}", (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, primaryColor, 3
    )

    # Hand range 25 - 750
    # Volume range -63.5 - 0.0

    cv2.imshow("Gesture Volume Controller", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break