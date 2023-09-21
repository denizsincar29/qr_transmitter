from base64 import b64decode
from time import sleep, time
import cv2
# import chunker

cap = cv2.VideoCapture("chun/video.mp4")  # just for debugging. after success we'll make webcam.
detector = cv2.QRCodeDetector()
c=0
a=''
while c!=32:
    _, img = cap.read()
    data, bbox, _ = detector.detectAndDecode(img)
    data=b64decode(data)
    if a!=data:
        print(data)
        a=data
    #cv2.imshow("QR file receiver", img)
    #c=cv2.waitKey(1)
    # if c>-1: print(c)

cap.release()
cv2.destroyAllWindows()