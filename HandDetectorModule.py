import math

import cv2
import mediapipe as mp
import numpy as np
import time

class HandDetectorModule:
    def __init__(self):
        self.mpHands = mp.solutions.hands 
        self.hands = self.mpHands.Hands()
        self.mpDraw =  mp.solutions.drawing_utils
        self.results = None
        self.lmList = []
        self.tipIds = [4, 8, 12, 16, 20]
    
    def process(self, img):
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)
        self.results = results
    
    def get_landmarks(self, img):
        lmList = []
        if self.results.multi_hand_landmarks:
            for handlandmark in self.results.multi_hand_landmarks:
                for id,lm in enumerate(handlandmark.landmark):
                    h,w,_ = img.shape
                    cx,cy = int(lm.x*w),int(lm.y*h)
                    lmList.append([id,cx,cy]) 
                self.mpDraw.draw_landmarks(img,handlandmark,self.mpHands.HAND_CONNECTIONS)
        self.lmList = lmList
        return lmList
    
    def get_hand_center(self, img):
        if self.results.multi_hand_landmarks:
            for handlandmark in self.results.multi_hand_landmarks:
                h,w,_ = img.shape
                cx,cy = int(handlandmark.hand_center.x*w),int(handlandmark.hand_center.y*h)
                return cx,cy
        return "No hand detected"
    
    # A function that detect which finger is extended and return its id
    def get_extended_finger(self, img):
        pass

    # def is_thumb_extended(self, img):
    #     if self.results.multi_hand_landmarks:
    #         for handlandmark in self.results.multi_hand_landmarks:
    #             if handlandmark.landmark[4].y > handlandmark.landmark[2].y or handlandmark.landmark[4].x > handlandmark.landmark[2].x:
    #                 return False
    #     return True

    def is_thumb_up(self):
        if self.results.multi_hand_landmarks:
            for handlandmark in self.results.multi_hand_landmarks:
                if handlandmark.landmark[3].x < handlandmark.landmark[2].x or handlandmark.landmark[4].y > handlandmark.landmark[2].y:
                    return False
        return True

    def is_thumb_down(self):
        if self.results.multi_hand_landmarks:
            for handlandmark in self.results.multi_hand_landmarks:
                if handlandmark.landmark[3].x < handlandmark.landmark[2].x or handlandmark.landmark[4].y > handlandmark.landmark[2].y:
                    return True
        return False
    
    def fingersUp(self):
        fingers = []
        for i in range(1, 5):
            if self.lmList[self.tipIds[i]][2] > self.lmList[self.tipIds[i] - 2][2]:
                fingers.append(False)
            else:
                fingers.append(True)
        return fingers