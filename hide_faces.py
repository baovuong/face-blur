import cv2 
import numpy as np 
import sys 
import argparse 


def area(w, h):
    return w * h

def perimeter(w, h):
    return 2 * (w + h)

def weight(box):
    return area(box[2], box[3]) + perimeter(box[2], box[3])

def encompassed_box(box1, box2):
    
    # (x, y, w, h)
    x = [box1[0], box1[0] + box1[2], box2[0], box2[0] + box2[2]]
    y = [box1[1], box1[1] + box1[3], box2[1], box2[1] + box2[3]]

    p1 = (min(x), min(y))
    p2 = (max(x), max(y))

    return (p1[0], p1[1], abs(p1[0] - p2[0]), abs(p1[1] - p2[1]))

def in_proximity(box1, box2):

    # (x, y, w, h)
    encompassed = encompassed_box(box1, box2)
    en_weight = weight(encompassed) * 0.7
    return en_weight <= weight(box1) or en_weight <= weight(box2)

def sharpen(img):

    blurred = cv2.GaussianBlur(img, (0,0), 3)
    cv2.addWeighted(img, 1.5, blurred, -0.5, 0, blurred)
    return blurred 

def detect_faces(img, classifier_file):
    face_cascade = cv2.CascadeClassifier(classifier_file)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sharpened = sharpen(gray)

    return face_cascade.detectMultiScale(sharpened, 1.22, 2)

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

def pixelate(img, p1, p2, blocks=3):
    face = img[p1[1]:p2[1], p1[0]:p2[0]]
    face = anonymize_face_pixelate(face, blocks)
    img[p1[1]:p2[1], p1[0]:p2[0]] = face


def hide_faces(input_filename, output_filename, cascades):
    img = cv2.imread(input_filename)
    
    # Detect faces 
    faces = np.array([detect_faces(img, c) for c in cascades])
    flattened = np.concatenate([f for f in faces if len(f) > 0])

    # clean up
    cleaned = set()
    for f in flattened:
        prox = sorted([g for g in flattened if in_proximity(f, g)], key=lambda x: weight(x))
        if len(prox) > 0:
            cleaned.add(tuple(prox[0]))

    print('%s faces found.' % len(cleaned))

    for (x, y, w, h) in cleaned:
        pixelate(img, (x, y), (x+w, y+h), 8)
    
    cv2.imwrite(output_filename, img)

def main():

    cascades = [
        'data/haarcascades/haarcascade_profileface.xml',
        'data/haarcascades/haarcascade_frontalface_default.xml',
        'data/lbpcascades/lbpcascade_frontalface_improved.xml'
    ]

    parser = argparse.ArgumentParser(description='hide some face')
    parser.add_argument('input', help='input filename')
    parser.add_argument('output', help='output filename')
    args = parser.parse_args()
    hide_faces(args.input, args.output, cascades)

if __name__ == '__main__':
    main() 