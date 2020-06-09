import cv2 
import numpy as np 
from functools import reduce 

def sharpen(img):

    blurred = cv2.GaussianBlur(img, (0,0), 3)
    cv2.addWeighted(img, 1.5, blurred, -0.5, 0, blurred)
    return blurred 

def detect_faces(img, classifier_file):
    face_cascade = cv2.CascadeClassifier(classifier_file)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    sharpened = sharpen(gray)

    return face_cascade.detectMultiScale(sharpened, 1.2, 5)

def anonymize_face_pixelate(image, blocks=3):
    # divide the input image into NxN blocks
    (h, w) = image.shape[:2]
    xSteps = np.linspace(0, w, blocks + 1, dtype="int")
    ySteps = np.linspace(0, h, blocks + 1, dtype="int")
    # loop over the blocks in both the x and y direction
    for i in range(1, len(ySteps)):
        for j in range(1, len(xSteps)):
            # compute the starting and ending (x, y)-coordinates
            # for the current block
            startX = xSteps[j - 1]
            startY = ySteps[i - 1]
            endX = xSteps[j]
            endY = ySteps[i]
            # extract the ROI using NumPy array slicing, compute the
            # mean of the ROI, and then draw a rectangle with the
            # mean RGB values over the ROI in the original image
            roi = image[startY:endY, startX:endX]
            (B, G, R) = [int(x) for x in cv2.mean(roi)[:3]]
            cv2.rectangle(image, (startX, startY), (endX, endY),
                (B, G, R), -1)
    # return the pixelated blurred image
    return image



def main():
    img = cv2.imread('tmp_data/splash_evelopegate.jpg')

    # Detect faces 

    cascades = [
        'data/haarcascades/haarcascade_profileface.xml',
        'data/haarcascades/haarcascade_frontalface_default.xml',
    ]

    faces = np.array([detect_faces(img, c) for c in cascades])
    flattened = np.concatenate(faces)

    for (x, y, w, h) in flattened:

        # pixelate faces 
        face = img[y:y+h, x:x+w]
        face = anonymize_face_pixelate(face, 8)
        img[y:y+h, x:x+w] = face
        #cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
    cv2.imshow('img', img)
    cv2.waitKey()


if __name__ == '__main__':
    main() 