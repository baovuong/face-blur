import cv2 
import numpy as np 

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

    face_cascade = cv2.CascadeClassifier('data/haarcascades/haarcascade_frontalface_default.xml')
    img = cv2.imread('lenna.png')

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl1 = clahe.apply(gray)

    blur = cv2.GaussianBlur(cl1,(5,5),0)
    smooth = cv2.addWeighted(blur,1.5,cl1,-0.5,0)


    # Detect faces 
    faces = face_cascade.detectMultiScale(cl1, 1.2, 5)


    for (x, y, w, h) in faces:

        # pixelate faces 
        face = img[y:y+h, x:x+w]
        face = anonymize_face_pixelate(face, 8)
        img[y:y+h, x:x+w] = face
        #cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
    cv2.imshow('img', smooth)
    cv2.waitKey()


if __name__ == '__main__':
    main() 