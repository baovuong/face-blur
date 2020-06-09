import cv2 
import numpy as np 

img = cv2.imread('Lenna_(test_image).png')

px = img[100, 100]
print(px)

blue = img[100, 100, 0]
print(blue)